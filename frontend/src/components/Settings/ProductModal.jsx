import React, { useState } from 'react';
import { MdClose, MdSave } from 'react-icons/md';
import ProductService from '../../services/product.service';
import toast from 'react-hot-toast';
import { notifySuccess, notifyError } from '../../utils/notificationHelper';

const ProductModal = ({ product, categories, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: product?.name || '',
    price: product?.price || '',
    category_id: product?.category_id || '',
    description: product?.description || '',
    image_url: product?.image_url || '',
    is_available: product?.is_available ?? true
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!formData.name || !formData.price || !formData.category_id) {
      toast.error('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      if (product) {
        await ProductService.updateProduct(product.id, formData);
        notifySuccess('Product Updated', `${formData.name} has been updated`);
        toast.success('Product updated successfully');
      } else {
        await ProductService.createProduct(formData);
        notifySuccess('Product Created', `${formData.name} has been added to menu`);
        toast.success('Product created successfully');
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
      <div className="bg-white rounded-2xl w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{product ? 'Edit Product' : 'Add Product'}</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg">
            <MdClose size={20} />
          </button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Product Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
              placeholder="Enter product name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Category *</label>
            <select
              value={formData.category_id}
              onChange={(e) => setFormData({ ...formData, category_id: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
            >
              <option value="">Select Category</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Price *</label>
            <input
              type="number"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
              placeholder="Enter price"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
              rows="3"
              placeholder="Enter description"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Image URL</label>
            <input
              type="text"
              value={formData.image_url}
              onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
              placeholder="Enter image URL"
            />
          </div>
          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.is_available}
                onChange={(e) => setFormData({ ...formData, is_available: e.target.checked })}
                className="w-4 h-4"
              />
              <span className="text-sm font-medium">Available</span>
            </label>
          </div>
        </div>
        <div className="flex gap-3 mt-6">
          <button onClick={handleSubmit} disabled={loading} className="flex-1 py-2 bg-[#3A707A] text-white rounded-lg font-medium disabled:opacity-50">
            <MdSave size={16} className="inline mr-1" /> {loading ? 'Saving...' : (product ? 'Update' : 'Create')}
          </button>
          <button onClick={onClose} className="flex-1 py-2 bg-gray-200 rounded-lg font-medium">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductModal;