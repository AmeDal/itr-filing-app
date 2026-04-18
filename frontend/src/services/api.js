const API_BASE_URL = 'http://localhost:8000/api/v1';

export const apiService = {
  /**
   * Authenticate user via PAN and Mobile
   */
  async login(panNumber, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pan_number: panNumber.toUpperCase(),
          password: password
        }),
      });

      if (!response.ok) {
        if (response.status === 401) throw new Error('Invalid PAN or Password');
        throw new Error('Authentication failed. Please try again later.');
      }

      return await response.json();
    } catch (err) {
      if (err instanceof TypeError) throw new Error('Network error. Is the backend running?');
      throw err;
    }
  },

  /**
   * Create a new user profile
   */
  async signup(userData) {
    try {
      const response = await fetch(`${API_BASE_URL}/users/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || 'Signup failed. Please check your data.');
      }

      return response.json();
    } catch (err) {
      if (err instanceof TypeError) throw new Error('Network error. Is the backend running?');
      throw err;
    }
  },

  /**
   * Upload ITR documents for processing
   */
  async uploadDocuments(formData) {
    try {
      const response = await fetch(`${API_BASE_URL}/itr/upload`, {
        method: 'POST',
        body: formData, // No content-type header for FormData, browser sets it
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || 'Upload failed.');
      }

      return await response.json();
    } catch (err) {
      if (err instanceof TypeError) throw new Error('Network error. Is the backend running?');
      throw err;
    }
  },

  /**
   * Connect to real-time progress stream (SSE)
   */
  connectProgressStream(sessionId, onMessage, onError) {
    const eventSource = new EventSource(`${API_BASE_URL}/itr/progress/${sessionId}`);
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (err) {
        console.error("Failed to parse SSE message", err);
      }
    };

    eventSource.onerror = (err) => {
      onError(err);
      eventSource.close();
    };

    return eventSource;
  }
};
