import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { caseService } from '../../services/caseService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import styles from './ClientDashboard.module.css';

/**
 * ClientDashboard Page
 * Main dashboard for clients showing recent cases and quick actions.
 */
export function ClientDashboard({ user }) {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadCases = async () => {
      try {
        setIsLoading(true);
        setError('');
        if (user?.user_id) {
          const clientCases = await caseService.getClientCases(user.user_id);
          setCases(clientCases);
        }
      } catch (err) {
        setError('Failed to load cases. Please try again.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadCases();
  }, [user]);

  const handleNewCase = () => {
    navigate('/issue-submission');
  };

  const handleViewCase = (caseId) => {
    navigate(`/case/${caseId}`);
  };

  const recentCases = cases.slice(0, 5);

  return (
    <div className={styles.dashboard}>
      <div className={styles.header}>
        <h1>Welcome, {user?.full_name}</h1>
        <p>Manage your legal cases and track progress</p>
      </div>

      <div className={styles.quickActions}>
        <Card
          title="New Legal Issue"
          subtitle="Submit a new case"
          className={styles.actionCard}
        >
          <p>Describe your legal issue and upload relevant documents for analysis.</p>
          <Button variant="primary" fullWidth onClick={handleNewCase}>
            Submit New Case
          </Button>
        </Card>

        <Card
          title="My Cases"
          subtitle={`${cases.length} total`}
          className={styles.actionCard}
        >
          <p>View and manage all your legal cases.</p>
          <Button
            variant="secondary"
            fullWidth
            onClick={() => navigate('/cases')}
          >
            View All Cases
          </Button>
        </Card>

        <Card
          title="Appointments"
          subtitle="Schedule consultations"
          className={styles.actionCard}
        >
          <p>Book appointments with your assigned lawyer.</p>
          <Button
            variant="secondary"
            fullWidth
            onClick={() => navigate('/appointments')}
          >
            Manage Appointments
          </Button>
        </Card>
      </div>

      <Card title="Recent Cases" className={styles.recentCases}>
        {isLoading ? (
          <div className={styles.centerContent}>
            <LoadingSpinner size="lg" />
          </div>
        ) : error ? (
          <div className={styles.errorMessage}>{error}</div>
        ) : recentCases.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No cases yet. Start by submitting a new legal issue.</p>
            <Button variant="primary" onClick={handleNewCase}>
              Submit Your First Case
            </Button>
          </div>
        ) : (
          <div className={styles.caseList}>
            {recentCases.map((caseItem) => (
              <div key={caseItem.case_id} className={styles.caseRow}>
                <div className={styles.caseInfo}>
                  <h4>{caseItem.title}</h4>
                  <p>{caseItem.description.substring(0, 100)}...</p>
                  <div className={styles.caseMeta}>
                    <span>Issue: {caseItem.issue_type || 'Pending classification'}</span>
                    <span>Created: {new Date(caseItem.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className={styles.caseAction}>
                  <StatusBadge status={caseItem.status} />
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleViewCase(caseItem.case_id)}
                  >
                    View
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
