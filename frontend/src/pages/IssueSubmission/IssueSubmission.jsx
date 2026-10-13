import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { caseService } from '../../services/caseService';
import { TextInput } from '../../components/forms/TextInput';
import { FileUpload } from '../../components/forms/FileUpload';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';
import styles from './IssueSubmission.module.css';

/**
 * IssueSubmission Page
 * Form for clients to describe legal issues and upload documents.
 */
export function IssueSubmission({ user }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
  });
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');

  const validateForm = () => {
    const newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Case title is required';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Case description is required';
    } else if (formData.description.length < 50) {
      newErrors.description = 'Description must be at least 50 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const handleFileSelect = (files) => {
    setUploadedFiles((prev) => [...prev, ...files]);
  };

  const handleRemoveFile = (index) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGeneralError('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    try {
      // TODO: Handle file uploads to backend
      const caseData = {
        title: formData.title,
        description: formData.description,
        client_id: user?.user_id,
        documents: [], // Document IDs will be added after file upload
      };

      const response = await caseService.createCase(caseData);
      navigate(`/case/${response.case_id}`);
    } catch (error) {
      setGeneralError(error.message || 'Failed to submit case. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Submit Your Legal Issue</h1>
        <p>Describe your case and upload relevant documents for analysis</p>
      </div>

      <div className={styles.content}>
        <Card title="Case Information" className={styles.mainCard}>
          <form onSubmit={handleSubmit}>
            {generalError && <div className={styles.generalError}>{generalError}</div>}

            <TextInput
              label="Case Title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g., Employment Dispute with Former Employer"
              error={errors.title}
              required
            />

            <TextInput
              label="Case Description"
              name="description"
              type="textarea"
              value={formData.description}
              onChange={handleChange}
              placeholder="Provide detailed information about your legal issue. Include relevant dates, people involved, and any previous actions taken."
              error={errors.description}
              required
              rows={8}
            />

            <FileUpload
              label="Upload Supporting Documents"
              name="documents"
              onFileSelect={handleFileSelect}
              accept=".pdf,.doc,.docx,.txt"
              multiple={true}
            />

            {uploadedFiles.length > 0 && (
              <div className={styles.fileList}>
                <h4>Uploaded Documents ({uploadedFiles.length})</h4>
                <ul>
                  {uploadedFiles.map((file, index) => (
                    <li key={index} className={styles.fileItem}>
                      <span className={styles.fileName}>{file.name}</span>
                      <span className={styles.fileSize}>
                        ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                      <button
                        type="button"
                        className={styles.removeBtn}
                        onClick={() => handleRemoveFile(index)}
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className={styles.actions}>
              <Button
                type="button"
                variant="secondary"
                onClick={() => navigate(-1)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isLoading}
              >
                {isLoading ? 'Submitting...' : 'Submit Case'}
              </Button>
            </div>
          </form>
        </Card>

        <Card title="Tips for Best Results" className={styles.tipsCard}>
          <ul className={styles.tipsList}>
            <li>
              <strong>Be specific:</strong> Provide dates, names, and specific events
            </li>
            <li>
              <strong>Include documents:</strong> Contracts, emails, letters, etc. help with analysis
            </li>
            <li>
              <strong>Explain impact:</strong> Describe how this issue is affecting you
            </li>
            <li>
              <strong>Previous actions:</strong> Note any steps you've already taken
            </li>
            <li>
              <strong>What you want:</strong> Describe your desired outcome
            </li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
