import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MdArrowBack, MdReceipt, MdPerson, MdTableBar, MdAccessTime, MdCurrencyRupee} from 'react-icons/md';
import useOrderStore from '../store/orderStore';
import Receipt from '../components/Payment/Receipt';
import toast from 'react-hot-toast';

const OrderDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { orders, fetchOrders } = useOrderStore();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showReceipt, setShowReceipt] = useState(false);

  useEffect(() => {
    const existingOrder = orders.find(o => o.id === parseInt(id));
    if (existingOrder) {
      setOrder(existingOrder);
      setLoading(false);
    } else {
      loadOrders();
    }
  }, [id, orders]);

  const loadOrders = async () => {
    try {
      await fetchOrders();
    } catch (error) {
      toast.error('Failed to load order details');
      navigate('/orders');
    } finally {
      setLoading(false);
    }
  };

  const handleViewReceipt = async () => {
    try {
      setShowReceipt(true);
    } catch (error) {
      toast.error('Failed to load receipt');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-700';
      case 'cancelled': return 'bg-red-100 text-red-700';
      case 'preparing': return 'bg-blue-100 text-blue-700';
      case 'ready': return 'bg-green-100 text-green-700';
      case 'served': return 'bg-purple-100 text-purple-700';
      default: return 'bg-yellow-100 text-yellow-700';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-[#3A707A] border-t-transparent"></div>
      </div>
    );
  }

  if (!order) return null;

  return (
    <>
      <div className="min-h-screen bg-[#F8FAFB] p-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-6">
            <button
              onClick={() => navigate('/orders')}
              className="flex items-center gap-2 text-gray-500 hover:text-[#3A707A] transition-colors mb-4"
            >
              <MdArrowBack size={20} /> Back to Orders
            </button>
            <div className="flex justify-between items-center flex-wrap gap-4">
              <div>
                <h1 className="text-2xl font-black text-[#3A707A] tracking-tighter uppercase">
                  Order #{order.order_number}
                </h1>
                <p className="text-xs text-gray-400 font-bold uppercase tracking-widest mt-1">
                  Order Details & Information
                </p>
              </div>
              {order.payment_status === 'paid' && (
                <button
                  onClick={handleViewReceipt}
                  className="flex items-center gap-2 px-4 py-2 bg-[#3A707A] text-white rounded-lg text-sm font-bold hover:bg-[#2E5A63] transition-colors"
                >
                  <MdReceipt size={18} /> View Receipt
                </button>
              )}
            </div>
          </div>

          {/* Order Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-[#3A707A]/10 rounded-lg">
                  <MdPerson className="text-[#3A707A]" size={20} />
                </div>
                <div>
                  <p className="text-xs text-gray-400 uppercase">Customer</p>
                  <p className="font-semibold text-gray-800 uppercase">{order.customer_name || 'Guest'}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-[#3A707A]/10 rounded-lg">
                  <MdTableBar className="text-[#3A707A]" size={20} />
                </div>
                <div>
                  <p className="text-xs text-gray-400 uppercase">Order Type</p>
                  <p className="font-semibold text-gray-800 text-sm uppercase">
                    {order.order_type === 'dine_in' ? 'Dine In' : 'Takeaway'}
                    {order.table && ` - ${order.table.table_number}`}
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-[#3A707A]/10 rounded-lg">
                  <MdAccessTime className="text-[#3A707A]" size={20} />
                </div>
                <div>
                  <p className="text-xs text-gray-400 uppercase">Date & Time</p>
                  <p className="font-semibold text-xs text-gray-800">
                    {new Date(order.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-[#3A707A]/10 rounded-lg">
                  <MdCurrencyRupee className="text-[#3A707A]" size={20} />
                </div>
                <div>
                  <p className="text-xs text-gray-400 uppercase">Total Amount</p>
                  <p className="font-bold text-md text-[#3A707A]">रु {order.total_amount}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Order Items */}
          <div className="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-50 mb-6">
            <div className="p-6 border-b border-gray-100">
              <h3 className="font-bold text-gray-800">Order Items</h3>
              <p className="text-xs text-gray-400 mt-1">{order.items?.length || 0} items</p>
            </div>
            <div className="divide-y divide-gray-100">
              {order.items?.map((item) => (
                <div key={item.id} className="p-4 flex justify-between items-center hover:bg-gray-50 transition-colors">
                  <div>
                    <p className="font-medium text-gray-800">{item.product?.name || item.product_name || `Product #${item.product_id}`}</p>
                    <p className="text-xs text-gray-500">रु {item.unit_price} × {item.quantity}</p>
                    {item.notes && <p className="text-xs text-gray-400 mt-1">Note: {item.notes}</p>}
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-[#3A707A]">रु {item.subtotal}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="p-6 bg-gray-50 border-t border-gray-100">
              <div className="flex justify-between items-center">
                <span className="font-bold text-gray-800">Grand Total</span>
                <span className="font-bold text-xl text-[#3A707A]">रु {order.total_amount}</span>
              </div>
            </div>
          </div>

          {/* Status Section */}
          <div className="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-50">
            <div className="p-6 border-b border-gray-100">
              <h3 className="font-bold text-gray-800">Order Status</h3>
            </div>
            <div className="p-6">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1.5 rounded-lg text-sm font-medium capitalize ${getStatusColor(order.status)}`}>
                    {order.status}
                  </span>
                  <span className={`px-3 py-1.5 rounded-lg text-sm font-medium capitalize ${
                    order.payment_status === 'paid' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {order.payment_status === 'paid' ? 'Paid' : 'Pending Payment'}
                  </span>
                </div>
                {order.payment_status !== 'paid' && order.status !== 'cancelled' && (
                  <button
                    onClick={() => navigate('/payments')}
                    className="px-4 py-2 bg-[#3A707A] text-white rounded-lg text-sm font-bold hover:bg-[#2E5A63] transition-colors"
                  >
                    Process Payment
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Receipt Modal */}
      {showReceipt && (
        <Receipt order={order} onClose={() => setShowReceipt(false)} />
      )}
    </>
  );
};

export default OrderDetails;