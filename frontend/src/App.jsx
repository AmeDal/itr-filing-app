import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';

// Context
import { AuthProvider, useAuth } from './context/AuthContext';
import { setApiAuth } from './services/api';

// Components
import ProtectedRoute from './components/shared/ProtectedRoute';
import AppLayout from './components/shared/AppLayout';

// Pages
import AuthPage from './pages/AuthPage';
import ITRSelectionPage from './pages/ITRSelectionPage';
import DocumentUploadPage from './pages/DocumentUploadPage';
import ProgressDashboardPage from './pages/ProgressDashboardPage';
import SummaryPage from './pages/SummaryPage';
import FilingHistoryPage from './pages/FilingHistoryPage';
import AdminUsersPage from './pages/AdminUsersPage';

const ApiAuthBridge = () => {
  const { accessToken, refreshAccessToken } = useAuth();
  
  useEffect(() => {
    setApiAuth(accessToken, refreshAccessToken);
  }, [accessToken, refreshAccessToken]);
  
  return null;
};

function App() {
  return (
    <AuthProvider>
      <ApiAuthBridge />
      <BrowserRouter>
        <div className="app-root">
          <Routes>
            <Route path="/" element={<AuthPage />} />
            
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route path="/itr-select" element={<ITRSelectionPage />} />
                <Route path="/upload" element={<DocumentUploadPage />} />
                <Route path="/progress" element={<ProgressDashboardPage />} />
                <Route path="/summary" element={<SummaryPage />} />
                <Route path="/filing-history" element={<FilingHistoryPage />} />
                
                <Route element={<ProtectedRoute requireAdmin={true} />}>
                  <Route path="/admin/users" element={<AdminUsersPage />} />
                </Route>
              </Route>
            </Route>

            <Route path="*" element={<AuthPage />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
