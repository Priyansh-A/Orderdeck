import React, { useState, useEffect } from 'react';
import { MdAdd, MdEdit, MdDelete, MdFastfood } from 'react-icons/md';
import ProductService from '../../services/product.service';
import CategoryService from '../../services/category.service';
import ProductModal from './ProductModal';
import toast from 'react-hot-toast';
import { notifySuccess, notifyError } from '../../utils/notificationHelper';

const ProductsTab = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [productsData, categoriesData] = await Promise.all([
        ProductService.getAllProducts(),
        CategoryService.getAllCategories()
      ]);
      setProducts(productsData);
      setCategories(categoriesData);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (product) => {
    if (!window.confirm(`Delete product ${product.name}?`)) return;
    try {
      await ProductService.deleteProduct(product.id);
      notifySuccess('Product Deleted', `${product.name} has been removed from menu`);
      toast.success('Product deleted');
      loadData();
    } catch (error) {
      notifyError(error.response?.data?.detail || 'Failed to delete product');
      toast.error('Failed to delete product');
    }
  };

  const openModal = (product = null) => {
    setEditingProduct(product);
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
          Add Product
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-50">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#E9EDF2]">
              <tr className="text-[#6C757D] text-[11px] uppercase font-bold tracking-widest">
                <th className="py-4 px-6 text-left">Product</th>
                <th className="py-4 px-6 text-left">Category</th>
                <th className="py-4 px-6 text-left">Price</th>
                <th className="py-4 px-6 text-left">Status</th>
                <th className="py-4 px-6 text-center">Actions</th>
               </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {products.map((product) => {
                const category = categories.find(c => c.id === product.category_id);
                return (
                  <tr key={product.id} className="hover:bg-gray-50 transition-colors">
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center">
                          <MdFastfood className="text-orange-600" size={16} />
                        </div>
                        <span className="font-medium text-gray-800">{product.name}</span>
                      </div>
                    </td>
                    <td className="py-4 px-6 text-gray-600">{category?.name || 'Unknown'}</td>
                    <td className="py-4 px-6 font-semibold text-[#3A707A]">रु {product.price}</td>
                    <td className="py-4 px-6">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        product.is_available ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>
                        {product.is_available ? 'Available' : 'Unavailable'}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <div className="flex justify-center gap-2">
                        <button onClick={() => openModal(product)} className="p-1.5 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors">
                          <MdEdit size={18} />
                        </button>
                        <button onClick={() => handleDelete(product)} className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                          <MdDelete size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <ProductModal
          product={editingProduct}
          categories={categories}
          onClose={() => {
            setShowModal(false);
            setEditingProduct(null);
          }}
          onSuccess={loadData}
        />
      )}
    </>
  );
};

export default ProductsTab;