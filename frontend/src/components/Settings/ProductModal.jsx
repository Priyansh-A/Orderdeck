import React, { useState, useRef, useEffect } from 'react';
import { MdClose, MdSave, MdUpload, MdDelete } from 'react-icons/md';
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
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (product?.image_url) {
      if (product.image_url.startsWith('assets/')) {
        setImagePreview(`http://localhost:8000/${product.image_url}`);
      } else {
        setImagePreview(product.image_url);
      }
    }
  }, [product]);

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        toast.error('Please select a valid image (JPEG, PNG, GIF, or WEBP)');
        return;
      }
      
      if (file.size > 5 * 1024 * 1024) {
        toast.error('Image size should be less than 5MB');
        return;
      }
      
      setImageFile(file);
      const previewUrl = URL.createObjectURL(file);
      setImagePreview(previewUrl);
      
      setFormData({ ...formData, image_url: '' });
    }
  };

  const handleRemoveImage = () => {
    setImageFile(null);
    setImagePreview('');
    setFormData({ ...formData, image_url: '' });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async () => {
    if (!formData.name || !formData.price || !formData.category_id) {
      toast.error('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      const submitData = {
        name: formData.name,
        price: parseFloat(formData.price),
        category_id: parseInt(formData.category_id),
        description: formData.description,
        is_available: formData.is_available,
      };

      if (imageFile) {
        submitData.image = imageFile;
      } 
      else if (formData.image_url) {
        submitData.image_url = formData.image_url;
      }

      if (product) {
        await ProductService.updateProduct(product.id, submitData);
        notifySuccess('Product Updated', `${formData.name} has been updated`);
      } else {
        await ProductService.createProduct(submitData);
        notifySuccess('Product Created', `${formData.name} has been added to menu`);
      }
      
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error saving product:', error);
      notifyError(error.response?.data?.detail || 'Operation failed');
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
          {/* Image Upload Section */}
          <div>
            <label className="block text-sm font-medium mb-1">Product Image</label>
            <div className="space-y-3">
              {imagePreview && (
                <div className="relative w-full h-40 rounded-lg overflow-hidden bg-gray-100 border">
                  <img 
                    src={imagePreview} 
                    alt="Product preview" 
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/400x300?text=No+Image';
                    }}
                  />
                  <button
                    onClick={handleRemoveImage}
                    className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                    type="button"
                  >
                    <MdDelete size={16} />
                  </button>
                </div>
              )}
              
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-[#3A707A] hover:text-[#3A707A] transition-colors flex items-center justify-center gap-2"
              >
                <MdUpload size={20} />
                {imagePreview ? 'Change Image' : 'Upload Image'}
              </button>
              
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/gif,image/webp"
                onChange={handleImageSelect}
                className="hidden"
              />
              
              {/* Optional: Image URL input as fallback */}
              {!imageFile && (
                <div className="mt-2">
                  <label className="block text-xs text-gray-500 mb-1">Or enter image URL</label>
                  <input
                    type="text"
                    value={formData.image_url}
                    onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                    className="w-full px-3 py-1 text-sm border rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
                    placeholder="https://example.com/image.jpg"
                  />
                </div>
              )}
              
              <p className="text-xs text-gray-500">
                Supported formats: JPEG,JPG, PNG, GIF, WEBP (Max 5MB)
              </p>
            </div>
          </div>

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
              step="0.01"
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
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_available}
                onChange={(e) => setFormData({ ...formData, is_available: e.target.checked })}
                className="w-4 h-4 cursor-pointer"
              />
              <span className="text-sm font-medium">Available for sale</span>
            </label>
          </div>
        </div>
        
        <div className="flex gap-3 mt-6">
          <button 
            onClick={handleSubmit} 
            disabled={loading} 
            className="flex-1 py-2 bg-[#3A707A] text-white rounded-lg font-medium disabled:opacity-50 hover:bg-[#2d5a63] transition-colors flex items-center justify-center gap-2"
          >
            <MdSave size={16} /> 
            {loading ? 'Saving...' : (product ? 'Update Product' : 'Create Product')}
          </button>
          <button 
            onClick={onClose} 
            className="flex-1 py-2 bg-gray-200 rounded-lg font-medium hover:bg-gray-300 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductModal;