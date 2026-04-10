import React, { useState } from 'react';
import { MdPeople, MdRecommend, MdCategory, MdRestaurantMenu, MdCloudUpload } from 'react-icons/md';
import UsersTab from '../components/Settings/UsersTab';
import CategoriesTab from '../components/Settings/CategoriesTab';
import ProductsTab from '../components/Settings/ProductsTab';
import RecommendationsTab from '../components/Settings/RecommendationsTab';
import SeedDataModal from '../components/Settings/SeedDataModal';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('users');
  const [showSeedModal, setShowSeedModal] = useState(false);

  const tabs = [
    { id: 'users', label: 'Users', icon: MdPeople },
    { id: 'categories', label: 'Categories', icon: MdCategory },
    { id: 'products', label: 'Products', icon: MdRestaurantMenu },
    { id: 'recommendations', label: 'Recommendations', icon: MdRecommend },
  ];

  return (
    <div className="min-h-screen bg-[#F8FAFB] p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
                <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-black text-[#3A707A] tracking-tighter uppercase">Settings</h1>
            <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">Manage Users, Categories & Products</p>
          </div>
          <button
            onClick={() => setShowSeedModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-bold hover:bg-green-700 transition-colors"
          >
            <MdCloudUpload size={18} />
            Seed Menu Data
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-3 mb-6 overflow-x-auto no-scrollbar pb-2">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-5 py-2 rounded-lg font-bold text-sm flex items-center gap-2 transition-all whitespace-nowrap ${
                activeTab === tab.id 
                  ? 'bg-[#3A707A] text-white' 
                  : 'bg-white text-gray-500 hover:bg-gray-100'
              }`}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'users' && <UsersTab />}
        {activeTab === 'categories' && <CategoriesTab />}
        {activeTab === 'products' && <ProductsTab />}
        {activeTab === 'recommendations' && <RecommendationsTab />}
      </div>
        {showSeedModal && (
        <SeedDataModal onClose={() => setShowSeedModal(false)} />
      )}
    </div>
  );
};

export default Settings;