import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Navbar.module.css';

/**
 * Navbar Component
 * Top navigation bar with branding, user menu, and logout.
 */
export function Navbar({ user, onLogout }) {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  const getRoleDisplay = (role) => {
    const roleMap = {
      client: 'Client',
      lawyer: 'Lawyer',
      admin: 'Admin'
    };
    return roleMap[role] || role;
  };

  return (
    <nav className={styles.navbar}>
      <div className={styles.navbarContainer}>
        <div className={styles.logo}>
          <h1 onClick={() => navigate('/dashboard')}>JurisLink</h1>
        </div>

        <div className={styles.userSection}>
          {user && (
            <div className={styles.userMenu}>
              <button
                className={styles.userButton}
                onClick={() => setMenuOpen(!menuOpen)}
              >
                <span className={styles.userName}>{user.full_name}</span>
                <span className={styles.userRole}>{getRoleDisplay(user.role)}</span>
                <span className={styles.menuToggle}>▼</span>
              </button>

              {menuOpen && (
                <div className={styles.dropdown}>
                  <button
                    className={styles.dropdownItem}
                    onClick={() => {
                      navigate('/profile');
                      setMenuOpen(false);
                    }}
                  >
                    Profile
                  </button>
                  <button
                    className={styles.dropdownItem}
                    onClick={() => {
                      handleLogout();
                      setMenuOpen(false);
                    }}
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
