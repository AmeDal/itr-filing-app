import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { API_BASE_URL } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const login = async (pan, password) => {
    const formData = new URLSearchParams();
    formData.append('username', pan);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    setAccessToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    try {
      await fetch(`${API_BASE_URL}/users/logout`, { 
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${accessToken}`
        }
      });
    } catch (e) {
      console.error('Logout API failed', e);
    } finally {
      setAccessToken(null);
      setUser(null);
    }
  };

  const refreshAccessToken = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/users/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setAccessToken(data.access_token);
        // We might want to fetch user profile /me if needed
        const meRes = await fetch(`${API_BASE_URL}/users/me`, {
          headers: { 'Authorization': `Bearer ${data.access_token}` },
          credentials: 'include'
        });
        if (meRes.ok) {
          const userData = await meRes.json();
          setUser(userData);
        }
        return data.access_token;
      }
    } catch (e) {
      console.error('Refresh failed', e);
    }
    setAccessToken(null);
    setUser(null);
    return null;
  }, []);

  // Try silent refresh on mount
  useEffect(() => {
    const initAuth = async () => {
      await refreshAccessToken();
      setIsLoading(false);
    };
    initAuth();
  }, [refreshAccessToken]);

  const value = {
    user,
    accessToken,
    isAuthenticated: !!accessToken,
    isAdmin: user?.role === 'admin',
    login,
    logout,
    refreshAccessToken,
    isLoading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
