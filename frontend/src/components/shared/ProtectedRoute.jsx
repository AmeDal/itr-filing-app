import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Loader2 } from 'lucide-react';

const ProtectedRoute = ({ requireAdmin = false }) => {
  const { isAuthenticated, isAdmin, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="auth-container" style={{ background: 'var(--bg-dark)' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
          <Loader2 className="loading-spinner" size={48} style={{ color: 'var(--accent-primary)', border: 'none' }} />
          <p className="subtitle" style={{ margin: 0 }}>Authenticating...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Save the attempted location for post-login redirect
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  if (requireAdmin && !isAdmin) {
    // If user is logged in but not admin, redirect to base authenticated page
    return <Navigate to="/itr-select" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;

