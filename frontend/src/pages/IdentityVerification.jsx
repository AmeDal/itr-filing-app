import React, { useState, useEffect } from 'react';
import { Upload, ChevronRight, CheckCircle, AlertCircle, Loader2, CreditCard, Trash2, FileText, X, Sparkles, Scan, Search, RefreshCw, AlertTriangle, ChevronLeft, Lock } from 'lucide-react';
import { apiService } from '../services/api';

const IdentityVerification = () => {
    // Flows:
    // 1: Selection - Exactly 1 PAN slot, 1 Aadhar slot
    // 2: Processing - Show batch progress for these 2 docs
    // 3: Review - Verify extracted data one by one
    const [step, setStep] = useState(1);
    const [panFile, setPanFile] = useState(null);
    const [panPassword, setPanPassword] = useState('');
    const [aadharFile, setAadharFile] = useState(null);
    const [aadharPassword, setAadharPassword] = useState('');
    const [batchId, setBatchId] = useState(null);
    const [batchStatus, setBatchStatus] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [reviewIndex, setReviewIndex] = useState(0);

    // Trigger batch processing
    const startBatchProcessing = async () => {
        if (!panFile) return;
        
        setLoading(true);
        setError(null);
        try {
            const files = [panFile];
            const docTypes = ['PAN'];
            const passwords = [panPassword];
            
            if (aadharFile) {
                files.push(aadharFile);
                docTypes.push('AADHAR');
                passwords.push(aadharPassword);
            }

            const response = await apiService.extractBatch(files, docTypes, passwords);
            setBatchId(response.batch_id);
            setStep(2);
        } catch (err) {
            // Handle [object Object] cases
            let msg = err.message;
            if (typeof msg !== 'string') {
                msg = JSON.stringify(msg);
            }
            if (msg.includes('detail')) {
                try {
                    const parsed = JSON.parse(msg);
                    msg = parsed.detail[0]?.msg || msg;
                } catch(e) {}
            }
            setError(msg || 'Failed to start batch processing');
        } finally {
            setLoading(false);
        }
    };

    // Polling effect
    useEffect(() => {
        let interval;
        if (step === 2 && batchId) {
            const poll = async () => {
                try {
                    const status = await apiService.getBatchStatus(batchId);
                    setBatchStatus(status);
                    if (status.is_completed) {
                        clearInterval(interval);
                    }
                } catch (err) {
                    console.error('Polling error:', err);
                }
            };
            poll(); // initial
            interval = setInterval(poll, 2000);
        }
        return () => clearInterval(interval);
    }, [step, batchId]);

    const handleBatchConfirm = async () => {
        if (batchStatus?.is_completed) {
            const anySuccess = batchStatus.documents.some(d => d.status === 'completed');
            if (anySuccess) {
                // Find first successful doc index
                const firstSuccess = batchStatus.documents.findIndex(d => d.status === 'completed');
                setReviewIndex(firstSuccess);
                setStep(3);
            } else {
                setStep(1); // Go back to fix everything
            }
        }
    };

    const handleReviewNext = async (isFinal = false) => {
        // Find next completed doc
        const nextIndex = batchStatus.documents.findIndex((d, i) => i > reviewIndex && d.status === 'completed');
        
        if (isFinal || nextIndex === -1) {
            setStep(4);
        } else {
            setReviewIndex(nextIndex);
        }
    };

    const handleBackToUpload = () => {
        setStep(1);
        setBatchId(null);
        setBatchStatus(null);
    };

    // Only review completed docs
    const currentDocForReview = batchStatus?.documents[reviewIndex];

    const progressPercent = batchStatus 
        ? (batchStatus.documents.filter(d => ['completed', 'error'].includes(d.status)).length / batchStatus.documents.length) * 100
        : 0;

    return (
        <div className="animate-fade">
            <div className="card" style={{ maxWidth: '750px', margin: '0 auto', overflow: 'hidden', padding: '2rem' }}>

                {/* STEP 1: DUAL SLOT SELECTION */}
                {step === 1 && (
                    <div>
                        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <div style={{ background: 'linear-gradient(135deg, var(--primary), #60a5fa)', padding: '0.6rem', borderRadius: '10px' }}>
                                <CreditCard size={22} color="#fff" />
                            </div>
                            <h2 style={{ margin: 0 }}>Identity Verification</h2>
                        </div>
                        <p style={{ marginBottom: '2rem', color: 'var(--text-muted)' }}>Upload your PAN card and optionally your Aadhar card to begin identity extraction.</p>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
                            <DocumentSlot 
                                label="PAN Card" 
                                description="Mandatory Identification" 
                                file={panFile} 
                                onFileSelect={setPanFile} 
                                icon={<CreditCard size={24} color="var(--primary)" />}
                                required
                                inputId="pan-slot"
                            />
                            <DocumentSlot 
                                label="Aadhar Card" 
                                description="Optional Linkage" 
                                file={aadharFile} 
                                onFileSelect={setAadharFile} 
                                icon={<FileText size={24} color={panFile ? "var(--primary)" : "var(--border)"} />}
                                disabled={!panFile}
                                inputId="aadhar-slot"
                            />
                        </div>

                        {error && <ErrorMessage message={error} />}

                        <button 
                            className="btn btn-primary" 
                            style={{ 
                                width: '100%', 
                                padding: '1rem', 
                                background: !panFile ? 'var(--border)' : 'linear-gradient(135deg, var(--primary), #2563eb)',
                                boxShadow: !panFile ? 'none' : '0 4px 6px -1px rgba(59, 130, 246, 0.2)' 
                            }}
                            disabled={!panFile || loading} onClick={startBatchProcessing}
                        >
                            {loading ? <Loader2 className="animate-spin" /> : 'Begin Batch Extraction'}
                            {!loading && <Sparkles size={18} style={{ marginLeft: '0.5rem' }} />}
                        </button>
                    </div>
                )}

                {/* STEP 2: PROCESSING PROGRESS - CLEANER NAV */}
                {step === 2 && (
                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                            <button onClick={handleBackToUpload} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', border: 'none', background: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontWeight: 600 }}>
                                <ChevronLeft size={20} /> Back to Upload
                            </button>
                            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--primary)', background: 'rgba(59, 130, 246, 0.08)', padding: '0.3rem 0.8rem', borderRadius: '20px' }}>
                                Parallel Processing
                            </div>
                        </div>

                        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '4px', background: 'var(--bg-main)' }}>
                            <div style={{ 
                                height: '100%', background: 'linear-gradient(90deg, var(--primary), #60a5fa)', 
                                width: `${progressPercent}%`, transition: 'width 0.5s cubic-bezier(0.4, 0, 0.2, 1)' 
                            }} />
                        </div>

                        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                             <div style={{ 
                                position: 'relative', width: '80px', height: '80px', margin: '0 auto 1.5rem',
                                display: 'flex', alignItems: 'center', justifyContent: 'center'
                            }}>
                                <div style={{ position: 'absolute', inset: 0, border: '2px solid var(--primary)', borderRadius: '50%', opacity: 0.2, animation: 'pulse 2s infinite' }} />
                                <div style={{ 
                                    background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05))', 
                                    width: '100%', height: '100%', borderRadius: '50%', 
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    backdropFilter: 'blur(4px)'
                                }}>
                                    <Scan size={32} color="var(--primary)" style={{ animation: 'bounce-subtle 3s infinite' }} />
                                </div>
                            </div>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>AI Processing Engine</h2>
                            <p style={{ color: 'var(--text-muted)' }}>Scanning and verifying your identity documents in parallel.</p>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2.5rem' }}>
                            {batchStatus?.documents.map((doc) => (
                                <div key={doc.id} style={{ 
                                    padding: '1.25rem', 
                                    background: doc.status === 'error' ? 'rgba(239, 68, 68, 0.01)' : '#fff', 
                                    borderRadius: '16px',
                                    border: `1px solid ${doc.status === 'error' ? 'rgba(239, 68, 68, 0.1)' : 'var(--border)'}`, 
                                    display: 'flex', flexDirection: 'column', gap: '1rem',
                                    position: 'relative', overflow: 'hidden'
                                }}>
                                    {doc.status === 'extracting' && (
                                        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.03), transparent)', animation: 'shimmer 2s infinite' }} />
                                    )}

                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
                                        <div style={{ 
                                            width: '48px', height: '48px', borderRadius: '12px', 
                                            background: doc.status === 'completed' ? 'rgba(16, 185, 129, 0.08)' : 
                                                        doc.status === 'error' ? 'rgba(239, 68, 68, 0.08)' : 'rgba(59, 130, 246, 0.08)',
                                            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1
                                        }}>
                                            {doc.status === 'completed' ? <CheckCircle size={22} color="var(--success)" /> : 
                                             doc.status === 'error' ? (doc.error_message === 'PDF_PASSWORD_REQUIRED' ? <Lock size={22} color="var(--primary)" /> : <AlertTriangle size={22} color="var(--error)" />) : 
                                             <Loader2 size={22} color="var(--primary)" className="animate-spin" />}
                                        </div>

                                        <div style={{ flex: 1, zIndex: 1 }}>
                                            <div style={{ fontWeight: 700, color: doc.status === 'error' ? (doc.error_message === 'PDF_PASSWORD_REQUIRED' ? 'var(--primary)' : 'var(--error)') : 'var(--text-main)' }}>
                                                {doc.doc_type} Data Analysis
                                            </div>
                                            <div style={{ fontSize: '0.8125rem', color: doc.status === 'error' ? 'var(--text-muted)' : 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                                {doc.status === 'completed' && 'Verification successful.'}
                                                {doc.status === 'error' && (doc.error_message === 'PDF_PASSWORD_REQUIRED' ? 'Encrypted document detected.' : (doc.error_message || 'Processing failed.'))}
                                                {doc.status === 'queued' && 'Waiting for secure engine...'}
                                                {doc.status === 'extracting' && 'Structuring extracted content...'}
                                            </div>
                                        </div>

                                        {doc.status === 'error' && doc.error_message !== 'PDF_PASSWORD_REQUIRED' && (
                                            <button 
                                                onClick={startBatchProcessing}
                                                style={{ 
                                                    zIndex: 1, padding: '0.5rem 1rem', borderRadius: '10px', border: '1px solid rgba(239, 68, 68, 0.1)',
                                                    background: '#fff', color: 'var(--error)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', fontWeight: 700
                                                }}
                                            >
                                                <RefreshCw size={14} /> Retry Scan
                                            </button>
                                        )}
                                    </div>

                                    {/* PASSWORD SECTION */}
                                    {doc.status === 'error' && doc.error_message === 'PDF_PASSWORD_REQUIRED' && (
                                        <div style={{ zIndex: 1, padding: '1rem', background: 'rgba(59, 130, 246, 0.03)', borderRadius: '12px', display: 'flex', gap: '0.75rem', alignItems: 'flex-end' }}>
                                            <div style={{ flex: 1 }}>
                                                <label style={{ fontSize: '0.65rem', fontWeight: 800, textTransform: 'uppercase', marginBottom: '0.4rem', display: 'block' }}>Enter PDF Password</label>
                                                <input 
                                                    type="password" 
                                                    style={{ width: '100%', padding: '0.6rem', borderRadius: '8px', border: '1px solid var(--border)' }}
                                                    placeholder="Required to unlock"
                                                    value={doc.doc_type === 'PAN' ? panPassword : aadharPassword}
                                                    onChange={(e) => doc.doc_type === 'PAN' ? setPanPassword(e.target.value) : setAadharPassword(e.target.value)}
                                                />
                                            </div>
                                            <button 
                                                onClick={startBatchProcessing}
                                                style={{ 
                                                    padding: '0.6rem 1.25rem', borderRadius: '8px', background: 'var(--primary)', 
                                                    color: '#fff', border: 'none', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem'
                                                }}
                                            >
                                                <Lock size={14} /> Unlock & Retry
                                            </button>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>

                        {batchStatus?.is_completed && batchStatus.documents.some(d => d.status === 'error' && d.error_message !== 'PDF_PASSWORD_REQUIRED') && (
                            <div style={{ 
                                padding: '1.25rem', background: '#fef2f2', borderRadius: '16px', border: '1px solid #fee2e2',
                                marginBottom: '2.5rem', display: 'flex', gap: '1rem', alignItems: 'flex-start'
                            }}>
                                <AlertTriangle size={22} color="var(--error)" style={{ marginTop: '0.1rem' }} />
                                <div style={{ fontSize: '0.875rem', color: '#991b1b', lineHeight: 1.5 }}>
                                    <div style={{ fontWeight: 800, marginBottom: '0.2rem' }}>Processing Attention Required</div>
                                    One or more documents couldn't be automatically verified. You can <strong>Retry Scan</strong> above or go <strong>Back to Upload</strong>.
                                </div>
                            </div>
                        )}

                        <button 
                            className="btn btn-primary" 
                            style={{ 
                                width: '100%', 
                                padding: '1rem',
                                background: batchStatus?.documents.some(d => d.status === 'completed') ? 'var(--primary)' : 'var(--border)' 
                            }} 
                            disabled={!batchStatus?.is_completed || !batchStatus.documents.some(d => d.status === 'completed')} 
                            onClick={handleBatchConfirm}
                        >
                            Continue to Review
                            <ChevronRight size={18} style={{ marginLeft: '0.5rem' }} />
                        </button>
                    </div>
                )}

                {/* STEP 3: REVIEW RESULTS */}
                {step === 3 && currentDocForReview && (
                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                            <button onClick={() => setStep(2)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', border: 'none', background: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontWeight: 600 }}>
                                <ChevronLeft size={20} /> Back to Status
                            </button>
                            <div style={{ fontSize: '0.75rem', color: 'var(--primary)', background: 'rgba(59, 130, 246, 0.1)', padding: '0.4rem 1rem', borderRadius: '20px', fontWeight: 700 }}>
                                {reviewIndex + 1} / {batchStatus.documents.filter(d => d.status === 'completed').length}
                            </div>
                        </div>

                        <div style={{ padding: '2rem', background: 'var(--bg-main)', borderRadius: '20px', border: '1px solid var(--border)', marginBottom: '2rem' }}>
                            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginBottom: '2rem' }}>
                                <div style={{ background: 'var(--primary)', width: '3px', height: '1.25rem', borderRadius: '4px' }} />
                                <h3 style={{ margin: 0, fontSize: '1.125rem', fontWeight: 800 }}>{currentDocForReview.doc_type} Data Details</h3>
                            </div>
                            
                            {currentDocForReview.doc_type === 'PAN' ? (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                                    <FormInput label="PAN NUMBER" value={currentDocForReview.extraction_data?.pan_number} disabled />
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
                                        <FormInput label="FIRST NAME" value={currentDocForReview.extraction_data?.first_name} />
                                        <FormInput label="LAST NAME" value={currentDocForReview.extraction_data?.last_name} />
                                    </div>
                                    <FormInput label="FATHER NAME" value={currentDocForReview.extraction_data?.father_name} />
                                    <FormInput label="DATE OF BIRTH" type="date" value={currentDocForReview.extraction_data?.dob} />
                                </div>
                            ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                                    <FormInput label="AADHAR NUMBER" value={currentDocForReview.extraction_data?.aadhar_number} disabled />
                                    <FormInput label="RESIDENTIAL ADDRESS" value={currentDocForReview.extraction_data?.address_line} />
                                    <FormInput label="POSTAL PINCODE" value={currentDocForReview.extraction_data?.pincode} />
                                </div>
                            )}
                        </div>

                        <button className="btn btn-primary" style={{ width: '100%', padding: '1rem' }} onClick={() => handleReviewNext(batchStatus.documents.filter(d => d.status === 'completed').length === reviewIndex + 1)}>
                            {batchStatus.documents.filter(d => d.status === 'completed').length === reviewIndex + 1 ? 'Complete Verification' : 'Next Document'} 
                            <ChevronRight size={18} style={{ marginLeft: '0.5rem' }} />
                        </button>
                    </div>
                )}

                {/* STEP 4: SUCCESS */}
                {step === 4 && (
                    <div style={{ textAlign: 'center', padding: '4rem 0' }}>
                        <div style={{ position: 'relative', width: '100px', height: '100px', margin: '0 auto 2.5rem' }}>
                            <div style={{ absolute: 0, background: 'rgba(16, 185, 129, 0.1)', borderRadius: '50%', transform: 'scale(1.2)', animation: 'pulse 2s infinite' }} />
                            <div style={{ position: 'absolute', inset: 0, background: 'var(--success)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <CheckCircle size={52} color="#fff" />
                            </div>
                        </div>
                        <h2 style={{ fontSize: '2rem', fontWeight: 900, marginBottom: '1rem' }}>Identity Verified</h2>
                        <p style={{ color: 'var(--text-muted)', marginBottom: '3.5rem', maxWidth: '450px', margin: '0 auto 3.5rem', lineHeight: 1.6 }}>Your documents have been processed and confirmed. Your secure profile is now active.</p>
                        <button className="btn btn-primary" style={{ padding: '1rem 4rem' }} onClick={() => window.location.reload()}>Finish & Continue</button>
                    </div>
                )}
            </div>

            <style dangerouslySetInnerHTML={{ __html: `
                @keyframes pulse { 0% { transform: scale(1); opacity: 0.2; } 50% { transform: scale(1.05); opacity: 0.1; } 100% { transform: scale(1); opacity: 0.2; } }
                @keyframes shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
                @keyframes bounce-subtle { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
                .dot-pulse { width: 4px; height: 4px; border-radius: 50%; background: var(--primary); display: inline-block; margin-right: 4px; animation: dot-pulse 1.5s infinite ease-in-out; }
                @keyframes dot-pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.3; transform: scale(0.8); } }
            `}} />
        </div>
    );
};

const DocumentSlot = ({ label, description, file, onFileSelect, icon, required, disabled, inputId }) => (
    <div 
        style={{
            border: '2px dashed',
            borderColor: file ? 'var(--success)' : (disabled ? 'var(--border)' : '#e2e8f0'),
            borderRadius: '24px', padding: '2rem 1.5rem', textAlign: 'center',
            background: disabled ? 'rgba(0,0,0,0.02)' : (file ? 'rgba(16, 185, 129, 0.01)' : 'white'),
            cursor: disabled ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            opacity: disabled ? 0.4 : 1,
            position: 'relative'
        }}
        onClick={() => !disabled && document.getElementById(inputId).click()}
    >
        <div style={{ marginBottom: '1.25rem', display: 'flex', justifyContent: 'center' }}>
            {file ? <CheckCircle size={32} color="var(--success)" /> : icon}
        </div>
        <div style={{ fontWeight: 800, fontSize: '1rem', color: 'var(--text-main)' }}>{label} {required && '*'}</div>
        <div style={{ 
            fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem', 
            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100%' 
        }}>
            {file ? file.name : description}
        </div>
        <input id={inputId} type="file" hidden accept="image/*,application/pdf" onChange={(e) => e.target.files[0] && onFileSelect(e.target.files[0])} disabled={disabled} />
    </div>
);

const FormInput = ({ label, value, type = 'text', disabled = false }) => (
    <div className="input-group">
        <label className="input-label" style={{ fontSize: '0.6875rem', fontWeight: 800, color: 'var(--text-muted)', marginBottom: '0.6rem', display: 'block', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</label>
        <input 
            className="input-field" 
            type={type} 
            value={value || ''} 
            readOnly={disabled} 
            style={{ 
                borderRadius: '14px', padding: '0.875rem 1.25rem', border: '1px solid #e2e8f0', 
                background: disabled ? '#f8fafc' : '#fff', cursor: disabled ? 'not-allowed' : 'text', 
                width: '100%', fontWeight: disabled ? 700 : 500, color: 'var(--text-main)'
            }} 
        />
    </div>
);

const ErrorMessage = ({ message }) => (
    <div style={{ 
        display: 'flex', alignItems: 'center', gap: '1rem', color: '#b91c1c', 
        marginBottom: '2rem', fontSize: '0.875rem', background: '#fef2f2', 
        padding: '1.25rem', borderRadius: '16px', border: '1px solid #fee2e2' 
    }}>
        <AlertTriangle size={22} /><span style={{ fontWeight: 700 }}>{message}</span>
    </div>
);

export default IdentityVerification;
