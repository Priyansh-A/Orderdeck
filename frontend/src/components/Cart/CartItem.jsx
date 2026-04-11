import React from 'react';
import { MdAdd, MdRemove, MdDeleteOutline } from 'react-icons/md';
import useCartStore from '../../store/cartStore';

const CartItem = ({ item }) => {
  const updateItem = useCartStore((state) => state.updateItem);
  const removeItem = useCartStore((state) => state.removeItem);

  const increment = () => updateItem(item.id, item.quantity + 1);
  const decrement = () => {
    if (item.quantity > 1) {
      updateItem(item.id, item.quantity - 1);
    } else {
      removeItem(item.id);
    }
  };

  const unitPrice = item.unit_price || 0;
  const productName = item.product?.name || `Product #${item.product_id}`;

  return (
    <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm mb-3">
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <h4 className="font-bold text-base text-text-black mb-2">{productName}</h4>
          
          <div className="flex items-center gap-3 mb-1">
            <div className="flex items-center gap-1">
              <button
                onClick={decrement}
                className="w-7 h-7 rounded-full bg-[#F3F6F9] flex items-center justify-center text-gray-500 hover:bg-gray-200 hover:text-black transition-colors"
              >
                <MdRemove size={14} />
              </button>
              <span className="text-sm font-bold text-text-black min-w-6 text-center">
                {item.quantity}
              </span>
              <button
                onClick={increment}
                className="w-7 h-7 rounded-full bg-[#F3F6F9] flex items-center justify-center text-gray-500 hover:bg-gray-200 hover:text-black transition-colors"
              >
                <MdAdd size={14} />
              </button>
            </div>
          </div>
          <p className="text-[11px] text-gray-400 font-medium">Rs. {unitPrice.toFixed(2)} each</p>
        </div>
        <div className="flex items-center justify-center min-w-20">
          <span className="font-black text-[#3A707A] text-lg whitespace-nowrap">
            Rs. {item.subtotal?.toFixed(2)}
          </span>
        </div>

        <div className="flex items-center justify-end min-w-11">
          <button 
            onClick={() => removeItem(item.id)}
            className="text-gray-400 hover:text-red-500 transition-colors"
          >
            <MdDeleteOutline size={22} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default CartItem;