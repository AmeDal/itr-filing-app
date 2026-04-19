import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, ShieldCheck, AlertTriangle } from 'lucide-react';
import FileDropzone from '../components/upload/FileDropzone';
import { apiService } from '../services/api';

import { DocumentType } from '../constants/docTypes';

const DocumentUploadPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { ay, itrType } = location.state || {};

    // Safety check to ensure AY is present
    useEffect(() => {
        if (!ay) navigate('/itr-select');
    }, [ay, navigate]);

    const [files, setFiles] = useState({
        [DocumentType.AS26]: [],
        [DocumentType.AIS]: [],
        [DocumentType.TIS]: [],
        [DocumentType.BANK_STATEMENT]: [],
        [DocumentType.TRADING_REPORT]: [],
        [DocumentType.FORM_16]: [],
        [DocumentType.OTHER]: []
    });

    const [showWarning, setShowWarning] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const onFilesAdded = (id, newFiles) => {
        const isMultiple = [DocumentType.BANK_STATEMENT, DocumentType.TRADING_REPORT, DocumentType.OTHER].includes(id);
        setFiles(prev => ({
            ...prev,
            [id]: isMultiple ? [...prev[id], ...newFiles] : newFiles
        }));
    };

    const onFileRemoved = (id, index) => {
        setFiles(prev => ({
            ...prev,
            [id]: prev[id].filter((_, i) => i !== index)
        }));
    };

    const isAllRequiredPresent = files[DocumentType.AS26].length > 0 && 
                                 files[DocumentType.AIS].length > 0 && 
                                 files[DocumentType.TIS].length > 0 && 
                                 files[DocumentType.BANK_STATEMENT].length > 0;

    const handleSubmit = async (force = false) => {
        if (!isAllRequiredPresent) return;

        // Form 16 Warning logic
        if (files[DocumentType.FORM_16].length === 0 && !force) {
            setShowWarning(true);
            return;
        }

        setLoading(true);
        setError(null);

        try {
            // Prepare FormData
            const formData = new FormData();
            // Ensure AY format for backend AY-YYYY-YY (now robustly handled)
            const ayCleaned = ay.replace(/\s+/g, '');
            const ayFormatted = ayCleaned.startsWith('AY-') ? ayCleaned : `AY-${ayCleaned}`;
            
            formData.append('ay', ayFormatted);
            formData.append('itr_type', itrType);

            const docTypes = [];
            
            // Flatten files and track types
            Object.entries(files).forEach(([type, fileList]) => {
                fileList.forEach(file => {
                    formData.append('files', file);
                    docTypes.push(type);
                });
            });

            formData.append('doc_types', JSON.stringify(docTypes));

            const response = await apiService.uploadDocuments(formData);
            navigate('/progress', { state: { sessionId: response.session_id, files: files } });
        } catch (err) {
            setError(err.message || "Failed to upload documents. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="glass-card" style={{ maxWidth: '1000px' }}>
                <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2.5rem' }}>
                    <div>
                        <button className="auth-toggle" onClick={() => navigate(-1)} style={{ background: 'none', border: 'none', padding: 0, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <ArrowLeft size={16} /> Change Selection
                        </button>
                        <h1 style={{ margin: 0 }}>Document Upload</h1>
                        <p className="subtitle" style={{ marginBottom: 0 }}>AY {ay} • {itrType}</p>
                    </div>
                </header>

                <div style={{ height: '500px', overflowY: 'auto', paddingRight: '1rem', marginBottom: '2rem' }}>
                    <FileDropzone 
                        id={DocumentType.AS26} label="Form 26AS" required
                        description="Tax Credit Statement from Income Tax Dept."
                        files={files[DocumentType.AS26]} onFilesAdded={onFilesAdded} onFileRemoved={onFileRemoved}
                    />
                    <FileDropzone 
                        id={DocumentType.AIS} label="AIS" required
                        description="Annual Information Statement."
                        files={files[DocumentType.AIS]} onFilesAdded={onFilesAdded} onFileRemoved={onFileRemoved}
                    />
                    <FileDropzone 
                        id={DocumentType.TIS} label="TIS" required
                        description="Taxpayer Information Summary."
                        files={files[DocumentType.TIS]} onFilesAdded={onFilesAdded} onFileRemoved={onFileRemoved}
                    />
                    <FileDropzone 
                        id={DocumentType.BANK_STATEMENT} label="Bank Statements" required multiple
                        description="PDF format only."
                        files={files[DocumentType.BANK_STATEMENT]} onFilesAdded={onFilesAdded} onFileRemoved={onFileRemoved}
                        notice="Please add ALL statements for ALL active bank accounts."
                    />
                    <FileDropzone 
                        id={DocumentType.TRADING_REPORT} label="Trading Report (Tax P&L)" multiple accept=".xls,.xlsx,.pdf"
                        description="Excel or PDF exported from Broker (Optional)."
                        files={files[DocumentType.TRADING_REPORT]} onFilesAdded={onFilesAdded} onFileRemoved={onFileRemoved}
                    />
                    <FileDropzone 
                        id={DocumentType.FORM_16} label="Form 16"
                        description="Salary Certificate from your employer (Optional)."
                        files={files[DocumentType.FORM_16]} onFilesAdded={onFilesAdded} onFileRemoved={onFileRemoved}
                    />
                    <FileDropzone 
                        id={DocumentType.OTHER} label="Other Documents" multiple accept=".pdf,.xls,.xlsx"
                        description="Investment proofs, Rent receipts, etc (Optional)."
                        files={files[DocumentType.OTHER]} onFilesAdded={onFilesAdded} onFileRemoved={onFileRemoved}
                    />
                </div>


                {error && (
                    <div className="error-text" style={{ padding: '1rem', background: 'var(--surface-overlay)', border: '1px solid var(--error)', borderRadius: '12px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <AlertTriangle size={18} /> {error}
                    </div>
                )}

                <footer style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: isAllRequiredPresent ? 'var(--success)' : 'var(--text-secondary)' }}>
                        <ShieldCheck size={20} />
                        <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>{isAllRequiredPresent ? 'All required documents ready' : 'Required documents missing'}</span>
                    </div>
                    <button 
                        className="btn btn-primary" 
                        style={{ width: 'auto', paddingLeft: '2.5rem', paddingRight: '2.5rem' }}
                        disabled={!isAllRequiredPresent || loading}
                        onClick={() => handleSubmit()}
                    >
                        {loading ? <div className="loading-spinner"></div> : 'Upload & Process'}
                        {!loading && <ArrowRight size={18} />}
                    </button>
                </footer>

                {/* Form 16 Warning Modal */}
                {showWarning && (
                    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '2rem' }}>
                        <div className="glass-card" style={{ maxWidth: '400px', textAlign: 'center' }}>
                            <div style={{ background: 'rgba(245, 158, 11, 0.15)', width: '64px', height: '64px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
                                <AlertTriangle size={32} color="#f59e0b" />
                            </div>
                            <h2>Form 16 Missing</h2>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '2rem', lineHeight: 1.5 }}>
                                If Form 16 is applicable but currently unavailable, you can upload it later. 
                                <br/><br/>
                                <strong style={{ color: 'var(--text-main)' }}>Note: Processing will be incomplete without it.</strong>
                            </p>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                <button className="btn btn-primary" onClick={() => handleSubmit(true)}>Confirm and Proceed</button>
                                <button className="btn" style={{ background: 'rgba(255,255,255,0.05)' }} onClick={() => setShowWarning(false)}>Go Back and Add</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DocumentUploadPage;
