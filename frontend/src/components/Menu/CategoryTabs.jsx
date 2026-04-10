import React, { useState, useEffect } from 'react';
import CategoryService from '../../services/category.service';

const CategoryTabs = ({ selectedCategory, onCategoryChange }) => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadCategories(); }, []);

  const loadCategories = async () => {
    try {
      const data = await CategoryService.getAllCategories();
      setCategories([{ id: null, name: 'All' }, ...data]);
    } catch (error) {
      console.error('Failed to load categories:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="h-8 w-full animate-pulse bg-gray-100 rounded mb-4"></div>;

  return (
    <div className="flex overflow-x-auto pb-2 sm:flex-wrap gap-2 mb-4 no-scrollbar">
      {categories.map((category) => (
        <button
          key={category.id || 'all'}
          onClick={() => onCategoryChange(category.id)}
          className={`px-4 py-1.5 rounded-md font-bold text-xs sm:text-sm transition-all duration-200 whitespace-nowrap
            ${(selectedCategory === category.id) 
              ? 'bg-primary-500 text-white shadow-sm' 
              : 'bg-[#3A707A] text-white opacity-90 hover:opacity-100'
            }`}
        >
          {category.name}
        </button>
      ))}
    </div>
  );
};

export default CategoryTabs;