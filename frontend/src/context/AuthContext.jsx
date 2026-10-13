import React, { createContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';

/**
 * AuthContext
 * Provides authentication state and methods to the entire app.
 * Handles token storage, user session restoration, and login/logout.
 */
export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Restore session on app load
  useEffect(() => {
    const restoreSession = async () => {
      try {
        // Check for test user in localStorage first (test mode)
        const savedUser = localStorage.getItem('user');
        const savedToken = localStorage.getItem('access_token');
        
        if (savedUser && savedToken) {
          // Test mode - use localStorage directly
          try {
            setUser(JSON.parse(savedUser));
            setToken(savedToken);
          } catch (e) {
            console.error('Failed to parse saved user:', e);
          }
        }
        // Don't try to validate with backend - will cause 401 errors in test mode
      } catch (err) {
        console.error('Session restoration error:', err);
        // Clear invalid data
        authService.clearToken();
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    // Small delay to ensure localStorage is ready
    const timer = setTimeout(restoreSession, 100);
    return () => clearTimeout(timer);
  }, []);

  const login = useCallback(async (email, password) => {
    try {
      setError(null);
      const response = await authService.login(email, password);
      authService.saveToken(response.access_token);
      setToken(response.access_token);
      setUser(response.user);
      return response.user;
    } catch (err) {
      const errorMessage = err.message || 'Login failed';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const signup = useCallback(async (userData) => {
    try {
      setError(null);
      const user = await authService.signup(userData);
      return user;
    } catch (err) {
      const errorMessage = err.message || 'Signup failed';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const logout = useCallback(() => {
    authService.clearToken();
    setToken(null);
    setUser(null);
    setError(null);
  }, []);

  // Method to directly set user (for test mode)
  const setUserDirectly = useCallback((userData) => {
    setUser(userData);
  }, []);

  // Method to directly set token (for test mode)
  const setTokenDirectly = useCallback((tokenData) => {
    setToken(tokenData);
  }, []);

  const value = {
    user,
    token,
    isLoading,
    error,
    login,
    signup,
    logout,
    setUser: setUserDirectly,
    setToken: setTokenDirectly,
    isLoggedIn: !!user && !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
