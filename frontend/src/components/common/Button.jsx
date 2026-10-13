import React from 'react';
import styles from './Button.module.css';

/**
 * Button Component
 * Reusable button with variant support (primary, secondary, danger).
 */
export function Button({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  fullWidth = false,
  type = 'button',
  onClick,
  className = '',
}) {
  const combinedClassName = [
    styles.button,
    styles[`variant_${variant}`],
    styles[`size_${size}`],
    fullWidth ? styles.fullWidth : '',
    disabled ? styles.disabled : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      type={type}
      className={combinedClassName}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
