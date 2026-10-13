import React, { useState, useEffect } from 'react';
import { healthService } from '../services/healthService';
import styles from './HealthIndicator.module.css';

/**
 * Health Indicator Component
 * Displays backend and database connection status.
 */
export function HealthIndicator() {
  const [status, setStatus] = useState({
    backend: 'checking',
    database: 'checking',
    error: null,
  });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await healthService.checkHealth();
        setStatus({
          backend: response.backend,
          database: response.database,
          error: null,
        });
      } catch (error) {
        setStatus({
          backend: 'disconnected',
          database: 'disconnected',
          error: error.message,
        });
      }
    };

    checkHealth();
    // Check health every 10 seconds
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
      case 'running':
        return 'green';
      case 'checking':
        return 'yellow';
      case 'disconnected':
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <div className={styles.indicator}>
      <div className={styles.title}>System Status</div>
      <div className={styles.items}>
        <div className={styles.item}>
          <span
            className={`${styles.dot} ${styles[`dot_${getStatusColor(status.backend)}`]}`}
          ></span>
          <span>Backend: {status.backend}</span>
        </div>
        <div className={styles.item}>
          <span
            className={`${styles.dot} ${styles[`dot_${getStatusColor(status.database)}`]}`}
          ></span>
          <span>Database: {status.database}</span>
        </div>
      </div>
      {status.error && <div className={styles.error}>{status.error}</div>}
    </div>
  );
}
