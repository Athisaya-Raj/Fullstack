import React from 'react';
import styles from './StatusBadge.module.css';

/**
 * StatusBadge Component
 * Displays case status with color-coded styling.
 */
export function StatusBadge({ status, className = '' }) {
  const getStatusColor = (status) => {
    const statusMap = {
      open: 'blue',
      assigned: 'purple',
      in_progress: 'orange',
      completed: 'green',
      closed: 'gray',
      cancelled: 'red',
    };
    return statusMap[status] || 'gray';
  };

  const getStatusLabel = (status) => {
    const labelMap = {
      open: 'Open',
      assigned: 'Assigned',
      in_progress: 'In Progress',
      completed: 'Completed',
      closed: 'Closed',
      cancelled: 'Cancelled',
    };
    return labelMap[status] || status;
  };

  const color = getStatusColor(status);
  const label = getStatusLabel(status);

  return (
    <span className={`${styles.badge} ${styles[`color_${color}`]} ${className}`}>
      {label}
    </span>
  );
}
