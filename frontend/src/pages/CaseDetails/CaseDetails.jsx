import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { caseService } from '../../services/caseService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import styles from './CaseDetails.module.css';

/**
 * CaseDetails Page
 * Displays full case information including classification, summary, and status.
 */
export function CaseDetails() {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadCase = async () => {
      try {
        setIsLoading(true);
        setError('');
        const data = await caseService.getCase(caseId);
        setCaseData(data);
      } catch (err) {
        setError('Failed to load case details. Please try again.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadCase();
  }, [caseId]);

  if (isLoading) {
    return (
      <div className={styles.container}>
        <LoadingSpinner fullScreen size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.errorContainer}>
          <div className={styles.errorMessage}>{error}</div>
          <Button onClick={() => navigate(-1)}>Go Back</Button>
        </div>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className={styles.container}>
        <div className={styles.errorContainer}>
          <div className={styles.errorMessage}>Case not found</div>
          <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1>{caseData.title}</h1>
          <div className={styles.headerMeta}>
            <span>Case ID: {caseData.case_id}</span>
            <span>
              Created: {new Date(caseData.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
        <StatusBadge status={caseData.status} />
      </div>

      <div className={styles.content}>
        <div className={styles.mainContent}>
          <Card title="Case Description">
            <p className={styles.description}>{caseData.description}</p>
          </Card>

          <Card title="Classification" subtitle="Issue type detected by AI">
            <div className={styles.classificationResult}>
              {caseData.issue_type ? (
                <>
                  <div className={styles.issueType}>{caseData.issue_type}</div>
                  <p>Category automatically identified from your case description.</p>
                </>
              ) : (
                <p className={styles.pending}>Classification in progress...</p>
              )}
            </div>
          </Card>

          <Card title="Summary" subtitle="AI-generated document summary">
            <div className={styles.summaryContent}>
              <p>
                {caseData.summary ||
                  'Summary will be available once documents are analyzed.'}
              </p>
              {caseData.key_phrases && caseData.key_phrases.length > 0 && (
                <div className={styles.keyPhrases}>
                  <h4>Key Phrases</h4>
                  <div className={styles.phraseList}>
                    {caseData.key_phrases.map((phrase, index) => (
                      <span key={index} className={styles.phrase}>
                        {phrase}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Card>

          <Card title="Status Timeline">
            <div className={styles.timeline}>
              <div className={styles.timelineItem}>
                <span className={styles.timelineMark}>✓</span>
                <div>
                  <strong>Case Created</strong>
                  <p>{new Date(caseData.created_at).toLocaleString()}</p>
                </div>
              </div>

              {caseData.status !== 'open' && (
                <div className={styles.timelineItem}>
                  <span className={styles.timelineMark}>✓</span>
                  <div>
                    <strong>Status Updated</strong>
                    <p>
                      {new Date(caseData.updated_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              )}

              {caseData.assigned_lawyer_id && (
                <div className={styles.timelineItem}>
                  <span className={styles.timelineMark}>✓</span>
                  <div>
                    <strong>Lawyer Assigned</strong>
                    <p>A lawyer has been assigned to your case</p>
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>

        <div className={styles.sidebar}>
          <Card title="Case Status">
            <div className={styles.statusDetail}>
              <StatusBadge status={caseData.status} />
              <p className={styles.statusDescription}>
                {getStatusDescription(caseData.status)}
              </p>
            </div>
          </Card>

          <Card title="Assigned Lawyer">
            {caseData.assigned_lawyer_id ? (
              <div className={styles.lawyerInfo}>
                <p>A lawyer has been assigned to your case.</p>
                <Button
                  variant="primary"
                  fullWidth
                  onClick={() => navigate(`/appointments`)}
                >
                  Book Consultation
                </Button>
              </div>
            ) : (
              <p className={styles.pending}>
                Awaiting lawyer assignment. We'll notify you as soon as one is assigned.
              </p>
            )}
          </Card>

          <Card title="Actions">
            <div className={styles.actions}>
              <Button variant="secondary" fullWidth onClick={() => navigate(-1)}>
                Go Back
              </Button>
              <Button
                variant="secondary"
                fullWidth
                onClick={() => navigate(`/case/${caseId}/edit`)}
              >
                Edit Case
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function getStatusDescription(status) {
  const descriptions = {
    open: 'Your case has been submitted and is awaiting review.',
    assigned: 'A lawyer has been assigned to your case.',
    in_progress: 'Your case is currently being worked on.',
    completed: 'Your case has been completed.',
    closed: 'Your case is closed.',
  };
  return descriptions[status] || 'Unknown status';
}
