import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, FileText, ArrowRight, CheckCircle2 } from 'lucide-react';
import clsx from 'clsx';

const ITR_TYPES = [
    { id: 'ITR-1', name: 'ITR-1 (Sahaj)', desc: 'For individuals having income from salaries, one house property, other sources (Interest etc.), and total income up to ₹50 lakh.', status: 'active' },
    { id: 'ITR-2', name: 'ITR-2', desc: 'For Individuals and HUFs not having income from profits and gains of business or profession.', status: 'active' },
    { id: 'ITR-3', name: 'ITR-3', desc: 'For individuals and HUFs having income from profits and gains of business or profession.', status: 'coming_soon' },
    { id: 'ITR-4', name: 'ITR-4 (Sugam)', desc: 'For Individuals, HUFs and Firms (other than LLP) being a resident having total income up to ₹50 lakh.', status: 'not_supported' },
    { id: 'ITR-5', name: 'ITR-5', desc: 'For persons other than- (i) individual, (ii) HUF, (iii) company and (iv) person filing Form ITR-7.', status: 'not_supported' },
];

const ITRSelectionPage = () => {
    const navigate = useNavigate();
    const [ay, setAy] = useState('2024-25');
    const [selectedType, setSelectedType] = useState('ITR-1');

    const handleContinue = () => {
        if (!selectedType) return;
        navigate('/upload', { state: { ay, itrType: selectedType } });
    };

    return (
        <div className="auth-container">
            <div className="glass-card" style={{ maxWidth: '800px' }}>
                <header style={{ marginBottom: '2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                        <div style={{ background: 'var(--accent-primary)', p: '0.5rem', borderRadius: '8px', display: 'flex' }}>
                            <FileText size={20} color="white" />
                        </div>
                        <h1 style={{ margin: 0 }}>Start Your Filing</h1>
                    </div>
                    <p className="subtitle" style={{ marginBottom: '1.5rem' }}>
                        Select the correct Assessment Year and ITR form to begin.
                    </p>
                </header>

                <div className="select-wrapper">
                    <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Calendar size={14} /> Assessment Year (AY)
                    </label>
                    <div style={{ position: 'relative' }}>
                        <select 
                            className="custom-select" 
                            value={ay} 
                            onChange={(e) => setAy(e.target.value)}
                        >
                            <option value="2025-26">2025-26 (Latest)</option>
                            <option value="2024-25">2024-25</option>
                            <option value="2023-24">2023-24</option>
                        </select>
                        <div style={{ position: 'absolute', right: '1.25rem', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-secondary)' }}>
                            <ArrowRight size={18} style={{ transform: 'rotate(90deg)' }} />
                        </div>
                    </div>
                </div>

                <div style={{ marginBottom: '1rem' }}>
                    <label className="input-label">Select ITR Form Type</label>
                    <div className="selection-grid">
                        {ITR_TYPES.map((type) => (
                            <div 
                                key={type.id}
                                className={clsx(
                                    'selection-card',
                                    selectedType === type.id && 'active',
                                    type.status !== 'active' && 'disabled'
                                )}
                                onClick={() => type.status === 'active' && setSelectedType(type.id)}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <h3>{type.id}</h3>
                                    {type.status === 'coming_soon' && <span className="badge badge-amber">Coming Soon</span>}
                                    {type.status === 'not_supported' && <span className="badge badge-red">Not Supported</span>}
                                    {type.status === 'active' && selectedType === type.id && <CheckCircle2 size={18} color="var(--accent-primary)" />}
                                </div>
                                <p>{type.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>

                <footer style={{ marginTop: '3rem', display: 'flex', justifyContent: 'flex-end' }}>
                    <button 
                        className="btn btn-primary" 
                        style={{ width: 'auto', paddingLeft: '2.5rem', paddingRight: '2.5rem' }}
                        disabled={!selectedType}
                        onClick={handleContinue}
                    >
                        Continue to Upload <ArrowRight size={18} />
                    </button>
                </footer>
            </div>
        </div>
    );
};

export default ITRSelectionPage;
