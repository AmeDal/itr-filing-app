import React, { useCallback } from 'react';
import { Upload, X, FileCheck, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

const FileDropzone = ({ 
    id, 
    label, 
    description, 
    accept = '.pdf', 
    multiple = false, 
    files = [], 
    onFilesAdded, 
    onFileRemoved,
    required = false,
    notice = ""
}) => {
    const handleFileChange = (e) => {
        const selected = Array.from(e.target.files);
        if (selected.length > 0) {
            onFilesAdded(id, selected);
        }
    };

    const onDrop = useCallback((e) => {
        e.preventDefault();
        const selected = Array.from(e.dataTransfer.files);
        if (selected.length > 0) {
            onFilesAdded(id, selected);
        }
    }, [id, onFilesAdded]);

    const onDragOver = (e) => e.preventDefault();

    return (
        <div className="upload-section" style={{ marginBottom: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <div>
                   <label className="input-label" style={{ marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                       {label} {required && <span style={{ color: 'var(--error)' }}>*</span>}
                   </label>
                   {description && <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{description}</p>}
                </div>
                {files.length > 0 && (
                    <span className="badge badge-blue">
                        {files.length} {files.length === 1 ? 'file' : 'files'}
                    </span>
                )}
            </div>

            {notice && (
                <div style={{ background: 'rgba(79, 70, 229, 0.05)', padding: '0.75rem', borderRadius: '10px', marginBottom: '1rem', border: '1px solid rgba(79, 70, 229, 0.1)', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <AlertCircle size={16} color="var(--accent-primary)" />
                    <p style={{ fontSize: '0.75rem', color: 'var(--accent-primary)', fontWeight: '600' }}>{notice}</p>
                </div>
            )}

            <div 
                className={clsx(
                    'dropzone',
                    files.length > 0 && 'has-files'
                )}
                onDrop={onDrop}
                onDragOver={onDragOver}
                onClick={() => document.getElementById(`input-${id}`).click()}
                style={{
                    border: '2px dashed var(--border-color)',
                    borderRadius: '16px',
                    padding: '1.5rem',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'var(--transition)',
                    background: 'rgba(255, 255, 255, 0.01)'
                }}
            >
                <input 
                    type="file" 
                    id={`input-${id}`} 
                    multiple={multiple} 
                    accept={accept} 
                    style={{ display: 'none' }} 
                    onChange={handleFileChange}
                />
                
                {files.length === 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                        <Upload size={32} strokeWidth={1.5} />
                        <p style={{ fontSize: '0.875rem' }}>Drag & drop or Click to upload</p>
                        <p style={{ fontSize: '0.75rem', opacity: 0.6 }}>Supports {accept}</p>
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {files.map((file, idx) => (
                            <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(255, 255, 255, 0.03)', padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflow: 'hidden' }}>
                                    <FileCheck size={16} color="var(--success)" />
                                    <span style={{ fontSize: '0.8rem', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>{file.name}</span>
                                </div>
                                <X 
                                    size={16} 
                                    className="hover-red" 
                                    style={{ cursor: 'pointer', color: 'var(--text-secondary)' }} 
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onFileRemoved(id, idx);
                                    }}
                                />
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileDropzone;
