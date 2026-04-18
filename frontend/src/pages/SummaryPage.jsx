import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CheckCircle2, Home, Download, ArrowRight } from 'lucide-react';

const SummaryPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { sessionId } = location.state || {};

    return (
        <div className="auth-container">
            <div className="glass-card" style={{ maxWidth: '600px', textAlign: 'center' }}>
                <div style={{ background: 'var(--success)', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 2rem', boxShadow: '0 0 40px rgba(16, 185, 129, 0.2)' }}>
                    <CheckCircle2 size={40} color="white" />
                </div>
                
                <h1>Extraction Complete</h1>
                <p className="subtitle">All your documents have been successfully parsed and structured.</p>
                
                <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', borderRadius: '20px', padding: '2rem', marginBottom: '3rem' }}>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Session ID</p>
                    <code style={{ fontSize: '1rem', color: 'var(--accent-secondary)', fontWeight: 700 }}>{sessionId}</code>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <button className="btn btn-primary" onClick={() => navigate('/itr-select')}>
                        <Home size={18} /> New Filing
                    </button>
                    <button className="btn" style={{ background: 'rgba(255,255,255,0.05)' }}>
                        <Download size={18} /> Download JSON
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SummaryPage;
