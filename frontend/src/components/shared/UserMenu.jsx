import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { LogOut, User, Settings as SettingsIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const UserMenu = () => {
  const { user, logout, isAdmin } = useAuth();
  const [isOpen, setIsOpen] = React.useState(false);
  const navigate = useNavigate();

  if (!user) return null;

  return (
    <div className="user-menu-container">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="user-menu-trigger"
      >
        <div className="user-avatar">
          <User className="w-5 h-5" />
        </div>
        <div className="user-info">
          <p className="user-name">{user.first_name} {user.last_name}</p>
          <p className="user-role">{user.role}</p>
        </div>
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)}></div>
          <div className="dropdown-menu">
            {isAdmin && (
              <button
                onClick={() => { navigate('/admin/users'); setIsOpen(false); }}
                className="dropdown-action"
              >
                <SettingsIcon className="w-4 h-4 text-primary" />
                <span>Admin Console</span>
              </button>
            )}
            <button
              onClick={() => { logout(); setIsOpen(false); navigate('/'); }}
              className="dropdown-action dropdown-logout"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default UserMenu;
