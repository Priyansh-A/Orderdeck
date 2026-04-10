import React, { useState } from 'react';
import { 
  MdAccessTime, MdTableBar, MdCheckCircle, MdRestaurant, 
  MdDirectionsBike, MdFastfood, MdDeleteOutline, MdLocalDining 
} from 'react-icons/md';
import useOrderStore from '../../store/orderStore';
import toast from 'react-hot-toast';

const OrderCard = ({ order, onStatusUpdate }) => {
  const { updateStatus, cancelOrder } = useOrderStore();
  const [updating, setUpdating] = useState(false);
  const [localStatus, setLocalStatus] = useState(order.status);

  const statusConfig = {
    pending:   { label: 'Pending', btn: 'bg-purple-50 text-purple-600', next: 'preparing', icon: <MdFastfood size={16}/> },
    preparing: { label: 'Preparing', btn: 'bg-orange-50 text-orange-600', next: 'ready', icon: <MdRestaurant size={16}/> },
    ready:     { label: 'Ready', btn: 'bg-blue-50 text-blue-600', next: 'served', icon: <MdCheckCircle size={16}/> },
    served:    { label: 'Served', btn: 'bg-indigo-50 text-indigo-600', next: 'completed', icon: <MdLocalDining size={16}/> },
    completed: { label: 'Completed', btn: 'bg-green-50 text-green-600', next: null, icon: <MdCheckCircle size={16}/> },
    cancelled: { label: 'Cancelled', btn: 'bg-red-50 text-red-600', next: null, icon: <MdDeleteOutline size={16}/> },
  };

  const currentTheme = statusConfig[localStatus] || statusConfig.pending;
  const itemCount = order.items?.length || 0;

  const handleNextStatus = async () => {
    if (!currentTheme.next) return;
    setUpdating(true);
    const newStatus = currentTheme.next;
    setLocalStatus(newStatus);
    
    try {
      await updateStatus(order.id, newStatus);
      notifyOrderStatusUpdated(order.order_number, newStatus);
      toast.success(`Order #${order.order_number?.slice(-3)} updated to ${newStatus}`);
      if (onStatusUpdate) onStatusUpdate(newStatus); 
    } catch (err) { 
      setLocalStatus(order.status);
      notifyError("Update failed");
      toast.error("Update failed"); 
    } finally { 
      setUpdating(false); 
    }
  };

  const handleCancel = async () => {
    if (!window.confirm("Cancel this order?")) return;
    setUpdating(true);
        setLocalStatus('cancelled');
    try {
      await cancelOrder(order.id);
      notifyOrderStatusUpdated(order.order_number, 'cancelled');
      toast.success("Order Cancelled");
      if (onStatusUpdate) onStatusUpdate('cancelled');
    } catch (err) { 
      setLocalStatus(order.status);
      notifyError("Cancel failed");
      toast.error("Cancel failed"); 
    } finally { 
      setUpdating(false); 
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return `${date.getDate()} ${date.toLocaleDateString('en-GB', { month: 'short' })}, ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  };

  return (
    <div className={`bg-white rounded-xl border border-gray-100 p-5 shadow-sm transition-all relative ${localStatus === 'cancelled' ? 'opacity-60' : 'hover:shadow-md'}`}>
      
      {/* Header */}
      <div className="flex justify-between items-start mb-1">
        <h3 className="text-text-black capitalize font-bold text-base truncate pr-2">
          {order.customer_name || 'Walking Customer'}
        </h3>
        <div className="flex items-center gap-2 shrink-0">
          {localStatus !== 'cancelled' && localStatus !== 'completed' && (
            <button onClick={handleCancel} className="text-gray-300 hover:text-red-500 transition-colors mr-1">
              <MdDeleteOutline size={18} />
            </button>
          )}
          <span className="bg-[#F3F6F9] text-[#3A707A] text-[10px] font-bold px-2 py-0.5 rounded-md">
            #{String(itemCount).padStart(3, '0')}
          </span>
        </div>
      </div>

      {/* Meta */}
      <div className="flex flex-col gap-1 mb-4">
        <div className="flex items-center gap-1.5 text-gray-400 text-[11px] font-medium">
          <MdAccessTime size={14} />
          <span>{formatDate(order.created_at)}</span>
        </div>
        <div className="flex items-center gap-1.5 text-gray-400 text-[11px] font-medium">
          <MdTableBar size={14} />
          <span>{order.order_type === 'dine_in' ? `Table ${order.table?.table_number || '01'}` : 'Takeaway'}</span>
        </div>
      </div>

      <div className="border-t border-dashed border-gray-200 my-3"></div>

      {/* Items List */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-text-black font-bold text-sm">Order ({itemCount})</span>
          <span className="text-[#3A707A] font-bold text-sm">रु {order.total_amount}</span>
        </div>
        <div className="space-y-1.5">
          {order.items?.slice(0, 2).map((item, idx) => (
            <div key={idx} className="flex justify-between text-[12px] text-gray-500">
              <span className="truncate pr-4">{item.quantity}x {item.product?.name || item.product_name}</span>
              <span className="shrink-0 text-text-black font-medium">रु {(item.subtotal || (item.price * item.quantity)).toLocaleString()}</span>
            </div>
          ))}
          {itemCount > 2 && <button className="text-[#3A707A] text-[11px] font-bold mt-1 underline">See More {'>'}</button>}
        </div>
      </div>

      {/* Footer Button Logic */}
      <div className="flex items-center gap-2 mt-4">
        <button 
          onClick={handleNextStatus}
          disabled={updating || !currentTheme.next}
          className={`grow flex items-center justify-center gap-2 py-2.5 rounded-lg text-[10px] font-extrabold uppercase tracking-tight transition-all ${currentTheme.btn} disabled:opacity-50`}
        >
          {currentTheme.icon} {currentTheme.label}
        </button>
        <div className="bg-[#F3F6F9] text-[#3A707A] p-2.5 rounded-lg">
          {order.order_type === 'dine_in' ? <MdRestaurant size={18} /> : <MdDirectionsBike size={18} />}
        </div>
      </div>
    </div>
  );
};

export default OrderCard;