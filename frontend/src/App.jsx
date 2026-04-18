import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import AuthPage from './pages/AuthPage';
import ITRSelectionPage from './pages/ITRSelectionPage';
import DocumentUploadPage from './pages/DocumentUploadPage';
import ProgressDashboardPage from './pages/ProgressDashboardPage';
import SummaryPage from './pages/SummaryPage';

function App() {
  return (
    <BrowserRouter>
      <div className="app-root">
        <Routes>
          <Route path="/" element={<AuthPage />} />
          <Route path="/itr-select" element={<ITRSelectionPage />} />
          <Route path="/upload" element={<DocumentUploadPage />} />
          <Route path="/progress" element={<ProgressDashboardPage />} />
          <Route path="/summary" element={<SummaryPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
