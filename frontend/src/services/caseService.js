/**
 * Case Service
 * Wraps case API calls for case management.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const caseService = {
  /**
   * Create a new case.
   * @param {Object} caseData - Case creation data
   * @returns {Promise<Object>} Created case
   */
  async createCase(caseData) {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/cases`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(caseData),
      });

      if (!response.ok) {
        throw new Error(`Case creation failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Case creation error:', error);
      throw error;
    }
  },

  /**
   * Get a case by ID.
   * @param {string} caseId - Case ID
   * @returns {Promise<Object>} Case data
   */
  async getCase(caseId) {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/cases/${caseId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Case retrieval failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Case retrieval error:', error);
      throw error;
    }
  },

  /**
   * Get all cases for a client.
   * @param {string} clientId - Client ID
   * @returns {Promise<Array>} List of cases
   */
  async getClientCases(clientId) {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/cases/client/${clientId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Cases retrieval failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Cases retrieval error:', error);
      throw error;
    }
  },

  /**
   * Update a case.
   * @param {string} caseId - Case ID
   * @param {Object} updates - Case updates
   * @returns {Promise<Object>} Updated case
   */
  async updateCase(caseId, updates) {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/cases/${caseId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`Case update failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Case update error:', error);
      throw error;
    }
  },
};
