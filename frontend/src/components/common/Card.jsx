import React from 'react';
import styles from './Card.module.css';

/**
 * Card Component
 * Reusable container for content with consistent styling.
 */
export function Card({ children, title, subtitle, className = '' }) {
  return (
    <div className={`${styles.card} ${className}`}>
      {title && (
        <div className={styles.header}>
          <h3 className={styles.title}>{title}</h3>
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        </div>
      )}
      <div className={styles.content}>{children}</div>
    </div>
  );
}
