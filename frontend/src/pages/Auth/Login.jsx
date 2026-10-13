import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { TextInput } from '../../components/forms/TextInput';
import { Button } from '../../components/common/Button';
import styles from './Login.module.css';

/**
 * Login Page
 * User authentication form for existing users.
 */
export function Login() {
  const navigate = useNavigate();
  const authContext = useContext(AuthContext);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGeneralError('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    
    // HARDCODED TEST CREDENTIALS - For development/testing only
    const testCredentials = {
      email: 'test@example.com',
      password: 'password123'
    };

    // Check if using test credentials
    if (formData.email === testCredentials.email && formData.password === testCredentials.password) {
      try {
        // Create mock user object for testing
        const mockUser = {
          user_id: 'test-user-123',
          email: testCredentials.email,
          full_name: 'Test User',
          role: 'client',
          is_verified: true,
          created_at: new Date().toISOString()
        };

        // Create mock token (valid JWT-like structure)
        const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyLTEyMyIsInJvbGUiOiJjbGllbnQiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.test-signature';

        // Save token to localStorage
        localStorage.setItem('access_token', mockToken);
        localStorage.setItem('user', JSON.stringify(mockUser));

        // Update auth context
        authContext.setToken(mockToken);
        authContext.setUser(mockUser);
        
        // Redirect to dashboard
        setTimeout(() => {
          navigate('/dashboard');
        }, 300);
      } catch (error) {
        setGeneralError('Test login failed.');
      } finally {
        setIsLoading(false);
      }
    } else {
      // Show test credentials hint
      setGeneralError(`🧪 Test Mode Active - Use:\nEmail: test@example.com\nPassword: password123`);
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginCard}>
        <div className={styles.header}>
          <h1>JurisLink</h1>
          <p>Legal Aid Platform</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <h2>Login</h2>

          {generalError && <div className={styles.generalError}>{generalError}</div>}

          <div className={styles.testHint}>
            <p>🧪 Test Mode Active</p>
            <p>Email: <strong>test@example.com</strong></p>
            <p>Password: <strong>password123</strong></p>
          </div>

          <TextInput
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="you@example.com"
            error={errors.email}
            required
          />

          <TextInput
            label="Password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="••••••••"
            error={errors.password}
            required
          />

          <Button
            type="submit"
            disabled={isLoading}
            fullWidth
            size="lg"
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </Button>
        </form>

        <div className={styles.footer}>
          <p>
            Don't have an account?{' '}
            <Link to="/signup" className={styles.link}>
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
