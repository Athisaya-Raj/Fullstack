import React from 'react';
import styles from './TextInput.module.css';

/**
 * TextInput Component
 * Reusable text input field with label and error handling.
 */
export function TextInput({
  label,
  name,
  type = 'text',
  value,
  onChange,
  onBlur,
  placeholder,
  error,
  required = false,
  disabled = false,
  maxLength,
  rows,
}) {
  const isTextarea = type === 'textarea';
  const InputComponent = isTextarea ? 'textarea' : 'input';

  return (
    <div className={styles.field}>
      {label && (
        <label htmlFor={name} className={styles.label}>
          {label}
          {required && <span className={styles.required}>*</span>}
        </label>
      )}
      <InputComponent
        id={name}
        name={name}
        type={isTextarea ? undefined : type}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        placeholder={placeholder}
        disabled={disabled}
        maxLength={maxLength}
        rows={rows}
        className={`${styles.input} ${error ? styles.hasError : ''}`}
      />
      {error && <div className={styles.errorMessage}>{error}</div>}
    </div>
  );
}
