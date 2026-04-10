import React, { useState, useEffect } from 'react';
import { FiSearch, FiBell, FiShoppingCart, FiUser, FiMenu, FiX } from 'react-icons/fi';
import { useNavigate, NavLink } from 'react-router-dom';
import { MdLogout } from 'react-icons/md';
import { useAuth } from '../../context/AuthContext';
import useNotificationStore from '../../services/notification.service';
import NotificationSidebar from '../Notification/NotificationSidebar';
import { useSearch } from '../../context/SearchContext';
import ProductService from '../../services/product.service';
import OrderService from '../../services/order.service';
import TableService from '../../services/table.service';

const Header = ({ onCartClick }) => {
  const { user, logout } = useAuth();
  const { searchTerm, setSearchTerm, searchResults, setSearchResults, clearSearch } = useSearch();
  const navigate = useNavigate();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { unreadCount } = useNotificationStore();

  const menuItems = [
    { path: '/tables', label: 'Tables' },
    { path: '/', label: 'Menu' },
    { path: '/orders', label: 'Orders' },
    { path: '/payments', label: 'Payments' },
    { path: '/analytics', label: 'Analytics' },
    { path: '/settings', label: 'Settings' },
  ];

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (searchTerm.length >= 2) {
        performSearch();
      } else if (searchTerm.length === 0) {
        setSearchResults({ products: [], orders: [], tables: [] });
        setShowSearchResults(false);
      }
    }, 500);
    return () => clearTimeout(delayDebounce);
  }, [searchTerm]);

  const performSearch = async () => {
    try {
      const [products, orders, tables] = await Promise.all([
        ProductService.getAllProducts(),
        OrderService.getAllOrders(),
        TableService.getAllTables()
      ]);

      const filteredProducts = products.filter(p => 
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (p.description && p.description.toLowerCase().includes(searchTerm.toLowerCase()))
      );

      const filteredOrders = orders.filter(o => 
        o.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (o.customer_name && o.customer_name.toLowerCase().includes(searchTerm.toLowerCase()))
      );

      const filteredTables = tables.filter(t => 
        t.table_number.toLowerCase().includes(searchTerm.toLowerCase())
      );

      setSearchResults({
        products: filteredProducts.slice(0, 5),
        orders: filteredOrders.slice(0, 5),
        tables: filteredTables.slice(0, 5)
      });
      setShowSearchResults(true);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const handleResultClick = (type, id) => {
    clearSearch();
    setShowSearchResults(false);
    if (type === 'product') navigate('/');
    else if (type === 'order') navigate(`/orders/${id}`);
    else if (type === 'table') navigate('/tables');
  };

  const handleLogout = () => {
    logout();
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <header className="bg-white border-b sticky top-0 z-30" style={{ borderColor: '#E6E6E6' }}>
        {/* Desktop View */}
        <div className="hidden md:flex px-6 py-4 items-center justify-between gap-4">
          <h1 className="text-4xl font-bold" style={{ color: '#2E636E' }}>
            Order-Deck
          </h1>
          
          <div className="flex-1 max-w-md relative">
            <div className="relative">
              <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#555555' }} size={20} />
              <input
                type="text"
                placeholder="Search product or any order..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all bg-light-gray-bg"
                style={{ border: '1px solid #E6E6E6', color: '#1E1616' }}
              />
              {searchTerm && (
                <button
                  onClick={() => {
                    setSearchTerm('');
                    clearSearch();
                    setShowSearchResults(false);
                  }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <FiX size={16} />
                </button>
              )}
            </div>

            {/* Search Results Dropdown */}
            {showSearchResults && (searchResults.products.length > 0 || searchResults.orders.length > 0 || searchResults.tables.length > 0) && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-gray-100 z-50 max-h-96 overflow-y-auto">
                {searchResults.products.length > 0 && (
                  <div className="p-3">
                    <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Products</h4>
                    {searchResults.products.map(product => (
                      <button
                        key={product.id}
                        onClick={() => handleResultClick('product', product.id)}
                        className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-lg transition-colors flex items-center justify-between"
                      >
                        <div>
                          <p className="text-sm font-medium text-gray-800">{product.name}</p>
                          <p className="text-xs text-gray-500">रु {product.price}</p>
                        </div>
                        <span className="text-xs text-[#3A707A]">Product</span>
                      </button>
                    ))}
                  </div>
                )}
                
                {searchResults.orders.length > 0 && (
                  <div className="p-3 border-t border-gray-100">
                    <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Orders</h4>
                    {searchResults.orders.map(order => (
                      <button
                        key={order.id}
                        onClick={() => handleResultClick('order', order.id)}
                        className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-lg transition-colors flex items-center justify-between"
                      >
                        <div>
                          <p className="text-sm font-medium text-gray-800">#{order.order_number}</p>
                          <p className="text-xs text-gray-500">{order.customer_name || 'Guest'}</p>
                        </div>
                        <span className="text-xs text-[#3A707A]">Order</span>
                      </button>
                    ))}
                  </div>
                )}
                
                {searchResults.tables.length > 0 && (
                  <div className="p-3 border-t border-gray-100">
                    <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Tables</h4>
                    {searchResults.tables.map(table => (
                      <button
                        key={table.id}
                        onClick={() => handleResultClick('table', table.id)}
                        className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-lg transition-colors flex items-center justify-between"
                      >
                        <div>
                          <p className="text-sm font-medium text-gray-800">{table.table_number}</p>
                          <p className="text-xs text-gray-500">Capacity: {table.capacity}</p>
                        </div>
                        <span className="text-xs text-[#3A707A]">Table</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* No Results */}
            {showSearchResults && searchTerm.length >= 2 && searchResults.products.length === 0 && searchResults.orders.length === 0 && searchResults.tables.length === 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-gray-100 z-50 p-6 text-center">
                <p className="text-gray-500 text-sm">No results found for "{searchTerm}"</p>
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-4">
            <button onClick={() => setShowNotifications(true)} className="p-2.5 hover:bg-light-gray-bg rounded-xl relative transition-colors">
              <FiBell className="size-5 text-text-blue" />
              {unreadCount > 0 && (
                <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-red-500 rounded-full"></span>
              )}
            </button>
            
            <button onClick={onCartClick} className="p-2.5 hover:bg-light-gray-bg rounded-xl transition-colors">
              <FiShoppingCart size={20} className='text-text-blue' />
            </button>
            
            <div className="flex items-center gap-3 pl-4" style={{ borderLeft: '1px solid #E6E6E6' }}>
              <div className="size-9 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#2E636E' }}>
                <FiUser size={16} className="text-white" />
              </div>
              <div className="hidden lg:block">
                <p className="text-sm font-medium" style={{ color: '#1E1616' }}>{user?.username || 'Guest'}</p>
                <p className="text-xs" style={{ color: '#555555' }}>{user?.role || 'Staff'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Mobile View */}
        <div className="md:hidden px-4 py-3">
          <div className="flex items-center justify-between gap-3">
            <button 
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <FiMenu size={24} style={{ color: '#2E636E' }} />
            </button>
            
            <h1 className="text-xl font-bold" style={{ color: '#2E636E' }}>Order-Deck</h1>
            
            <div className="flex items-center gap-2">
              <button onClick={() => setShowNotifications(true)} className="p-2 relative">
                <FiBell size={20} className='text-text-blue' />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                )}
              </button>
              <button onClick={onCartClick} className="p-2 relative">
                <FiShoppingCart size={20} className='text-text-blue' />
              </button>
            </div>
          </div>
          
          {/* Mobile Search Bar */}
          <div className="relative mt-3">
            <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#555555' }} size={16} />
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-lg bg-light-gray-bg text-sm"
              style={{ border: '1px solid #E6E6E6', color: '#1E1616' }}
            />
          </div>

          {/* Mobile Search Results */}
          {showSearchResults && searchTerm.length >= 2 && (
            <div className="absolute left-4 right-4 top-30 bg-white rounded-xl shadow-xl border border-gray-100 z-50 max-h-80 overflow-y-auto">
              {searchResults.products.length > 0 && (
                <div className="p-2">
                  <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider px-2 pt-2">Products</h4>
                  {searchResults.products.map(product => (
                    <button
                      key={product.id}
                      onClick={() => handleResultClick('product', product.id)}
                      className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-lg"
                    >
                      <p className="text-sm font-medium text-gray-800">{product.name}</p>
                      <p className="text-xs text-gray-500">रु {product.price}</p>
                    </button>
                  ))}
                </div>
              )}
              {searchResults.orders.length > 0 && (
                <div className="p-2 border-t border-gray-100">
                  <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider px-2 pt-2">Orders</h4>
                  {searchResults.orders.map(order => (
                    <button
                      key={order.id}
                      onClick={() => handleResultClick('order', order.id)}
                      className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-lg"
                    >
                      <p className="text-sm font-medium text-gray-800">#{order.order_number}</p>
                      <p className="text-xs text-gray-500">{order.customer_name || 'Guest'}</p>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Mobile Dropdown Menu */}
        {isMobileMenuOpen && (
          <>
            <div className="fixed inset-0 bg-black/50 z-40" onClick={() => setIsMobileMenuOpen(false)} />
            <div className="fixed top-18.25 left-0 right-0 bg-white shadow-xl z-50 rounded-b-2xl mx-0 overflow-hidden">
              <nav className="py-2 max-h-[calc(100vh-73px)] overflow-y-auto">
                {menuItems.map((item) => {
                  const isActive = window.location.pathname === item.path;
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className={`flex items-center gap-3 px-4 py-3 transition-colors ${
                        isActive ? 'bg-[#3A707A]/10 text-[#3A707A]' : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      <span className="text-sm font-medium">{item.label}</span>
                      {isActive && <div className="ml-auto w-1 h-6 bg-[#3A707A] rounded-full"></div>}
                    </NavLink>
                  );
                })}
                <div className="border-t border-gray-100 my-2"></div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-3 w-full px-4 py-3 text-red-600 hover:bg-red-50 transition-colors"
                >
                  <MdLogout className="size-5" />
                  <span className="text-sm font-medium">Logout</span>
                </button>
              </nav>
            </div>
          </>
        )}
      </header>
      
      <NotificationSidebar isOpen={showNotifications} onClose={() => setShowNotifications(false)} />
    </>
  );
};

export default Header;