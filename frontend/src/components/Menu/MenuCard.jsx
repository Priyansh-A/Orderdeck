import React, { useState } from 'react';
import { MdAdd, MdRemove } from 'react-icons/md';
import useCartStore from '../../store/cartStore';

const MenuCard = ({ product }) => {
  const [quantity, setQuantity] = useState(1);
  const addItem = useCartStore((state) => state.addItem);

  const handleAddToCart = () => {
    addItem({ product_id: product.id, quantity: quantity, notes: '' });
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden flex flex-col h-full shadow-sm hover:shadow-md transition-shadow">
      <div className="relative aspect-video w-full bg-gray-50">
        <img 
          src={product.image_full_url || `http://localhost:8000/assets/products/${product.image_url}`}
          alt={product.name}
          className="w-full h-full object-cover"
        />
      </div>

      <div className="p-2 sm:p-3 flex flex-col flex-1">
        <h3 className="font-bold text-gray-800 text-xs sm:text-sm mb-1 truncate">
          {product.name}
        </h3>
        
        <p className="text-gray-500 text-[10px] sm:text-[11px] leading-tight mb-2 line-clamp-2">
          {product.description || 'Description goes here...'}
        </p>

        <div className="mt-auto">
          <div className="flex flex-wrap items-center justify-between gap-1 mb-2">
            <span className="text-xs sm:text-sm font-bold text-gray-800 whitespace-nowrap">
              Rs {product.price}
            </span>
            
            <div className="flex items-center bg-gray-100 rounded-md px-1 py-0.5 gap-2">
              <button onClick={() => setQuantity(q => Math.max(1, q - 1))} className="hover:text-primary-500">
                <MdRemove size={14} />
              </button>
              <span className="font-bold text-[10px] sm:text-xs min-w-2.5 text-center">{quantity}</span>
              <button onClick={() => setQuantity(q => q + 1)} className="hover:text-primary-500">
                <MdAdd size={14} />
              </button>
            </div>
          </div>
          
          <button 
            onClick={handleAddToCart}
            className="w-full bg-[#3A707A] text-white py-1.5 rounded-md text-[10px] sm:text-[12px] font-bold transition-colors active:scale-95"
          >
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );
};

export default MenuCard;