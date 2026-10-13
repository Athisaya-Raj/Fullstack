import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';

/**
 * ProtectedRoute Component
 * Wraps routes that require authentication and/or specific roles.
 * Redirects unauthorized users to login or unauthorized page.
 */
export function ProtectedRoute({
  requiredRoles,
  children,
}) {
  const authContext = useContext(AuthContext);

  // Check if still loading
  if (authContext?.isLoading) {
    return <div className="loading-screen">Loading...</div>;
  }

  // Check if user is logged in
  if (!authContext?.isLoggedIn || !authContext?.user) {
    return <Navigate to="/login" replace />;
  }

  // Check if user has required role
  if (requiredRoles && !requiredRoles.includes(authContext.user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
}
