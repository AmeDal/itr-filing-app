import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import UserMenu from './UserMenu';
import ThemeToggle from './ThemeToggle';
import { ShieldCheck } from 'lucide-react';

const AppLayout = () => {
  const location = useLocation();

  return (
    <div className="app-container">
      <div className="bg-blobs">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
      </div>

      <header className="header">
        <div className="header-content">
          <Link to="/itr-select" className="logo">
            <div className="logo-icon">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <span className="logo-text">Agentic <span className="logo-italic">ITR</span></span>
          </Link>

          <nav className="nav">
            <Link to="/itr-select" className={`nav-link ${location.pathname === '/itr-select' ? 'active' : ''}`}>Dashboard</Link>
            <Link to="/upload" className={`nav-link ${location.pathname === '/upload' ? 'active' : ''}`}>Upload</Link>
          </nav>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <ThemeToggle />
            <UserMenu />
          </div>
        </div>
      </header>

      <main className="main-content">
        <Outlet />
      </main>

      <footer className="footer">
        <div className="footer-content">
          <p className="footer-copy">© 2026 Agentic ITR. All rights reserved.</p>
          <div className="footer-links">
            <a href="#" className="footer-link">Privacy Policy</a>
            <a href="#" className="footer-link">Terms of Service</a>
            <a href="#" className="footer-link">Security</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AppLayout;
