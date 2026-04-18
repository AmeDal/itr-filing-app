import React, { useEffect, useState, useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FileText, CheckCircle2, AlertCircle, RefreshCw, Loader2, ArrowRight } from 'lucide-react';
import { apiService } from '../services/api';

const ProgressDashboardPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { sessionId } = location.state || {};

    const [sessionState, setSessionState] = useState(null);
    const [connected, setConnected] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!sessionId) {
            navigate('/itr-select');
            return;
        }

        const es = apiService.connectProgressStream(
            sessionId,
            (data) => {
                setSessionState(data);
                setConnected(true);
                setError(null);
            },
            (err) => {
                console.error("SSE Error:", err);
                setError("Connection lost. Retrying...");
                setConnected(false);
            }
        );

        return () => es.close();
    }, [sessionId, navigate]);

    const documents = useMemo(() => {
        if (!sessionState?.documents) return [];
        return Object.values(sessionState.documents);
    }, [sessionState]);

    const overallProgress = useMemo(() => {
        if (documents.length === 0) return 0;
        const total = documents.reduce((acc, doc) => acc + (doc.total_pages || 1), 0);
        const completed = documents.reduce((acc, doc) => acc + (doc.completed_pages || 0), 0);
        return Math.round((completed / total) * 100);
    }, [documents]);

    const isAllDone = useMemo(() => {
        return documents.length > 0 && documents.every(doc => doc.status === 'completed');
    }, [documents]);

    const handleResults = () => {
        navigate('/summary', { state: { sessionId } });
    };

    return (
        <div className="auth-container">
            <div className="glass-card" style={{ maxWidth: '800px' }}>
                <header style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                            <h1 style={{ margin: 0 }}>Processing Documents</h1>
                            {!isAllDone && <Loader2 className="loading-spinner" style={{ border: 'none', animation: 'spin 2s linear infinite' }} />}
                        </div>
                        <p className="subtitle" style={{ marginBottom: 0 }}>
                            {connected ? 'Live connection active' : 'Connecting to background worker...'}
                        </p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                        <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--accent-primary)' }}>{overallProgress}%</span>
                    </div>
                </header>

                {error && (
                    <div className="error-text" style={{ padding: '0.75rem', background: 'rgba(244, 63, 94, 0.1)', borderRadius: '10px', marginBottom: '1.5rem', textAlign: 'center' }}>
                        {error}
                    </div>
                )}

                <div className="progress-list" style={{ maxHeight: '500px', overflowY: 'auto', paddingRight: '0.5rem' }}>
                    {documents.map((doc) => {
                        const progress = Math.round(((doc.completed_pages || 0) / (doc.total_pages || 1)) * 100);
                        const isError = doc.status === 'failed' || doc.status === 'error';
                        const isComplete = doc.status === 'completed';

                        return (
                            <div key={doc.file_hash} className="progress-item">
                                <div className="progress-header">
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                        <div style={{ p: '0.5rem', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', display: 'flex' }}>
                                            <FileText size={18} color="var(--text-secondary)" />
                                        </div>
                                        <div>
                                            <h4 style={{ margin: 0, fontSize: '0.95rem' }}>{doc.file_name}</h4>
                                            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{doc.doc_type.replace('_', ' ')}</span>
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        {isComplete ? (
                                            <span className="badge badge-blue" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                                <CheckCircle2 size={12} /> Completed
                                            </span>
                                        ) : isError ? (
                                            <button className="badge badge-red" style={{ border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                                <RefreshCw size={12} /> Retry
                                            </button>
                                        ) : (
                                            <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>{doc.completed_pages} of {doc.total_pages} pages</span>
                                        )}
                                    </div>
                                </div>
                                
                                <div className="progress-bar-container">
                                    <div 
                                        className={clsx(
                                            'progress-bar-fill',
                                            isComplete && 'success',
                                            isError && 'error'
                                        )} 
                                        style={{ width: `${progress}%` }} 
                                    />
                                </div>
                            </div>
                        );
                    })}
                </div>

                <footer style={{ marginTop: '3rem', display: 'flex', justifyContent: 'center' }}>
                    <button 
                        className="btn btn-primary" 
                        disabled={!isAllDone}
                        onClick={handleResults}
                        style={{ width: 'auto', paddingLeft: '3rem', paddingRight: '3rem' }}
                    >
                        View Results Summary <ArrowRight size={18} />
                    </button>
                </footer>
            </div>
        </div>
    );
};

export default ProgressDashboardPage;
