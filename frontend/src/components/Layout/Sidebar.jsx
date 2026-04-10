import { NavLink, useLocation } from 'react-router-dom';
import { 
  MdTableRestaurant,
  MdRestaurantMenu,
  MdReceipt,
  MdPayment,
  MdAnalytics,
  MdLogout, 
  MdSettings
} from 'react-icons/md';
import { useAuth } from '../../context/AuthContext';

const menuItems = [
  { path: '/tables', icon: MdTableRestaurant, label: 'TABLES' },
  { path: '/', icon: MdRestaurantMenu, label: 'MENU' },
  { path: '/orders', icon: MdReceipt, label: 'ORDERS' },
  { path: '/payments', icon: MdPayment, label: 'PAYMENTS' },
  { path: '/analytics', icon: MdAnalytics, label: 'ANALYTICS' },
  { path: '/settings', icon: MdSettings, label: 'SETTINGS' },
];

const Sidebar = () => {
  const { logout } = useAuth();
  const location = useLocation();

  const getActiveStyle = (isActive) => {
    return isActive 
      ? 'text-[#3A707A]' 
      : 'text-gray-500 hover:text-[#3A707A] hover:bg-gray-50';
  };

  return (
    <aside className="w-32 bg-white shadow-lg flex flex-col sticky top-18.25 h-[calc(100vh-73px)]">
      <nav className="flex-1 py-6">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex flex-col items-center gap-2 px-4 py-3 transition-all duration-200 ${getActiveStyle(isActive)}`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon 
                  className="size-5 transition-all duration-200"
                  style={{ opacity: isActive ? 1 : 0.6 }}
                />
                <span className="text-xs font-normal hidden min-[750px]:block font-quicksand letter-spacing-wide text-center">
                  {item.label}
                </span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
      
      <div className="p-4 border-t" style={{ borderColor: '#E6E6E6' }}>
        <button
          onClick={logout}
          className="flex flex-col items-center gap-2 w-full px-2 py-2.5 text-gray-500 hover:bg-red-50 hover:text-red-600 rounded-xl transition-all duration-200"
        >
          <MdLogout className="size-5 transition-all duration-200" style={{ opacity: 0.6 }} />
          <span className="text-xs font-normal hidden min-[750px]:block font-quicksand letter-spacing-wide text-center">
            LOGOUT
          </span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;