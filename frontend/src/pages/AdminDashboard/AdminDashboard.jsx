import React, { useState, useEffect } from 'react';
import { Card } from '../../components/common/Card';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import styles from './AdminDashboard.module.css';

/**
 * AdminDashboard Page
 * Administrative dashboard for system overview, case management, and analytics.
 */
export function AdminDashboard({ user }) {
  const [stats, setStats] = useState({
    totalCases: 0,
    totalClients: 0,
    totalLawyers: 0,
    openCases: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadStats = async () => {
      try {
        setIsLoading(true);
        setError('');
        // TODO: Implement admin stats API endpoint
        // For now, set placeholder values
        setStats({
          totalCases: 0,
          totalClients: 0,
          totalLawyers: 0,
          openCases: 0,
        });
      } catch (err) {
        setError('Failed to load statistics. Please try again.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadStats();
  }, []);

  return (
    <div className={styles.dashboard}>
      <div className={styles.header}>
        <h1>Admin Dashboard</h1>
        <p>System overview and management</p>
      </div>

      {error && <div className={styles.errorMessage}>{error}</div>}

      <div className={styles.statsGrid}>
        <Card className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{stats.totalCases}</div>
            <div className={styles.statLabel}>Total Cases</div>
          </div>
        </Card>

        <Card className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{stats.totalClients}</div>
            <div className={styles.statLabel}>Clients</div>
          </div>
        </Card>

        <Card className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{stats.totalLawyers}</div>
            <div className={styles.statLabel}>Lawyers</div>
          </div>
        </Card>

        <Card className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{stats.openCases}</div>
            <div className={styles.statLabel}>Open Cases</div>
          </div>
        </Card>
      </div>

      <div className={styles.contentGrid}>
        <Card title="Case Overview" className={styles.halfWidth}>
          {isLoading ? (
            <div className={styles.centerContent}>
              <LoadingSpinner size="md" />
            </div>
          ) : (
            <p>Case analytics and trends will appear here.</p>
          )}
        </Card>

        <Card title="Lawyer Assignment" className={styles.halfWidth}>
          {isLoading ? (
            <div className={styles.centerContent}>
              <LoadingSpinner size="md" />
            </div>
          ) : (
            <p>Assign cases to lawyers and manage assignments.</p>
          )}
        </Card>
      </div>

      <Card title="System Notifications">
        <div className={styles.notificationsList}>
          <p>No new notifications</p>
        </div>
      </Card>
    </div>
  );
}
