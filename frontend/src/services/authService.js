/**
 * Auth Service
 * Wraps authentication API calls for user registration and login.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const authService = {
  /**
   * Register a new user.
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} User response data
   */
  async signup(userData) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        throw new Error(`Signup failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  },

  /**
   * Login a user.
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<Object>} Token and user data
   */
  async login(email, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error(`Login failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  /**
   * Get current logged-in user (used for session restoration).
   * @returns {Promise<Object>} Current user data
   */
  async getCurrentUser() {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No token found');
      }

      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to get user: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  },

  /**
   * Save token to localStorage.
   * @param {string} token - Access token
   */
  saveToken(token) {
    localStorage.setItem('access_token', token);
  },

  /**
   * Get token from localStorage.
   * @returns {string|null} Access token or null
   */
  getToken() {
    return localStorage.getItem('access_token');
  },

  /**
   * Clear token from localStorage.
   */
  clearToken() {
    localStorage.removeItem('access_token');
  },
};
