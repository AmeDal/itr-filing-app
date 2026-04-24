import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, FileText, ArrowRight, CheckCircle2, ChevronDown } from 'lucide-react';
import clsx from 'clsx';

const ITR_TYPES = [
    { id: 'ITR-1', name: 'ITR-1 (Sahaj)', desc: 'Salaried individuals (income up to ₹50 lakh) with one house property and simple interest income. Not for those with capital gains or business income.', status: 'active' },
    { id: 'ITR-2', name: 'ITR-2', desc: 'Individuals and HUFs with capital gains, multiple house properties, or foreign income, but no business or professional income.', status: 'active' },
    { id: 'ITR-3', name: 'ITR-3', desc: 'Individuals and HUFs having income from business or profession.', status: 'coming_soon' },
    { id: 'ITR-4', name: 'ITR-4 (Sugam)', desc: 'Individuals, HUFs, and firms (excluding LLPs) opting for presumptive taxation scheme, with income up to ₹50 lakh.', status: 'not_supported' },
    { id: 'ITR-5', name: 'ITR-5', desc: 'Firms, LLPs, AOPs, BOIs, and other non-individual entities required to file returns.', status: 'not_supported' },
];

const ITRSelectionPage = () => {
    const navigate = useNavigate();
    
    // Dynamically calculate AY options based on current date
    const ayOptions = useMemo(() => {
        const today = new Date(); // Today is April 19, 2026 per context
        const currentYear = today.getFullYear();
        const currentMonth = today.getMonth() + 1;
        
        // India: AY starts on April 1. 
        // Example: On April 19, 2026, we are in AY 2026-27
        const latestAYStart = currentMonth >= 4 ? currentYear : currentYear - 1;
        
        return [
            { 
                value: `AY-${latestAYStart}-${(latestAYStart + 1).toString().slice(-2)}`, 
                label: `${latestAYStart}-${(latestAYStart + 1).toString().slice(-2)} (Latest)` 
            },
            { 
                value: `AY-${latestAYStart - 1}-${(latestAYStart).toString().slice(-2)}`, 
                label: `${latestAYStart - 1}-${(latestAYStart).toString().slice(-2)}` 
            },
            { 
                value: `AY-${latestAYStart - 2}-${(latestAYStart - 1).toString().slice(-2)}`, 
                label: `${latestAYStart - 2}-${(latestAYStart - 1).toString().slice(-2)}` 
            },
        ];
    }, []);

    const [ay, setAy] = useState(ayOptions[0].value);
    const [selectedType, setSelectedType] = useState('ITR-1');
    const [showAYDropdown, setShowAYDropdown] = useState(false);

    const handleContinue = () => {
        if (!selectedType) return;
        navigate('/upload', { state: { ay, itrType: selectedType } });
    };

    return (
        <div className="auth-container">
            <div className="glass-card" style={{ maxWidth: '800px' }}>
                <header style={{ marginBottom: '2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                        <div style={{ background: 'var(--accent-primary)', padding: '0.5rem', borderRadius: '8px', display: 'flex' }}>
                            <FileText size={20} color="white" />
                        </div>
                        <h1 style={{ margin: 0 }}>Start Your Filing</h1>
                    </div>
                    <p className="subtitle" style={{ marginBottom: '1.5rem' }}>
                        Select the correct Assessment Year and ITR form to begin.
                    </p>
                </header>

                <div className="select-wrapper" style={{ position: 'relative' }}>
                    <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Calendar size={14} /> Assessment Year (AY)
                    </label>
                    
                    <div 
                        className="custom-select" 
                        onClick={() => setShowAYDropdown(!showAYDropdown)}
                        style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                    >
                        <span>{ayOptions.find(o => o.value === ay)?.label}</span>
                        <ChevronDown 
                            size={20} 
                            style={{ 
                                transition: 'transform 0.3s ease',
                                transform: showAYDropdown ? 'rotate(180deg)' : 'rotate(0)'
                            }} 
                        />
                    </div>

                    {showAYDropdown && (
                        <>
                            <div 
                                style={{ position: 'fixed', inset: 0, zIndex: 10 }} 
                                onClick={() => setShowAYDropdown(false)} 
                            />
                            <div className="dropdown-options">
                                {ayOptions.map(option => (
                                    <div 
                                        key={option.value}
                                        className={clsx('dropdown-item', ay === option.value && 'selected')}
                                        onClick={() => {
                                            setAy(option.value);
                                            setShowAYDropdown(false);
                                        }}
                                    >
                                        {option.label}
                                        {ay === option.value && <CheckCircle2 size={14} color="var(--accent-primary)" />}
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
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
