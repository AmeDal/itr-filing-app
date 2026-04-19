import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const ThemeToggle = () => {
  const { theme, toggleTheme } = useAuth();

  return (
    <button
      onClick={toggleTheme}
      className="theme-toggle"
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      <div className={`theme-toggle-track ${theme}`}>
        <div className="theme-toggle-thumb">
          {theme === 'dark' ? (
            <Moon className="w-4 h-4 text-[#8b5cf6]" />
          ) : (
            <Sun className="w-4 h-4 text-[#f59e0b]" />
          )}
        </div>
      </div>
    </button>
  );
};

export default ThemeToggle;
