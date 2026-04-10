import { useEffect, useState, useCallback } from 'react';
import { 
  MdCheckCircle, MdPending, MdSearch, MdReceipt, MdDirectionsBike, MdDining,
  MdHourglassEmpty
} from 'react-icons/md';
import useOrderStore from '../store/orderStore'; 
import PaymentModal from '../components/Payment/PaymentModal';
import Receipt from '../components/Payment/Receipt';

const Payments = () => {
  const { orders, fetchOrders, loading: storeLoading } = useOrderStore();
  
  const [filteredOrders, setFilteredOrders] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('all');
  
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showReceipt, setShowReceipt] = useState(false);

  const loadData = useCallback(async () => {
    try {
      await fetchOrders();
    } catch (err) {
      console.error("Ledger sync failed:", err);
    }
  }, [fetchOrders]);

  useEffect(() => { 
    loadData(); 
  }, [loadData]);

  useEffect(() => {
    let result = orders.filter(order => order.status !== 'cancelled');

    if (activeTab !== 'all') {
      result = result.filter(o => o.payment_status === activeTab);
    }

    if (searchTerm) {
      result = result.filter(o => 
        o.order_number.toLowerCase().includes(searchTerm.toLowerCase()) || 
        (o.customer_name && o.customer_name.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    setFilteredOrders(result);
  }, [searchTerm, activeTab, orders]);

  const statusCounts = {
    all: orders.filter(o => o.status !== 'cancelled').length,
    paid: orders.filter(o => o.payment_status === 'paid' && o.status !== 'cancelled').length,
    pending: orders.filter(o => o.payment_status === 'pending' && o.status !== 'cancelled').length,
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'paid': return 'bg-green-50 text-green-600';
      case 'pending': return 'bg-yellow-50 text-yellow-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'paid': return <MdCheckCircle size={22} />;
      case 'pending': return <MdHourglassEmpty size={22} />;
      default: return <MdPending size={22} />;
    }
  };

  const getActiveColor = (tab) => {
    if (activeTab !== tab) return '';
    switch(tab) {
      case 'paid': return 'bg-green-600 text-white';
      case 'pending': return 'bg-yellow-600 text-white';
      default: return 'bg-[#3A707A] text-white';
    }
  };

  const getOrderTypeIcon = (type) => {
    return type === 'dine_in' ? <MdDining size={16} /> : <MdDirectionsBike size={16} />;
  };

  return (
    <div className="min-h-screen bg-[#FDFDFD] p-4 sm:p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-xl sm:text-2xl font-bold text-text-black">Payments</h1>
          <p className="text-xs text-gray-400 mt-1">Manage transactions and receipts</p>
        </div>

        {/* Filter Tabs - Responsive */}
        <div className="flex flex-wrap gap-2 sm:gap-3 mb-6">
          <button 
            onClick={() => setActiveTab('all')}
            className={`px-3 sm:px-5 py-1.5 sm:py-2 rounded-lg font-bold text-xs sm:text-sm flex items-center gap-1 sm:gap-2 transition-all whitespace-nowrap
              ${activeTab === 'all' 
                ? 'bg-[#3A707A] text-white' 
                : 'bg-gray-100 text-gray-600 hover:opacity-80'
              }`}
          >
            All
            <span className={`text-[9px] sm:text-[10px] px-1 py-0.5 rounded-full ${
              activeTab === 'all' 
                ? 'bg-white/20 text-white' 
                : 'bg-black/5 text-gray-600'
            }`}>
              {statusCounts.all}
            </span>
          </button>
          
          <button 
            onClick={() => setActiveTab('paid')}
            className={`px-3 sm:px-5 py-1.5 sm:py-2 rounded-lg font-bold text-xs sm:text-sm flex items-center gap-1 sm:gap-2 transition-all whitespace-nowrap
              ${activeTab === 'paid' 
                ? 'bg-green-600 text-white' 
                : 'bg-green-50 text-green-600 hover:opacity-80'
              }`}
          >
            Paid
            <span className={`text-[9px] sm:text-[10px] px-1 py-0.5 rounded-full ${
              activeTab === 'paid' 
                ? 'bg-white/20 text-white' 
                : 'bg-black/5 text-gray-600'
            }`}>
              {statusCounts.paid}
            </span>
          </button>
          
          <button 
            onClick={() => setActiveTab('pending')}
            className={`px-3 sm:px-5 py-1.5 sm:py-2 rounded-lg font-bold text-xs sm:text-sm flex items-center gap-1 sm:gap-2 transition-all whitespace-nowrap
              ${activeTab === 'pending' 
                ? 'bg-yellow-600 text-white' 
                : 'bg-yellow-50 text-yellow-600 hover:opacity-80'
              }`}
          >
            Pending
            <span className={`text-[9px] sm:text-[10px] px-1 py-0.5 rounded-full ${
              activeTab === 'pending' 
                ? 'bg-white/20 text-white' 
                : 'bg-black/5 text-gray-600'
            }`}>
              {statusCounts.pending}
            </span>
          </button>
        </div>

        {/* Search Bar */}
        <div className="relative mb-6 max-w-full sm:max-w-md">
          <MdSearch className="absolute left-3 sm:left-4 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
          <input 
            type="text" 
            placeholder="Search by order number or customer name..."
            className="w-full h-10 sm:h-11 pl-9 sm:pl-11 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#3A707A]/20 transition-all text-sm"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Orders List - Responsive */}
        <div className="space-y-3">
          {storeLoading ? (
            <div className="flex justify-center py-20">
              <div className="animate-spin rounded-full h-8 w-8 sm:h-10 sm:w-10 border-4 border-[#3A707A] border-t-transparent"></div>
            </div>
          ) : filteredOrders.length > 0 ? filteredOrders.map((order) => {
            const status = order.payment_status || 'pending';
            const statusColor = getStatusColor(status);
            
            return (
              <div 
                key={order.id} 
                className={`bg-white p-4 sm:p-5 rounded-xl border border-gray-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4 transition-all hover:shadow-md`}
              >
                <div className="flex items-center gap-3 sm:gap-4">
                  <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl flex items-center justify-center ${statusColor}`}>
                    {getStatusIcon(status)}
                  </div>

                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-bold text-text-black text-sm sm:text-base">
                        #{order.order_number}
                      </h3>
                      <span className="text-[9px] sm:text-[10px] px-1.5 sm:px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 font-medium">
                        {order.items?.length || 0} items
                      </span>
                    </div>
                    <p className="text-xs sm:text-sm capitalize text-gray-600 mt-0.5">
                      {order.customer_name || 'Guest'}
                    </p>
                    <div className="flex items-center gap-2 sm:gap-3 mt-1">
                      <div className="flex items-center gap-1 sm:gap-2">
                        {getOrderTypeIcon(order.order_type)}
                        <span className="text-[10px] sm:text-xs text-gray-400 capitalize">
                          {order.order_type === 'dine_in' ? 'Dine In' : 'Takeaway'}
                        </span>
                      </div>
                      <p className="text-[10px] sm:text-xs font-semibold text-[#3A707A]">
                        रु {order.total_amount}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button 
                    onClick={() => { 
                      setSelectedOrder(order); 
                      if (status === 'paid') {
                        setShowReceipt(true);
                      } else {
                        setShowPaymentModal(true);
                      }
                    }}
                    className={`px-4 sm:px-6 py-1.5 sm:py-2 rounded-lg font-bold text-[10px] sm:text-xs uppercase tracking-wider transition-all ${
                      status === 'paid' 
                        ? 'bg-gray-100 text-gray-600 hover:bg-gray-200' 
                        : 'bg-[#3A707A] text-white hover:bg-[#2E5A63] shadow-sm'
                    }`}
                  >
                    {status === 'paid' ? 'View Receipt' : 'Pay Now'}
                  </button>
                </div>
              </div>
            );
          }) : (
            <div className="text-center py-12 sm:py-16 bg-white rounded-xl border border-dashed border-gray-200">
              <MdReceipt size={32} className="sm:size-40 mx-auto text-gray-300 mb-3" />
              <p className="text-gray-400 font-medium text-xs sm:text-sm">No orders found</p>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {showPaymentModal && (
        <PaymentModal 
          order={selectedOrder} 
          onClose={() => { 
            setShowPaymentModal(false); 
            loadData();
          }} 
          onSuccess={() => {
            setShowPaymentModal(false);
            loadData();
          }}
        />
      )}
      
      {showReceipt && (
        <Receipt 
          order={selectedOrder} 
          onClose={() => setShowReceipt(false)} 
        />
      )}
    </div>
  );
};

export default Payments;