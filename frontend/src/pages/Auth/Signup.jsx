import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { TextInput } from '../../components/forms/TextInput';
import { Button } from '../../components/common/Button';
import styles from './Signup.module.css';

/**
 * Signup Page
 * User registration form for new users.
 */
export function Signup() {
  const navigate = useNavigate();
  const authContext = useContext(AuthContext);
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    password: '',
    confirmPassword: '',
    role: 'client',
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');

  const validateForm = () => {
    const newErrors = {};

    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
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

    try {
      // If user tries to signup with test email/password, create mock account
      if (formData.email === testCredentials.email && formData.password === testCredentials.password) {
        // Simulate successful signup by storing test user
        const mockUser = {
          user_id: 'test-user-123',
          email: formData.email,
          full_name: formData.full_name,
          role: formData.role,
          is_verified: true,
          created_at: new Date().toISOString()
        };

        // Store in localStorage for persistence
        localStorage.setItem('test_user_' + formData.email, JSON.stringify(mockUser));

        // Show success message
        setGeneralError('');
        
        // Redirect to login after successful signup
        setTimeout(() => {
          navigate('/login');
        }, 500);
      } else {
        // For other emails, show test credentials hint
        setGeneralError(`🧪 Test Mode Active\n\nTo test signup, use:\nEmail: ${testCredentials.email}\nPassword: ${testCredentials.password}`);
      }
    } catch (error) {
      setGeneralError(error.message || 'Signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.signupContainer}>
      <div className={styles.signupCard}>
        <div className={styles.header}>
          <h1>JurisLink</h1>
          <p>Legal Aid Platform</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <h2>Create Account</h2>

          {generalError && <div className={styles.generalError}>{generalError}</div>}

          <div className={styles.testHint}>
            <p>🧪 Test Mode Active</p>
            <p>Email: <strong>test@example.com</strong></p>
            <p>Password: <strong>password123</strong></p>
          </div>

          <TextInput
            label="Full Name"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            placeholder="John Doe"
            error={errors.full_name}
            required
          />

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

          <div className={styles.roleSelector}>
            <label className={styles.roleLabel}>I am a...</label>
            <div className={styles.roleOptions}>
              <label className={styles.radioLabel}>
                <input
                  type="radio"
                  name="role"
                  value="client"
                  checked={formData.role === 'client'}
                  onChange={handleChange}
                />
                Client seeking legal aid
              </label>
              <label className={styles.radioLabel}>
                <input
                  type="radio"
                  name="role"
                  value="lawyer"
                  checked={formData.role === 'lawyer'}
                  onChange={handleChange}
                />
                Lawyer offering services
              </label>
            </div>
          </div>

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

          <TextInput
            label="Confirm Password"
            name="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={handleChange}
            placeholder="••••••••"
            error={errors.confirmPassword}
            required
          />

          <Button
            type="submit"
            disabled={isLoading}
            fullWidth
            size="lg"
          >
            {isLoading ? 'Creating account...' : 'Sign Up'}
          </Button>
        </form>

        <div className={styles.footer}>
          <p>
            Already have an account?{' '}
            <Link to="/login" className={styles.link}>
              Login
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
