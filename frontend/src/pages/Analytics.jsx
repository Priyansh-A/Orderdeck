import React, { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { 
  MdReceipt, MdCalendarToday, MdTrendingUp, MdCurrencyRupee, 
  MdInventory2, MdPeople, MdVisibility, MdDining, MdDirectionsBike,
  MdCheckCircle, MdHourglassEmpty , MdCancel
} from 'react-icons/md';
import useOrderStore from '../store/orderStore';
import OrderService from '../services/order.service';
import Receipt from '../components/Payment/Receipt';
import toast from 'react-hot-toast';

const Analytics = () => { 
  const { orders, fetchOrders, loading } = useOrderStore();
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [weeklyData, setWeeklyData] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [dailyOrders, setDailyOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showReceipt, setShowReceipt] = useState(false);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  useEffect(() => {
    if (orders.length > 0) {
      calculateWeeklyData();
      calculateDailyOrders();
      calculatePaymentMethods();
    }
  }, [orders, selectedDate]);

  const calculateWeeklyData = () => {
    const last7Days = [];
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(today.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      const dayOrders = orders.filter(order => {
        const orderDate = new Date(order.created_at).toISOString().split('T')[0];
        return orderDate === dateStr && order.payment_status === 'paid';
      });
      const revenue = dayOrders.reduce((sum, order) => sum + order.total_amount, 0);
      last7Days.push({
        date: dateStr,
        day: date.toLocaleDateString('en-US', { weekday: 'short' }),
        revenue,
        orders: dayOrders.length
      });
    }
    setWeeklyData(last7Days);
  };

  const calculateDailyOrders = () => {
    const filtered = orders.filter(order => {
      const orderDate = new Date(order.created_at).toISOString().split('T')[0];
      return orderDate === selectedDate;
    });
    setDailyOrders(filtered);
  };

  const calculatePaymentMethods = () => {
    const paidOrders = orders.filter(o => o.payment_status === 'paid');
    const cash = paidOrders.filter(o => o.payment?.payment_method === 'cash').length;
    const online = paidOrders.filter(o => o.payment?.payment_method === 'online').length;
    setPaymentMethods([
      { name: 'Cash', value: cash, color: '#f59e0b' },
      { name: 'Online', value: online, color: '#3A707A' }
    ]);
  };

const handleViewReceipt = async (order) => {
  try {
    let fullOrder = order;
    
    const hasProductNames = order.items?.some(item => item.product?.name || item.product_name);
    
    if (!hasProductNames) {
      const fetchedOrder = await OrderService.getOrderById(order.id);
      fullOrder = fetchedOrder;
    }
    
    setSelectedOrder(fullOrder);
    setShowReceipt(true);
  } catch (error) {
    console.error('Failed to load receipt details:', error);
    toast.error('Failed to load receipt details');
  }
};

  const totalRevenue = weeklyData.reduce((sum, day) => sum + day.revenue, 0);
  const totalOrders = weeklyData.reduce((sum, day) => sum + day.orders, 0);
  const averageDaily = totalRevenue / 7;

  const StatCard = ({ title, value, icon: Icon, colorClass, borderClass }) => (
    <div className={`bg-white p-6 rounded-2xl shadow-sm border-l-4 ${borderClass} flex items-center gap-4`}>
      <div className={`p-3 ${colorClass} rounded-xl text-white`}>
        <Icon size={24} />
      </div>
      <div>
        <p className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">{title}</p>
        <p className="text-xl font-black text-gray-800">{value}</p>
      </div>
    </div>
  );

  const getPaymentStatusColor = (status) => {
    if (status === 'paid') return 'bg-green-50 text-green-600';
    if (status === 'pending') return 'bg-orange-50 text-orange-600';
    if (status === 'cancelled') return 'bg-red-50 text-red-600';
    return 'bg-gray-100 text-gray-600';
  };

  const getPaymentStatusIcon = (status) => {
    if (status === 'paid') return <MdCheckCircle size={20} />;
    if (status === 'pending') return <MdHourglassEmpty size={20} />;
    if (status === 'cancelled') return <MdCancel size={20} />;
    return null;
  };

  const getOrderTypeIcon = (type) => {
    return type === 'dine_in' ? <MdDining size={16} /> : <MdDirectionsBike size={16} />;
  };

  return (
    <>
      <div className="min-h-screen bg-[#F8FAFB] pb-10">
        <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 px-4 sm:px-8 py-4 sm:py-6 bg-white border-b border-gray-100 mb-6 sm:mb-8">
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-[#3A707A] tracking-tighter uppercase">Analytics</h1>
            <p className="text-[10px] sm:text-xs text-gray-400 font-bold uppercase tracking-widest">Business Performance Overview</p>
          </div>
          <div className="flex items-center gap-3 bg-[#F1F4F9] px-3 sm:px-4 py-1.5 sm:py-2 rounded-xl w-full sm:w-auto justify-between sm:justify-start">
            <MdCalendarToday className="text-[#3A707A]" />
            <input 
              type="date" 
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="bg-transparent border-none text-sm font-bold text-gray-700 outline-none w-full"
            />
          </div>
        </header>

        <div className="px-8 space-y-8">
          {/* Stats Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <StatCard 
              title="Weekly Revenue" 
              value={`रु ${totalRevenue.toLocaleString()}`} 
              icon={MdCurrencyRupee} 
              colorClass="bg-green-500" 
              borderClass="border-green-500"
            />
            <StatCard 
              title="Weekly Orders" 
              value={totalOrders} 
              icon={MdInventory2} 
              colorClass="bg-[#3A707A]" 
              borderClass="border-[#3A707A]"
            />
            <StatCard 
              title="Avg. Daily" 
              value={`रु ${averageDaily.toFixed(0)}`} 
              icon={MdTrendingUp} 
              colorClass="bg-orange-400" 
              borderClass="border-orange-400"
            />
            <StatCard 
              title="Total Customers" 
              value={orders.length} 
              icon={MdPeople} 
              colorClass="bg-purple-500" 
              borderClass="border-purple-500"
            />
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 bg-white p-8 rounded-4xl shadow-sm border border-gray-50">
              <h3 className="text-sm font-black text-gray-800 uppercase tracking-widest mb-8 flex items-center gap-2">
                <span className="w-2 h-2 bg-[#3A707A] rounded-full"></span> Revenue Trend
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F4F9" />
                  <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{fontSize: 12, fontWeight: 'bold'}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fontSize: 12}} />
                  <Tooltip 
                    contentStyle={{borderRadius: '15px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'}} 
                    formatter={(value) => [`रु ${value}`, 'Revenue']}
                  />
                  <Line type="monotone" dataKey="revenue" stroke="#3A707A" strokeWidth={4} dot={{r: 6, fill: '#3A707A', strokeWidth: 2, stroke: '#fff'}} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white p-8 rounded-4xl shadow-sm border border-gray-50 flex flex-col items-center">
              <h3 className="text-sm font-black text-gray-800 uppercase tracking-widest mb-8 w-full">Payment Split</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={paymentMethods} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                    {paymentMethods.map((entry, index) => <Cell key={index} fill={entry.color} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex gap-4 mt-4">
                {paymentMethods.map((pm) => (
                  <div key={pm.name} className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{backgroundColor: pm.color}}></div>
                      <span className="text-[10px] font-bold uppercase text-gray-500">{pm.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-50">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center flex-wrap gap-3">
              <div>
                <h3 className="font-bold text-gray-800">Daily Orders Detail</h3>
                <p className="text-xs text-gray-400 mt-1">Orders for {new Date(selectedDate).toLocaleDateString()}</p>
              </div>
              <span className="px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-600">
                {dailyOrders.length} orders
              </span>
            </div>
            <div className="overflow-x-auto">
              {dailyOrders.length === 0 ? (
                <div className="text-center py-16 min-w-125">
                  <MdReceipt size={40} className="mx-auto text-gray-300 mb-3" />
                  <p className="text-gray-400 font-medium text-sm">No orders found for this date</p>
                </div>
              ) : (
                <div className="min-w-150 md:min-w-0">
                  {dailyOrders.map((order) => {
                    const paymentStatus = order.payment_status || (order.status === 'cancelled' ? 'cancelled' : 'pending');
                    const statusColor = getPaymentStatusColor(paymentStatus);

                    return (
                      <div key={order.id} className="p-4 md:p-5 hover:bg-gray-50 transition-colors border-b border-gray-100">
                        <div className="flex items-center justify-between gap-4">
                          <div className="flex items-center gap-4 md:gap-6 flex-1 flex-wrap md:flex-nowrap">
                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${statusColor}`}>
                              {getPaymentStatusIcon(paymentStatus)}
                            </div>

                            <div className="min-w-120px">
                              <div className="flex items-center gap-2 flex-wrap">
                                <h4 className="font-bold text-gray-800 text-sm">
                                  #{order.order_number}
                                </h4>
                                <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 whitespace-nowrap">
                                  {order.items?.length || 0} items
                                </span>
                              </div>
                              <div className="flex items-center gap-2 mt-1">
                                {getOrderTypeIcon(order.order_type)}
                                <span className="text-xs text-gray-400 capitalize">
                                  {order.order_type === 'dine_in' ? 'Dine In' : 'Takeaway'}
                                </span>
                              </div>
                            </div>
                            <div className="min-w-25">
                              <p className="text-sm font-medium capitalize text-gray-700 truncate max-w-30">
                                {order.customer_name || 'Guest'}
                              </p>
                            </div>
                            <div className="min-w-20">
                              <p className="text-sm text-gray-500 whitespace-nowrap">
                                {new Date(order.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </p>
                            </div>
                            <div className="min-w-20">
                              <p className="font-bold text-[#3A707A] whitespace-nowrap">रु {order.total_amount}</p>
                            </div>
                          </div>
                          {/* Action Button */}
                          <div className="shrink-0">
                            {order.payment_status === 'paid' ? (
                              <button 
                                onClick={() => handleViewReceipt(order)} 
                                className="px-3 py-1.5 md:px-4 md:py-2 bg-gray-100 text-gray-600 rounded-lg text-xs font-medium hover:bg-gray-200 transition-colors flex items-center gap-2 whitespace-nowrap"
                              >
                                <MdVisibility size={16} /> View Receipt
                              </button>
                            ) : (
                              <span className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize whitespace-nowrap ${statusColor}`}>
                                {paymentStatus}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      {/* Receipt Modal */}
      {showReceipt && selectedOrder && (
        <Receipt 
          order={selectedOrder} 
          onClose={() => {
            setShowReceipt(false);
            setSelectedOrder(null);
          }} 
        />
      )}
    </>
  );
};

export default Analytics;