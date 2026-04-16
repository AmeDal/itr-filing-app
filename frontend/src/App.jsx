import React from 'react';
import './index.css';
import IdentityVerification from './pages/IdentityVerification';

function App() {
  return (
    <div className="app-container">
      <header style={{ marginBottom: '3rem', textAlign: 'center' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>ITR Filing</h1>
        <p>Your secure, AI-powered income tax filing assistant</p>
      </header>
      
      <main>
        <IdentityVerification />
      </main>
      
      <footer style={{ marginTop: '5rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
        &copy; {new Date().getFullYear()} ITR Filing Assistant. All rights reserved.
      </footer>
    </div>
  );
}

export default App;
