/**
 * Health Service
 * Wraps health check API calls for backend connectivity verification.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const healthService = {
  /**
   * Check backend and database health status.
   * @returns {Promise<Object>} Health status object
   */
  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  },
};
