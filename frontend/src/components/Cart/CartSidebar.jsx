import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MdClose, MdArrowBack, MdDining, MdDirectionsBike, MdCheckCircle, MdAdd } from 'react-icons/md';
import CartItem from './CartItem';
import useCartStore from '../../store/cartStore';
import OrderService from '../../services/order.service';
import RecommendationService from '../../services/recommendation.service';
import toast from 'react-hot-toast';
import { notifyOrderCreated, notifyError, notifySuccess } from '../../utils/notificationHelper';

const CartSidebar = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const { cart, fetchCart, clearCartItems, loading, selectedTable, customerName, addItem } = useCartStore();
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [step, setStep] = useState('type'); 
  const [takeawayName, setTakeawayName] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchCart();
      setStep('type');
      setTakeawayName('');
    }
  }, [isOpen, fetchCart]);

  useEffect(() => {
    if (cart?.id && cart?.items?.length > 0) {
      loadRecommendations();
    } else {
      setRecommendations([]);
    }
  }, [cart?.id, cart?.items?.length]);

  const loadRecommendations = async () => {
    setLoadingRecs(true);
    try {
      const recs = await RecommendationService.getCartRecommendations(cart.id, 3);
      setRecommendations(recs);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoadingRecs(false);
    }
  };

  const handleAddRecommendedItem = async (product) => {
    try {
      await addItem({
        product_id: product.product_id,
        quantity: 1,
        notes: ''
      });
      toast.success(`${product.name} added to cart!`);
      await loadRecommendations();
    } catch (error) {
      notifyError('Failed to add item');
      toast.error('Failed to add item');
    }
  };

  const total = cart?.items?.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0) || 0;

  const handleCheckoutDineIn = async () => {
    if (!selectedTable || !customerName) {
    const errorMsg = 'Dining: Please select table with customer name first.';
    notifyError(errorMsg);
    toast.error(errorMsg);
      return;
    }
    await placeOrder('dine_in', customerName);
  };

  const handleCheckoutTakeout = async () => {
    if (!takeawayName.trim()) {
    const errorMsg = 'Takeout: Please enter customer name.';
    notifyError(errorMsg);
    toast.error(errorMsg);
      return;
    }
    await placeOrder('takeaway', takeawayName.trim());
  };

  const placeOrder = async (orderType, finalizedCustomerName) => {
    setCheckoutLoading(true);
    try {
      const checkoutData = {
        cart_id: cart.id,
        order_type: orderType,
        customer_name: finalizedCustomerName
      };
      const order = await OrderService.checkout(checkoutData);
      notifyOrderCreated(order.order_number);
      notifySuccess('Order Placed', `Your ${orderType === 'dine_in' ? 'dine-in' : 'takeaway'} order has been placed successfully`);
      toast.success('Order placed successfully!');
      await clearCartItems();
      onClose();
      navigate('/orders');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Checkout failed. Please try again.';
      notifyError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setCheckoutLoading(false);
    }
  };

  const handleClose = () => {
    setStep('type');
    setTakeawayName('');
    onClose();
  };

  const getImageUrl = (product) => {
    if (product.image_full_url) return product.image_full_url;
    if (product.image_url) return `http://localhost:8000/assets/products/${product.image_url}`;
    return null;
  };

  const renderStepContent = () => {
    if (loading && !cart) {
      return <div className="flex-1 flex items-center justify-center text-sm font-bold text-gray-400">Loading map...</div>;
    }

    if (!cart?.items?.length) {
      return (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-gray-400">
          <p className="font-bold">Your cart is empty.</p>
          <p className="text-sm">Add items from the menu to see them here.</p>
        </div>
      );
    }

    if (step === 'type') {
      return (
        <div className="flex-1 p-6 space-y-6">
          <h3 className="text-base font-black text-text-black uppercase tracking-wider">Select Order Type</h3>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => setStep('cart')} 
              className="flex flex-col items-center justify-center gap-3 py-6 px-4 rounded-xl border-2 transition-all bg-white hover:bg-[#D1FAE5] border-gray-100 hover:border-[#A7F3D0] text-text-black"
            >
              <MdDining size={28} className="text-[#065F46]" />
              <span className="font-bold text-sm">Dining</span>
            </button>
            <button
              onClick={() => setStep('takeout_info')}
              className="flex flex-col items-center justify-center gap-3 py-6 px-4 rounded-xl border-2 transition-all bg-white hover:bg-[#E0E7FF] border-gray-100 hover:border-[#C7D2FE] text-text-black"
            >
              <MdDirectionsBike size={28} className="text-[#4338CA]" />
              <span className="font-bold text-sm">Takeout</span>
            </button>
          </div>
        </div>
      );
    }
    if (step === 'takeout_info') {
      return (
        <div className="flex-1 p-6 space-y-5">
          <button onClick={() => setStep('type')} className="text-xs text-gray-400 font-bold uppercase tracking-wide flex items-center gap-1 hover:text-gray-600 transition-colors">
            <MdArrowBack /> Back to Type
          </button>
          
          <h3 className="text-base font-black text-text-black uppercase tracking-wider">Customer Information</h3>
          <p className="text-xs text-gray-500">Please enter the customer name for the takeout order before viewing the cart.</p>
          
          <input 
            className="w-full border-2 border-gray-100 rounded-lg p-3 outline-none focus:border-[#4338CA] transition-colors text-sm"
            placeholder="Customer Name*"
            value={takeawayName}
            onChange={(e) => setTakeawayName(e.target.value)}
            autoFocus
          />
          
          <button
            onClick={() => step === 'takeout_info' && takeawayName.trim() && setStep('cart')}
            disabled={!takeawayName.trim()}
            className="w-full bg-[#4338CA] text-white py-3 rounded-xl font-bold text-xs uppercase tracking-widest transition-all disabled:opacity-50 active:scale-95 shadow-md shadow-indigo-100"
          >
            Confirm & View Cart
          </button>
        </div>
      );
    }

    if (step === 'cart') {
      const isDineInFlow = !takeawayName.trim();
      
      return (
        <>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <button onClick={() => setStep('type')} className="text-xs text-gray-400 font-bold uppercase tracking-wide flex items-center gap-1 hover:text-gray-600 transition-colors">
              <MdArrowBack /> Change Type
            </button>
            
            {isDineInFlow ? (
              selectedTable && (
                <div className="bg-emerald-50 border border-emerald-100 p-3 rounded-lg flex items-center justify-between">
                  <span className="text-xs font-bold text-[#065F46]">Table: {selectedTable} | {customerName}</span>
                  <MdCheckCircle className="text-[#10B981]" />
                </div>
              )
            ) : (
                <div className="bg-indigo-50 border border-indigo-100 p-3 rounded-lg flex items-center justify-between">
                  <span className="text-xs font-bold text-[#4338CA]">Takeout for: {takeawayName}</span>
                  <MdDirectionsBike className="text-[#6366F1]" />
                </div>
            )}
            
            {cart.items.map((item) => <CartItem key={item.id} item={item} />)}
            
            {/* Recommendations Section with Images */}
          {recommendations.length > 0 && (
            <div className="mt-6 pt-4 border-t border-gray-100">
              <h4 className="text-md font-bold text-gray-700 mb-3"> You might also like</h4>
              <div className="space-y-2">
                {recommendations.map((rec) => {
                  const imageUrl = getImageUrl(rec);
                  return (
                    <div key={rec.product_id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      {imageUrl ? (
                        <img 
                          src={imageUrl} 
                          alt={rec.name}
                          className="w-12 h-12 object-cover rounded-lg"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                      ) : null}
                      <div 
                        className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center"
                        style={{ display: imageUrl ? 'none' : 'flex' }}
                      >
                        <MdDining size={24} className="text-gray-500" />
                      </div>

                      {/* Product Info */}
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-800">{rec.name}</p>
                        <p className="text-xs text-gray-500">रु {rec.price}</p>
                        <p className="text-[10px] text-orange-500">{rec.reason}</p>
                      </div>

                      {/* Add Button */}
                      <button
                        onClick={() => handleAddRecommendedItem(rec)}
                        className="p-1.5 bg-[#2E636E] text-white rounded-lg hover:bg-[#1E4A52] transition-colors"
                      >
                        <MdAdd size={16} />
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
          </div>
          
          <div className="bg-white border-t border-gray-100 p-6 space-y-5">
            <div className="flex justify-between items-center px-1">
              <span className="text-base font-bold text-text-black">Total :</span>
              <span className="text-2xl font-black text-[#3A707A]">Rs {total}</span>
            </div>
            
            <button
              onClick={isDineInFlow ? handleCheckoutDineIn : handleCheckoutTakeout}
              disabled={checkoutLoading || (isDineInFlow && !selectedTable)}
              className="w-full bg-[#3A707A] text-white py-4 rounded-xl font-black text-sm uppercase tracking-widest transition-all shadow-lg active:scale-95 disabled:opacity-50"
            >
              {checkoutLoading ? 'Processing...' : 'Proceed to checkout'}
            </button>
            
            <button
              onClick={async () => { if(window.confirm('Clear Cart?')) { await clearCartItems(); handleClose(); } }}
              className="w-full bg-[#5FB2C3] text-white py-3 rounded-xl font-black text-sm uppercase tracking-widest active:scale-95 transition-all"
            >
              Clear Cart
            </button>
          </div>
        </>
      );
    }
  };

  return (
    <>
      {isOpen && <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-90 transition-opacity" onClick={handleClose} />}
      
      <div className={`fixed top-0 right-0 w-full max-w-md h-full bg-[#FDFDFD] shadow-2xl z-100 flex flex-col transition-transform duration-300 transform ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        
        <div className="flex items-center justify-between p-5 bg-white border-b border-gray-100">
          <h2 className="text-xl font-black text-text-black">Your Cart</h2>
          <button onClick={handleClose} className="p-1 hover:bg-gray-100 rounded-full transition-colors">
            <MdClose size={24} className="text-gray-400" />
          </button>
        </div>

        {renderStepContent()}
      </div>
    </>
  );
};

export default CartSidebar;