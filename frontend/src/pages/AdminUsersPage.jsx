import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useLocation, useNavigate } from 'react-router-dom';
import { Users, Trash2, Key, UserCheck, UserX, Shield, ShieldOff, Search, Loader2 } from 'lucide-react';

const AdminUsersPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user: currentUser, logout } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [modal, setModal] = useState({ show: false, type: '', data: null });
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [passDraft, setPassDraft] = useState('');
  const [confirmPassDraft, setConfirmPassDraft] = useState('');
  const [shouldLogout, setShouldLogout] = useState(false);

  const closeModal = () => {
    if (modal.type === 'success' && shouldLogout) {
      logout();
      return;
    }
    setModal({ show: false, type: '', data: null });
    setPassDraft('');
    setConfirmPassDraft('');
  };

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await apiService.listUsers();
      setUsers(data.users);
      setSelectedIds(new Set()); // Reset selection on refresh
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // Monitor for navigation away after self-reset success
  useEffect(() => {
    if (shouldLogout) {
       // If modal is closed or user navigates, they must logout.
       // We'll logout immediately if they try to move.
       return () => {
          if (shouldLogout) logout();
       };
    }
  }, [shouldLogout, logout]);

  const handleDelete = async (userId) => {
    try {
      await apiService.deleteUser(userId);
      setModal({ show: true, type: 'success', data: { message: "User has been permanently deleted." } });
      fetchUsers();
    } catch (err) {
      setModal({ show: true, type: 'error', data: { message: err.message } });
    }
  };

  const handleResetPassword = async (userId, newPass, confirmPass) => {
    if (!newPass) return;
    if (newPass !== confirmPass) {
       setModal({ show: true, type: 'error', data: { message: "Passwords do not match. Please re-enter." } });
       return;
    }
    
    // Quick client-side complexity check (now synced to 12 chars)
    const complexityRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$/;
    if (!complexityRegex.test(newPass)) {
       setModal({ show: true, type: 'error', data: { message: "Password is too weak. It must be at least 12 characters and contain uppercase, lowercase, a number, and a special character." } });
       return;
    }

    try {
      await apiService.resetPassword(userId, newPass);
      setModal({ show: true, type: 'success', data: { message: "Password updated successfully." } });
      if (userId === currentUser.id) {
         setShouldLogout(true);
      }
      fetchUsers();
    } catch (err) {
      setModal({ show: true, type: 'error', data: { message: err.message } });
    }
  };

  const handleBulkDelete = async () => {
    try {
      const count = selectedIds.size;
      await apiService.bulkDeleteUsers(Array.from(selectedIds));
      setModal({ show: true, type: 'success', data: { message: `${count} users have been permanently deleted.` } });
      fetchUsers();
    } catch (err) {
      setModal({ show: true, type: 'error', data: { message: err.message } });
    }
  };

  const toggleSelect = (userId) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(userId)) newSelected.delete(userId);
    else newSelected.add(userId);
    setSelectedIds(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === filteredUsers.length && filteredUsers.length > 0) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredUsers.map(u => u._id)));
    }
  };

  const filteredUsers = users.filter(u => 
    u.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.pan_number.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header className="admin-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Shield className="w-8 h-8 text-primary" />
            <h1 style={{ margin: 0 }}>User Management</h1>
          </div>
          <p className="subtitle" style={{ margin: 0 }}>Administrative control over portal users and data storage.</p>
        </div>
        
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          {selectedIds.size > 0 && (
            <button 
              className="btn btn-danger fade-in" 
              style={{ padding: '0.625rem 1.25rem', whiteSpace: 'nowrap' }}
              onClick={() => setModal({ show: true, type: 'bulk-delete', data: null })}
            >
              Delete Selected ({selectedIds.size})
            </button>
          )}
          <div className="search-container">
            <Search className="search-icon" />
            <input 
              type="text" 
              placeholder="Search by name or PAN..."
              className="search-input"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </header>

      <div className="glass-card" style={{ maxWidth: 'none', padding: 0, overflow: 'hidden', opacity: shouldLogout ? 0.3 : 1, pointerEvents: shouldLogout ? 'none' : 'auto' }}>
        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '5rem 0' }}>
            <Loader2 className="w-10 h-10 text-primary animate-spin" style={{ marginBottom: '1rem' }} />
            <p className="text-secondary">Decrypting user records...</p>
          </div>
        ) : error ? (
           <div style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--error)' }}>{error}</div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '40px' }}>
                    <input 
                      type="checkbox" 
                      className="custom-checkbox"
                      checked={selectedIds.size === filteredUsers.filter(u => u._id !== currentUser.id).length && filteredUsers.length > 1} 
                      onChange={toggleSelectAll} 
                    />
                  </th>
                  <th>User</th>
                  <th>ID / PAN</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map(u => (
                   <tr key={u._id} className={selectedIds.has(u._id) ? 'row-selected' : ''}>
                    <td>
                      <input 
                        type="checkbox" 
                        className="custom-checkbox"
                        disabled={u._id === currentUser.id}
                        checked={selectedIds.has(u._id)} 
                        onChange={() => toggleSelect(u._id)} 
                      />
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, color: 'white' }}>{u.first_name} {u.last_name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{u.email}</div>
                    </td>
                    <td style={{ fontFamily: 'monospace' }}>
                        <div style={{ fontSize: '0.7rem', opacity: 0.5 }}>{u._id}</div>
                        <div>{u.pan_number}</div>
                    </td>
                    <td>
                      <span className="badge badge-blue">
                        {u.role}
                      </span>
                    </td>
                    <td>
                        <div className="status-indicator">
                            <div className={`dot ${u.is_active ? 'dot-active' : 'dot-inactive'}`}></div>
                            <span style={{ fontSize: '0.75rem' }}>{u.is_active ? 'Active' : 'Deactivated'}</span>
                        </div>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                        <button 
                          onClick={() => setModal({ show: true, type: 'reset', data: u })}
                          className="action-btn"
                          title="Reset Password"
                        >
                          <Key className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => setModal({ show: true, type: 'delete', data: u })}
                          className="action-btn action-btn-danger"
                          title={u._id === currentUser.id ? "Cannot delete yourself" : "Delete User"}
                          disabled={u._id === currentUser.id}
                          style={{ opacity: u._id === currentUser.id ? 0.3 : 1, cursor: u._id === currentUser.id ? 'not-allowed' : 'pointer' }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>

      {/* Custom Modal */}
      {modal.show && (
        <div className="modal-overlay">
          <div className="modal-container">
            {modal.type === 'delete' ? (
              <>
                <h2 className="modal-title">Delete User?</h2>
                <p className="modal-description">
                  Are you sure you want to delete <b>{modal.data.first_name} {modal.data.last_name}</b>? 
                  This will permanently remove all extraction data and storage blobs. This action cannot be undone.
                </p>
                <div className="modal-actions">
                  <button className="btn btn-ghost" style={{ width: 'auto' }} onClick={closeModal}>Cancel</button>
                  <button className="btn btn-danger" style={{ width: 'auto' }} onClick={() => handleDelete(modal.data._id)}>Delete Permanently</button>
                </div>
              </>
            ) : modal.type === 'bulk-delete' ? (
              <>
                <h2 className="modal-title">Delete {selectedIds.size} Users?</h2>
                <p className="modal-description">
                  You are about to delete <b>{selectedIds.size} selected users</b> and all their associated data. 
                  This action is permanent and cannot be undone.
                </p>
                <div className="modal-actions">
                  <button className="btn btn-ghost" style={{ width: 'auto' }} onClick={closeModal}>Cancel</button>
                  <button className="btn btn-danger" style={{ width: 'auto' }} onClick={handleBulkDelete}>Delete All Selected</button>
                </div>
              </>
            ) : modal.type === 'reset' ? (
              <form onSubmit={(e) => {
                e.preventDefault();
                handleResetPassword(modal.data._id, e.target.new_pass.value, e.target.confirm_pass.value);
              }}>
                <h2 className="modal-title">Reset Password</h2>
                <div style={{ marginBottom: '1.5rem' }}>
                  <p className="modal-description" style={{ marginBottom: '0.5rem' }}>
                    Set a new password for <b>{modal.data.first_name}</b>.
                  </p>
                  <ul style={{ paddingLeft: '1.25rem', fontSize: '0.8rem', margin: 0 }}>
                    <li style={{ color: passDraft.length >= 12 ? 'var(--success)' : 'var(--text-secondary)' }}>
                      At least 12 characters long
                    </li>
                    <li style={{ color: /[A-Z]/.test(passDraft) && /[a-z]/.test(passDraft) ? 'var(--success)' : 'var(--text-secondary)' }}>
                      Lowercase & Uppercase letters
                    </li>
                    <li style={{ color: /\d/.test(passDraft) && /[@$!%*?&]/.test(passDraft) ? 'var(--success)' : 'var(--text-secondary)' }}>
                      Numbers & Special characters (@$!%*?&)
                    </li>
                    <li style={{ color: passDraft && passDraft === confirmPassDraft ? 'var(--success)' : 'var(--text-secondary)' }}>
                      Passwords match
                    </li>
                  </ul>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' }}>
                  <div className="input-group">
                    <input 
                      name="new_pass" 
                      type="password" 
                      className="input-field" 
                      placeholder="New password"
                      required
                      autoFocus
                      value={passDraft}
                      onChange={(e) => setPassDraft(e.target.value)}
                    />
                  </div>
                  <div className="input-group">
                    <input 
                      name="confirm_pass" 
                      type="password" 
                      className="input-field" 
                      placeholder="Confirm new password"
                      required
                      value={confirmPassDraft}
                      onChange={(e) => setConfirmPassDraft(e.target.value)}
                    />
                  </div>
                </div>

                <div className="modal-actions">
                  <button type="button" className="btn btn-ghost" style={{ width: 'auto' }} onClick={closeModal}>Cancel</button>
                  <button 
                    type="submit" 
                    className="btn btn-primary" 
                    style={{ width: 'auto' }}
                    disabled={
                      passDraft.length < 12 || 
                      !/[A-Z]/.test(passDraft) || 
                      !/[a-z]/.test(passDraft) || 
                      !/\d/.test(passDraft) || 
                      !/[@$!%*?&]/.test(passDraft) || 
                      passDraft !== confirmPassDraft
                    }
                  >
                    Update Password
                  </button>
                </div>
              </form>
            ) : (
              <>
                <h2 className="modal-title">{modal.type === 'success' ? 'Success' : 'Error'}</h2>
                <p className="modal-description">{modal.data.message}</p>
                <div className="modal-actions">
                  <button className="btn btn-primary" style={{ width: 'auto' }} onClick={closeModal}>Dismiss</button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default AdminUsersPage;
