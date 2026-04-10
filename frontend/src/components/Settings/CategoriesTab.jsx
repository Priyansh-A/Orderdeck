import React, { useState, useEffect } from 'react';
import { MdAdd, MdEdit, MdDelete, MdCategory } from 'react-icons/md';
import CategoryService from '../../services/category.service';
import CategoryModal from './CategoryModal';
import toast from 'react-hot-toast';
import { notifySuccess, notifyError } from '../../utils/notificationHelper';

const CategoriesTab = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    setLoading(true);
    try {
      const data = await CategoryService.getAllCategories();
      setCategories(data);
    } catch (error) {
      toast.error('Failed to load categories');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (category) => {
    if (!window.confirm(`Delete category ${category.name}?`)) return;
    try {
      await CategoryService.deleteCategory(category.id);
      notifySuccess('Category Deleted', `Category ${category.name} has been deleted`);
      toast.success('Category deleted');
      loadCategories();
    } catch (error) {
      notifyError(error.response?.data?.detail || 'Failed to delete category');
      toast.error('Failed to delete category');
    }
  };

  const openModal = (category = null) => {
    setEditingCategory(category);
    setShowModal(true);
  };

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-[#3A707A] border-t-transparent"></div>
      </div>
    );
  }

  return (
    <>
      <div className="mb-6 flex justify-end">
        <button
          onClick={() => openModal()}
          className="flex items-center gap-2 px-4 py-2 bg-[#3A707A] text-white rounded-lg text-sm font-bold hover:bg-[#2E5A63] transition-colors"
        >
          <MdAdd size={18} />
          Add Category
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-50">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#E9EDF2]">
              <tr className="text-[#6C757D] text-[11px] uppercase font-bold tracking-widest">
                <th className="py-4 px-6 text-left">Name</th>
                <th className="py-4 px-6 text-left">Created</th>
                <th className="py-4 px-6 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {categories.map((category) => (
                <tr key={category.id} className="hover:bg-gray-50 transition-colors">
                  <td className="py-4 px-6">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                        <MdCategory className="text-green-600" size={16} />
                      </div>
                      <span className="font-medium text-gray-800">{category.name}</span>
                    </div>
                  </td>
                  <td className="py-4 px-6 text-gray-500 text-sm">
                    {new Date(category.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-4 px-6 text-center">
                    <div className="flex justify-center gap-2">
                      <button onClick={() => openModal(category)} className="p-1.5 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors">
                        <MdEdit size={18} />
                      </button>
                      <button onClick={() => handleDelete(category)} className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                        <MdDelete size={18} />
                      </button>
                    </div>
                   </td>
                 </tr>
              ))}
            </tbody>
           </table>
        </div>
      </div>

      {showModal && (
        <CategoryModal
          category={editingCategory}
          onClose={() => {
            setShowModal(false);
            setEditingCategory(null);
          }}
          onSuccess={loadCategories}
        />
      )}
    </>
  );
};

export default CategoriesTab;