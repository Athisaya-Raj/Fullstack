import React, { useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext, AuthProvider } from './context/AuthContext';
import { Navbar } from './components/layout/Navbar';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { Login } from './pages/Auth/Login';
import { Signup } from './pages/Auth/Signup';
import { ClientDashboard } from './pages/ClientDashboard/ClientDashboard';
import { IssueSubmission } from './pages/IssueSubmission/IssueSubmission';
import { CaseDetails } from './pages/CaseDetails/CaseDetails';
import { CaseTracker } from './pages/CaseTracker/CaseTracker';
import { AppointmentBooking } from './pages/AppointmentBooking/AppointmentBooking';
import { LawyerDashboard } from './pages/LawyerDashboard/LawyerDashboard';
import { AdminDashboard } from './pages/AdminDashboard/AdminDashboard';
import './App.css';

/**
 * App Routes Component
 * Contains all routing logic.
 */
function AppRoutes() {
  const authContext = useContext(AuthContext);

  if (authContext?.isLoading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <BrowserRouter>
      <div className="app-container">
        {authContext?.isLoggedIn && authContext?.user && (
          <Navbar user={authContext.user} onLogout={authContext.logout} />
        )}

        <main className="app-main">
          <Routes>
            {/* Public Routes */}
            <Route
              path="/login"
              element={
                authContext?.isLoggedIn ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Login />
                )
              }
            />
            <Route
              path="/signup"
              element={
                authContext?.isLoggedIn ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Signup />
                )
              }
            />

            {/* Client Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute requiredRoles={['client', 'lawyer', 'admin']}>
                  {authContext?.user?.role === 'client' && (
                    <ClientDashboard user={authContext.user} />
                  )}
                  {authContext?.user?.role === 'lawyer' && (
                    <LawyerDashboard user={authContext.user} />
                  )}
                  {authContext?.user?.role === 'admin' && (
                    <AdminDashboard user={authContext.user} />
                  )}
                </ProtectedRoute>
              }
            />
            <Route
              path="/issue-submission"
              element={
                <ProtectedRoute requiredRoles={['client']}>
                  <IssueSubmission user={authContext?.user} />
                </ProtectedRoute>
              }
            />
            <Route
              path="/case/:caseId"
              element={
                <ProtectedRoute requiredRoles={['client', 'lawyer', 'admin']}>
                  <CaseDetails />
                </ProtectedRoute>
              }
            />
            <Route
              path="/cases"
              element={
                <ProtectedRoute requiredRoles={['client']}>
                  <CaseTracker user={authContext?.user} />
                </ProtectedRoute>
              }
            />
            <Route
              path="/appointments"
              element={
                <ProtectedRoute requiredRoles={['client', 'lawyer']}>
                  <AppointmentBooking user={authContext?.user} />
                </ProtectedRoute>
              }
            />

            {/* Lawyer Routes */}
            <Route
              path="/lawyer/dashboard"
              element={
                <ProtectedRoute requiredRoles={['lawyer']}>
                  <LawyerDashboard user={authContext?.user} />
                </ProtectedRoute>
              }
            />

            {/* Admin Routes */}
            <Route
              path="/admin/dashboard"
              element={
                <ProtectedRoute requiredRoles={['admin']}>
                  <AdminDashboard user={authContext?.user} />
                </ProtectedRoute>
              }
            />

            {/* Unauthorized */}
            <Route
              path="/unauthorized"
              element={
                <div className="error-container">
                  <h1>Access Denied</h1>
                  <p>You do not have permission to access this page.</p>
                  <a href="/dashboard">Go to Dashboard</a>
                </div>
              }
            />

            {/* Catch-all redirect */}
            <Route
              path="/"
              element={
                <Navigate
                  to={authContext?.isLoggedIn ? '/dashboard' : '/login'}
                  replace
                />
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        {!authContext?.isLoggedIn && (
          <footer className="app-footer">
            <p>&copy; 2024 JurisLink. An academic project for legal aid.</p>
          </footer>
        )}
      </div>
    </BrowserRouter>
  );
}

/**
 * Main App Component
 * Wraps routes with AuthProvider for authentication context.
 */
function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}

export default App;
