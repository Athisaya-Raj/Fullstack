import React from 'react';
import styles from './LoadingSpinner.module.css';

/**
 * LoadingSpinner Component
 * Shows a loading animation while data is being fetched.
 */
export function LoadingSpinner({ size = 'md', fullScreen = false }) {
  const content = (
    <div className={`${styles.spinner} ${styles[`size_${size}`]}`}>
      <div className={styles.dot1}></div>
      <div className={styles.dot2}></div>
      <div className={styles.dot3}></div>
    </div>
  );

  if (fullScreen) {
    return <div className={styles.fullScreen}>{content}</div>;
  }

  return content;
}
