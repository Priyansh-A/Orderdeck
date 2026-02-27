import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import categoryService from '../services/category.service';

const Home = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setIsLoading(true);
        const data = await categoryService.getAllCategories();
        setCategories(data);
        setError(null);
      } catch (err) {
        setError('Failed to load categories');
        console.error('Error fetching categories:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCategories();
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) {
    navigate('/login');
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-semibold text-gray-800">Restaurant Dashboard</h1>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-700">{user.username}</p>
                <p className="text-xs text-gray-500">
                  Role: <span className="capitalize">{user.role}</span>
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm bg-red-500 hover:bg-red-600 text-white rounded-lg transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Welcome, {user.username}! 👋
          </h2>
          <p className="text-gray-600">
            You are logged in as <span className="font-semibold capitalize">{user.role}</span>
          </p>
        </div>

        {/* Categories Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Categories</h3>
            <span className="px-3 py-1 bg-blue-100 text-blue-600 rounded-full text-sm">
              {categories.length} total
            </span>
          </div>

          {isLoading ? (
            <div className="flex justify-center items-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <div className="text-red-500 mb-2">⚠️ {error}</div>
              <button
                onClick={() => window.location.reload()}
                className="text-blue-600 hover:text-blue-800"
              >
                Try again
              </button>
            </div>
          ) : categories.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {categories.map((category) => (
                <div
                  key={category.id}
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:shadow-md transition"
                >
                  <h4 className="font-medium text-gray-800">{category.name}</h4>
                  <div className="flex justify-between items-center mt-2">
                    <p className="text-xs text-gray-500">ID: {category.id}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(category.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No categories</h3>
              <p className="mt-1 text-sm text-gray-500">Get started by creating a new category.</p>
            </div>
          )}
        </div>

        {/* Role-based info */}
        {user.role === 'manager' && (
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-700">
              🔑 You have manager privileges. You can manage staff, view reports, and access all features.
            </p>
          </div>
        )}
      </main>
    </div>
  );
};

export default Home;