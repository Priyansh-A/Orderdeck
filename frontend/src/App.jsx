import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout/Layout';
import Login from './pages/Login';
import Menu from './pages/Menu';
import Orders from './pages/Orders';
import Tables from './pages/Tables';
import PaymentSuccess from './pages/PaymentSuccess';
import PaymentFailure from './pages/PaymentFailure';
import Payments from './pages/Payments';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import { SearchProvider } from './context/SearchContext';
import OrderDetails from './pages/OrderDetails';

const PrivateRoute = ({ children }) => {
  const { user, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full size-12 border-4 border-primary-500 border-t-transparent"></div>
      </div>
    );
  }
  
  return user ? children : <Navigate to="/login" />;
};

const AppContent = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={
        <PrivateRoute>
          <Layout>
            <Menu />
          </Layout>
        </PrivateRoute>
      } />
      <Route path="/orders" element={
        <PrivateRoute>
          <Layout>
            <Orders />
          </Layout>
        </PrivateRoute>
      } />
      <Route path="/tables" element={
        <PrivateRoute>
          <Layout>
            <Tables />
          </Layout>
        </PrivateRoute>
      } />
    <Route path="/payment/success" element={
      <PrivateRoute>
      <PaymentSuccess />
      </PrivateRoute>      
  } />
    <Route path="/payment/failure" element={
      <PrivateRoute>
      <PaymentFailure />
      </PrivateRoute>      
      } />
      <Route path="/payments" element={
  <PrivateRoute>
    <Layout>
      <Payments />
    </Layout>
  </PrivateRoute>
  } />
  <Route path="/analytics" element={
  <PrivateRoute>
    <Layout>
      <Analytics />
    </Layout>
  </PrivateRoute>
  } />
  <Route path="/settings" element={
  <PrivateRoute>
    <Layout>
      <Settings />
    </Layout>
  </PrivateRoute>
  } />
  <Route path="/orders/:id" element={
  <PrivateRoute>
    <Layout>
      <OrderDetails />
    </Layout>
  </PrivateRoute>
  } />
    </Routes>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
          <SearchProvider>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 1000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 1000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 1000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
        <AppContent />
        </SearchProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;