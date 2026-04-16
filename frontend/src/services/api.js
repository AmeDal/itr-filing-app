const API_BASE_URL = 'http://localhost:8000/api/v1';

export const apiService = {
  /**
   * Extract data from a document image
   * @param {File} file - The image file to process
   * @param {string} docType - 'PAN' or 'AADHAR'
   * @returns {Promise<Object>} - Extracted data
   */
  async extractDocument(file, docType = 'PAN') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);

    try {
      const response = await fetch(`${API_BASE_URL}/extract/document`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('We are unable to process your document at this time. Please try again later.');
      }

      return response.json();
    } catch (err) {
      if (err instanceof TypeError) {
        throw new Error('Network error. Please check your connection and try again.');
      }
      throw err;
    }
  },

  /**
   * Create a new taxpayer profile
   * @param {Object} data - Taxpayer data
   * @returns {Promise<Object>}
   */
  async createTaxpayer(data) {
    try {
      const response = await fetch(`${API_BASE_URL}/taxpayers/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('We are unable to process your request at this time. Please try again later.');
      }

      return response.json();
    } catch (err) {
      if (err instanceof TypeError) {
        throw new Error('Network error. Please check your connection and try again.');
      }
      throw err;
    }
  },

  /**
   * Link Aadhar to an existing PAN profile
   * @param {string} panNumber - The PAN number
   * @param {Object} data - Aadhar data
   * @returns {Promise<Object>}
   */
  async linkAadhar(panNumber, data) {
    try {
      const response = await fetch(`${API_BASE_URL}/taxpayers/${panNumber}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('We are unable to process your request at this time. Please try again later.');
      }

      return response.json();
    } catch (err) {
      if (err instanceof TypeError) {
        throw new Error('Network error. Please check your connection and try again.');
      }
      throw err;
    }
  }
};
