import React, { useRef } from 'react';
import styles from './FileUpload.module.css';

/**
 * FileUpload Component
 * Reusable file upload input with drag-and-drop support.
 */
export function FileUpload({
  label,
  name,
  onFileSelect,
  accept = '.pdf,.doc,.docx',
  multiple = false,
  error,
  required = false,
  maxSizeGB = 10,
}) {
  const fileInputRef = useRef(null);
  const maxSizeBytes = maxSizeGB * 1024 * 1024 * 1024;

  const handleFileSelect = (files) => {
    const fileArray = Array.from(files);

    // Validate file sizes
    const oversized = fileArray.filter((file) => file.size > maxSizeBytes);
    if (oversized.length > 0) {
      alert(`Files too large (max ${maxSizeGB}GB): ${oversized.map((f) => f.name).join(', ')}`);
      return;
    }

    onFileSelect(fileArray);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    handleFileSelect(e.dataTransfer.files);
  };

  return (
    <div className={styles.field}>
      {label && (
        <label className={styles.label}>
          {label}
          {required && <span className={styles.required}>*</span>}
        </label>
      )}

      <div
        className={`${styles.dropZone} ${error ? styles.hasError : ''}`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        role="button"
        tabIndex={0}
      >
        <div className={styles.dropContent}>
          <div className={styles.icon}>📄</div>
          <p className={styles.text}>
            {multiple ? 'Drag files here or click to select' : 'Drag file here or click to select'}
          </p>
          <p className={styles.subtext}>
            {accept} • Max {maxSizeGB}GB
          </p>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          name={name}
          accept={accept}
          multiple={multiple}
          onChange={(e) => handleFileSelect(e.target.files)}
          className={styles.hiddenInput}
        />
      </div>

      {error && <div className={styles.errorMessage}>{error}</div>}
    </div>
  );
}
