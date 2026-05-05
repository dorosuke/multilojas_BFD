import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './styles/theme.css';
// Importe as páginas (criaremos em seguida)
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import Profile from './pages/Profile';
import SellerDashboard from './pages/SellerDashboard';
import MyStore from './pages/MyStore';
import MyProducts from './pages/MyProducts';
import ForgotPassword from './pages/ForgotPassword';
import Search from './pages/Search';
import PublicStore from './pages/PublicStore';
import PublicProduct from './pages/PublicProduct';
import Store from './pages/Store';
import Product from './pages/Product';

function PrivateRoute({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/login" />;
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/busca" element={<Search />} />
          <Route path="/loja/:slug" element={<PublicStore />} />
          <Route path="/produto/:slug" element={<PublicProduct />} />
          <Route path="/store/:id" element={<Store />} />
          <Route path="/store/:storeId/product/:productId" element={<Product />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
          <Route path="/seller-dashboard" element={<PrivateRoute><SellerDashboard /></PrivateRoute>} />
          <Route path="/my-store" element={<PrivateRoute><MyStore /></PrivateRoute>} />
          <Route path="/my-products" element={<PrivateRoute><MyProducts /></PrivateRoute>} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
