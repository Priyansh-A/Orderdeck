import React, { useEffect, useState } from 'react';
import OrderCard from '../components/Orders/OrderCard';
import useOrderStore from '../store/orderStore';

const Orders = () => {
  const { orders, fetchOrders, loading } = useOrderStore();
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchOrders();
  }, []);

  const statusFilters = [
    { value: 'all', label: 'All', count: orders.length, color: 'bg-gray-100 text-gray-600' },
    { value: 'pending', label: 'Pending', count: orders.filter(o => o.status === 'pending').length, color: 'bg-purple-50 text-purple-600' },
    { value: 'preparing', label: 'Preparing', count: orders.filter(o => o.status === 'preparing').length, color: 'bg-orange-50 text-orange-600' },
    { value: 'ready', label: 'Ready', count: orders.filter(o => o.status === 'ready').length, color: 'bg-blue-50 text-blue-600' },
    { value: 'served', label: 'Served', count: orders.filter(o => o.status === 'served').length, color: 'bg-indigo-50 text-indigo-600' },
    { value: 'completed', label: 'Completed', count: orders.filter(o => o.status === 'completed').length, color: 'bg-green-50 text-green-600' },
    { value: 'cancelled', label: 'Cancelled', count: orders.filter(o => o.status === 'cancelled').length, color: 'bg-red-50 text-red-600' },
  ];

  const filteredOrders = filter === 'all' 
    ? orders 
    : orders.filter(order => order.status === filter);

  const getActiveColor = (optValue) => {
    if (filter !== optValue) return optValue.color;
    switch(optValue) {
      case 'pending': return 'bg-purple-600 text-white';
      case 'preparing': return 'bg-orange-600 text-white';
      case 'ready': return 'bg-blue-600 text-white';
      case 'served': return 'bg-indigo-600 text-white';
      case 'completed': return 'bg-green-600 text-white';
      case 'cancelled': return 'bg-red-600 text-white';
      default: return 'bg-[#3A707A] text-white';
    }
  };

  return (
    <div className="min-h-screen bg-[#FDFDFD] p-6">
      <div className="max-w-7xl mx-auto mb-8">
        {/* Filter Pills with Status Colors */}
        <div className="flex gap-3 overflow-x-auto no-scrollbar pb-2">
          {statusFilters.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setFilter(opt.value)}
              className={`px-5 py-2 rounded-lg font-bold text-sm flex items-center gap-2 transition-all whitespace-nowrap
                ${filter === opt.value 
                  ? getActiveColor(opt.value) 
                  : `${opt.color} hover:opacity-80`
                }`}
            >
              {opt.label}
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                filter === opt.value 
                  ? 'bg-white/20 text-white' 
                  : 'bg-black/5 text-gray-600'
              }`}>
                {opt.count}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Order Grid */}
      <div className="max-w-7xl mx-auto">
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-10 w-10 border-4 border-[#3A707A] border-t-transparent"></div>
          </div>
        ) : filteredOrders.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-gray-200">
            <p className="text-gray-400 font-medium">No orders found in this category.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredOrders.map((order) => (
              <OrderCard 
                key={order.id} 
                order={order} 
                onStatusUpdate={fetchOrders}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Orders;