import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { caseService } from '../../services/caseService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import styles from './LawyerDashboard.module.css';

/**
 * LawyerDashboard Page
 * Dashboard for lawyers to manage assigned cases.
 */
export function LawyerDashboard({ user }) {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadCases = async () => {
      try {
        setIsLoading(true);
        setError('');
        // TODO: Implement lawyer-specific case retrieval
        // For now, fetch all cases (will be filtered by assigned_lawyer_id on backend)
        setCases([]);
      } catch (err) {
        setError('Failed to load cases. Please try again.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadCases();
  }, [user]);

  const stats = {
    assigned: cases.filter((c) => c.status === 'assigned').length,
    inProgress: cases.filter((c) => c.status === 'in_progress').length,
    completed: cases.filter((c) => c.status === 'completed').length,
  };

  return (
    <div className={styles.dashboard}>
      <div className={styles.header}>
        <h1>Welcome, {user?.full_name}</h1>
        <p>Manage your assigned cases and client consultations</p>
      </div>

      <div className={styles.statsGrid}>
        <Card className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{stats.assigned}</div>
            <div className={styles.statLabel}>Assigned Cases</div>
          </div>
        </Card>

        <Card className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{stats.inProgress}</div>
            <div className={styles.statLabel}>In Progress</div>
          </div>
        </Card>

        <Card className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{stats.completed}</div>
            <div className={styles.statLabel}>Completed</div>
          </div>
        </Card>
      </div>

      <Card title="My Cases">
        {isLoading ? (
          <div className={styles.centerContent}>
            <LoadingSpinner size="lg" />
          </div>
        ) : error ? (
          <div className={styles.errorMessage}>{error}</div>
        ) : cases.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No cases assigned yet. Check back soon!</p>
          </div>
        ) : (
          <div className={styles.caseList}>
            {cases.map((caseItem) => (
              <div key={caseItem.case_id} className={styles.caseRow}>
                <div className={styles.caseInfo}>
                  <h4>{caseItem.title}</h4>
                  <p className={styles.clientName}>
                    Client: {caseItem.client_name || 'Unknown'}
                  </p>
                  <p className={styles.description}>
                    {caseItem.description.substring(0, 150)}...
                  </p>
                </div>
                <div className={styles.caseAction}>
                  <StatusBadge status={caseItem.status} />
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => navigate(`/case/${caseItem.case_id}`)}
                  >
                    View & Update
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
