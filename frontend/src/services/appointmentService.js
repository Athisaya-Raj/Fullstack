/**
 * Appointment Service
 * Wraps appointment API calls for appointment booking and management.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const appointmentService = {
  /**
   * Create a new appointment.
   * @param {Object} appointmentData - Appointment creation data
   * @returns {Promise<Object>} Created appointment
   */
  async createAppointment(appointmentData) {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/appointments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(appointmentData),
      });

      if (!response.ok) {
        throw new Error(`Appointment creation failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Appointment creation error:', error);
      throw error;
    }
  },

  /**
   * Get an appointment by ID.
   * @param {string} appointmentId - Appointment ID
   * @returns {Promise<Object>} Appointment data
   */
  async getAppointment(appointmentId) {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/appointments/${appointmentId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Appointment retrieval failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Appointment retrieval error:', error);
      throw error;
    }
  },

  /**
   * Get all appointments for a client.
   * @param {string} clientId - Client ID
   * @returns {Promise<Array>} List of appointments
   */
  async getClientAppointments(clientId) {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/appointments/client/${clientId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Appointments retrieval failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Appointments retrieval error:', error);
      throw error;
    }
  },

  /**
   * Update an appointment.
   * @param {string} appointmentId - Appointment ID
   * @param {Object} updates - Appointment updates
   * @returns {Promise<Object>} Updated appointment
   */
  async updateAppointment(appointmentId, updates) {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/appointments/${appointmentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`Appointment update failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Appointment update error:', error);
      throw error;
    }
  },
};
