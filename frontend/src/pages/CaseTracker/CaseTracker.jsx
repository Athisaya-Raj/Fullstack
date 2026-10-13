import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { caseService } from '../../services/caseService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import styles from './CaseTracker.module.css';

/**
 * CaseTracker Page
 * Displays all client cases with status pipeline and filtering.
 */
export function CaseTracker({ user }) {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

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

  const filteredCases =
    filterStatus === 'all' ? cases : cases.filter((c) => c.status === filterStatus);

  const statusGroups = {
    open: cases.filter((c) => c.status === 'open').length,
    assigned: cases.filter((c) => c.status === 'assigned').length,
    in_progress: cases.filter((c) => c.status === 'in_progress').length,
    completed: cases.filter((c) => c.status === 'completed').length,
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>My Cases</h1>
        <p>Track all your legal cases through their lifecycle</p>
      </div>

      <div className={styles.statusPipeline}>
        <div
          className={`${styles.pipelineItem} ${
            filterStatus === 'all' ? styles.active : ''
          }`}
          onClick={() => setFilterStatus('all')}
        >
          <div className={styles.pipelineCount}>{cases.length}</div>
          <div className={styles.pipelineLabel}>All Cases</div>
        </div>

        <div
          className={`${styles.pipelineItem} ${
            filterStatus === 'open' ? styles.active : ''
          }`}
          onClick={() => setFilterStatus('open')}
        >
          <div className={styles.pipelineCount}>{statusGroups.open}</div>
          <div className={styles.pipelineLabel}>Open</div>
        </div>

        <div
          className={`${styles.pipelineItem} ${
            filterStatus === 'assigned' ? styles.active : ''
          }`}
          onClick={() => setFilterStatus('assigned')}
        >
          <div className={styles.pipelineCount}>{statusGroups.assigned}</div>
          <div className={styles.pipelineLabel}>Assigned</div>
        </div>

        <div
          className={`${styles.pipelineItem} ${
            filterStatus === 'in_progress' ? styles.active : ''
          }`}
          onClick={() => setFilterStatus('in_progress')}
        >
          <div className={styles.pipelineCount}>{statusGroups.in_progress}</div>
          <div className={styles.pipelineLabel}>In Progress</div>
        </div>

        <div
          className={`${styles.pipelineItem} ${
            filterStatus === 'completed' ? styles.active : ''
          }`}
          onClick={() => setFilterStatus('completed')}
        >
          <div className={styles.pipelineCount}>{statusGroups.completed}</div>
          <div className={styles.pipelineLabel}>Completed</div>
        </div>
      </div>

      <Card title={`Cases (${filteredCases.length})`}>
        {isLoading ? (
          <div className={styles.centerContent}>
            <LoadingSpinner size="lg" />
          </div>
        ) : error ? (
          <div className={styles.errorMessage}>{error}</div>
        ) : filteredCases.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No cases in this category yet.</p>
            <Button variant="primary" onClick={() => navigate('/issue-submission')}>
              Submit Your First Case
            </Button>
          </div>
        ) : (
          <div className={styles.caseGrid}>
            {filteredCases.map((caseItem) => (
              <div key={caseItem.case_id} className={styles.caseCard}>
                <div className={styles.cardHeader}>
                  <h3>{caseItem.title}</h3>
                  <StatusBadge status={caseItem.status} />
                </div>

                <p className={styles.description}>
                  {caseItem.description.substring(0, 150)}...
                </p>

                <div className={styles.cardMeta}>
                  {caseItem.issue_type && (
                    <span className={styles.issueType}>{caseItem.issue_type}</span>
                  )}
                  <span className={styles.date}>
                    {new Date(caseItem.created_at).toLocaleDateString()}
                  </span>
                </div>

                <Button
                  variant="secondary"
                  fullWidth
                  onClick={() => navigate(`/case/${caseItem.case_id}`)}
                >
                  View Details
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
