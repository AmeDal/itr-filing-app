import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { DOCUMENT_LABELS } from '../constants/docTypes';
import { FileText, CheckCircle2, AlertCircle, Trash2, Plus, ArrowRight, Loader2, Calendar, Layout } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const FilingHistoryPage = () => {
    const navigate = useNavigate();
    const [filings, setFilings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [modal, setModal] = useState({ show: false, ay: null, docType: null });
    const [deleting, setDeleting] = useState(false);

    const fetchHistory = async () => {
        try {
            const data = await apiService.getFilingHistory();
            setFilings(data);
            setLoading(false);
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    const handleDelete = async () => {
        setDeleting(true);
        try {
            await apiService.deleteDocument(modal.ay, modal.docType);
            await fetchHistory();
            setModal({ show: false, ay: null, docType: null });
        } catch (err) {
            alert(err.message);
        } finally {
            setDeleting(false);
        }
    };

    if (loading) {
        return (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
                <Loader2 className="animate-spin text-primary" size={48} />
                <p className="subtitle" style={{ marginTop: '1rem' }}>Loading filing history...</p>
            </div>
        );
    }

    return (
        <div className="fade-in" style={{ maxWidth: '1000px', margin: '0 auto' }}>
            <header style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1 style={{ margin: 0 }}>Filing History</h1>
                    <p className="subtitle" style={{ margin: 0 }}>View and manage your Income Tax Return filings.</p>
                </div>
                <button className="btn btn-primary" style={{ width: 'auto' }} onClick={() => navigate('/itr-select')}>
                    <Plus size={18} /> New Filing
                </button>
            </header>

            {filings.length === 0 ? (
                <div className="glass-card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
                    <div style={{ background: 'rgba(255,255,255,0.03)', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
                        <Layout size={32} color="var(--text-secondary)" />
                    </div>
                    <h3>No filings yet</h3>
                    <p className="subtitle">Start your first ITR extraction to see it here.</p>
                    <button className="btn btn-secondary" style={{ width: 'auto', marginTop: '1rem' }} onClick={() => navigate('/itr-select')}>
                        Get Started
                    </button>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(450px, 1fr))', gap: '1.5rem' }}>
                    {filings.map((filing) => (
                        <div key={filing.id} className="glass-card" style={{ padding: '1.5rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                                <div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-primary)', fontWeight: 700, marginBottom: '0.25rem' }}>
                                        <Calendar size={16} /> {filing.assessment_year}
                                    </div>
                                    <span className="badge badge-blue">{filing.itr_type}</span>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Last updated</div>
                                    <div style={{ fontSize: '0.85rem' }}>{new Date(filing.updated_at || filing.created_at).toLocaleDateString()}</div>
                                </div>
                            </div>

                            <div className="doc-list" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {filing.documents.length === 0 ? (
                                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>No documents uploaded yet.</p>
                                ) : (
                                    filing.documents.map((doc) => (
                                        <div key={doc.type} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                                {doc.is_extraction_complete ? (
                                                    <CheckCircle2 size={16} color="var(--success)" />
                                                ) : (
                                                    <Loader2 size={16} className="animate-spin" color="var(--accent-primary)" />
                                                )}
                                                <div>
                                                    <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{DOCUMENT_LABELS[doc.type] || doc.type}</div>
                                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{doc.name}</div>
                                                </div>
                                            </div>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                {doc.is_extraction_complete && (
                                                    <button 
                                                        className="action-btn action-btn-danger" 
                                                        onClick={() => setModal({ show: true, ay: filing.assessment_year, docType: doc.type })}
                                                        title="Delete & Re-upload"
                                                    >
                                                        <Trash2 size={14} />
                                                    </button>
                                                )}
                                                {!doc.is_extraction_complete && (
                                                    <button 
                                                        className="action-btn" 
                                                        onClick={() => navigate('/itr-select')}
                                                        title="Resume"
                                                    >
                                                        <ArrowRight size={14} />
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>

                            <footer style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', justifyContent: 'flex-end' }}>
                                <button className="btn btn-ghost" style={{ fontSize: '0.85rem', width: 'auto' }} onClick={() => navigate('/summary', { state: { ay: filing.assessment_year } })}>
                                    View Full Summary <ArrowRight size={14} style={{ marginLeft: '0.4rem' }} />
                                </button>
                            </footer>
                        </div>
                    ))}
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {modal.show && (
                <div className="modal-overlay">
                    <div className="modal-container">
                        <h2 className="modal-title">Replace Document?</h2>
                        <p className="modal-description">
                            You are about to delete the existing data for <b>{DOCUMENT_LABELS[modal.docType]}</b> in <b>{modal.ay}</b>. 
                            This action is permanent. You will need to re-upload the file to extract it again.
                        </p>
                        <div className="modal-actions">
                            <button className="btn btn-ghost" disabled={deleting} onClick={() => setModal({ show: false })}>Cancel</button>
                            <button className="btn btn-danger" disabled={deleting} onClick={handleDelete}>
                                {deleting ? <Loader2 className="animate-spin" size={16} /> : 'Delete & Continue'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FilingHistoryPage;
