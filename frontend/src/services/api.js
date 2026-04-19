import { fetchEventSource } from '@microsoft/fetch-event-source';

export const API_BASE_URL = 'http://localhost:8000/api/v1';

let accessToken = null;
let refreshCallback = null;

export const setApiAuth = (token, onRefresh) => {
  accessToken = token;
  refreshCallback = onRefresh;
};

const fetchWithAuth = async (url, options = {}) => {
  const headers = { ...options.headers };
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  const mergedOptions = {
    ...options,
    headers,
    credentials: 'include', // Ensure refresh cookie is sent
  };

  let response = await fetch(url, mergedOptions);

  if (response.status === 401 && refreshCallback) {
    // Attempt refresh
    const newToken = await refreshCallback();
    if (newToken) {
      accessToken = newToken;
      headers['Authorization'] = `Bearer ${accessToken}`;
      response = await fetch(url, { ...mergedOptions, headers });
    }
  }

  return response;
};

export const apiService = {
  async signup(userData) {
    const response = await fetch(`${API_BASE_URL}/users/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.detail || 'Signup failed');
    }
    return response.json();
  },

  async uploadDocuments(formData) {
    const response = await fetchWithAuth(`${API_BASE_URL}/itr/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.detail || 'Upload failed');
    }
    return response.json();
  },

  connectProgressStream(sessionId, onMessage, onError) {
    const ctrl = new AbortController();
    
    fetchEventSource(`${API_BASE_URL}/itr/progress/${sessionId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
      signal: ctrl.signal,
      async onopen(response) {
        if (!response.ok) {
          throw new Error('SSE connection failed');
        }
      },
      onmessage(msg) {
        if (msg.data) {
          try {
            onMessage(JSON.parse(msg.data));
          } catch (e) {
            console.error('SSE JSON error', e);
          }
        }
      },
      onerror(err) {
        onError(err);
        ctrl.abort();
      }
    });

    return () => ctrl.abort();
  },

  // Admin endpoints
  async listUsers(skip = 0, limit = 100) {
    const response = await fetchWithAuth(`${API_BASE_URL}/admin/users?skip=${skip}&limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch users');
    return response.json();
  },

  async deleteUser(userId) {
    const response = await fetchWithAuth(`${API_BASE_URL}/admin/users/${userId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Delete failed');
    return response.json();
  },

  async bulkDeleteUsers(userIds) {
    const response = await fetchWithAuth(`${API_BASE_URL}/admin/users/bulk-delete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_ids: userIds })
    });
    if (!response.ok) throw new Error('Bulk delete failed');
    return response.json();
  },

  async resetPassword(userId, newPassword) {
    const response = await fetchWithAuth(`${API_BASE_URL}/admin/users/${userId}/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_password: newPassword })
    });
    if (!response.ok) throw new Error('Password reset failed');
    return response.json();
  }
};
