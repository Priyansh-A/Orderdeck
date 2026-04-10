import React, { useState } from 'react';
import { MdClose, MdSave } from 'react-icons/md';
import CategoryService from '../../services/category.service';
import toast from 'react-hot-toast';
import { notifySuccess, notifyError } from '../../utils/notificationHelper';

const CategoryModal = ({ category, onClose, onSuccess }) => {
  const [name, setName] = useState(category?.name || '');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!name.trim()) {
      toast.error('Category name is required');
      return;
    }

    setLoading(true);
    try {
      if (category) {
        await CategoryService.updateCategory(category.id, { name });
        notifySuccess('Category Updated', `Category ${name} has been updated`);
        toast.success('Category updated successfully');
      } else {
        await CategoryService.createCategory({ name });
        notifySuccess('Category Created', `Category ${name} has been created`);
        toast.success('Category created successfully');
      }
      onSuccess();
      onClose();
    } catch (error) {
      notifyError(error.response?.data?.detail || 'Operation failed');
      toast.error('Operation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{category ? 'Edit Category' : 'Add Category'}</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg">
            <MdClose size={20} />
          </button>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Category Name *</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
            placeholder="Enter category name"
          />
        </div>
        <div className="flex gap-3 mt-6">
          <button onClick={handleSubmit} disabled={loading} className="flex-1 py-2 bg-[#3A707A] text-white rounded-lg font-medium disabled:opacity-50">
            <MdSave size={16} className="inline mr-1" /> {loading ? 'Saving...' : (category ? 'Update' : 'Create')}
          </button>
          <button onClick={onClose} className="flex-1 py-2 bg-gray-200 rounded-lg font-medium">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default CategoryModal;