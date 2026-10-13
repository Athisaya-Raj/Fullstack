import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { appointmentService } from '../../services/appointmentService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { TextInput } from '../../components/forms/TextInput';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import styles from './AppointmentBooking.module.css';

/**
 * AppointmentBooking Page
 * Allows clients to book appointments with assigned lawyers.
 */
export function AppointmentBooking({ user }) {
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showBookingForm, setShowBookingForm] = useState(false);
  const [formData, setFormData] = useState({
    appointment_date: '',
    notes: '',
  });
  const [formErrors, setFormErrors] = useState({});

  useEffect(() => {
    const loadAppointments = async () => {
      try {
        setIsLoading(true);
        setError('');
        if (user?.user_id) {
          const clientAppointments = await appointmentService.getClientAppointments(
            user.user_id
          );
          setAppointments(clientAppointments);
        }
      } catch (err) {
        setError('Failed to load appointments. Please try again.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadAppointments();
  }, [user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (formErrors[name]) {
      setFormErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validateForm = () => {
    const errors = {};
    if (!formData.appointment_date) {
      errors.appointment_date = 'Please select a date and time';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      const appointmentData = {
        appointment_date: new Date(formData.appointment_date).toISOString(),
        client_id: user?.user_id,
        lawyer_id: 'placeholder', // TODO: Get from case assignment
        case_id: 'placeholder', // TODO: Get from context
        notes: formData.notes,
      };

      await appointmentService.createAppointment(appointmentData);
      setShowBookingForm(false);
      setFormData({ appointment_date: '', notes: '' });
      // Reload appointments
      const updated = await appointmentService.getClientAppointments(user.user_id);
      setAppointments(updated);
    } catch (err) {
      setError('Failed to book appointment. Please try again.');
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Appointments</h1>
        <p>Schedule and manage your consultations with lawyers</p>
      </div>

      <div className={styles.content}>
        <Card title="My Appointments" subtitle={`${appointments.length} total`}>
          {isLoading ? (
            <div className={styles.centerContent}>
              <LoadingSpinner size="lg" />
            </div>
          ) : error ? (
            <div className={styles.errorMessage}>{error}</div>
          ) : appointments.length === 0 ? (
            <div className={styles.emptyState}>
              <p>No appointments scheduled yet.</p>
              <Button variant="primary" onClick={() => setShowBookingForm(true)}>
                Book an Appointment
              </Button>
            </div>
          ) : (
            <div className={styles.appointmentList}>
              {appointments.map((apt) => (
                <div key={apt.appointment_id} className={styles.appointmentItem}>
                  <div className={styles.appointmentTime}>
                    <div className={styles.date}>
                      {new Date(apt.appointment_date).toLocaleDateString()}
                    </div>
                    <div className={styles.time}>
                      {new Date(apt.appointment_date).toLocaleTimeString()}
                    </div>
                  </div>
                  <div className={styles.appointmentDetails}>
                    <h4>Consultation with Lawyer</h4>
                    {apt.notes && <p>{apt.notes}</p>}
                    <div className={styles.status}>Status: {apt.status}</div>
                  </div>
                  <div className={styles.appointmentActions}>
                    <Button variant="secondary" size="sm">
                      Reschedule
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {showBookingForm && (
          <Card title="Book New Appointment">
            <form onSubmit={handleSubmit}>
              <TextInput
                label="Date & Time"
                name="appointment_date"
                type="datetime-local"
                value={formData.appointment_date}
                onChange={handleChange}
                error={formErrors.appointment_date}
                required
              />

              <TextInput
                label="Notes (Optional)"
                name="notes"
                type="textarea"
                value={formData.notes}
                onChange={handleChange}
                placeholder="Any specific topics you'd like to discuss..."
                rows={4}
              />

              <div className={styles.formActions}>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowBookingForm(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary">
                  Book Appointment
                </Button>
              </div>
            </form>
          </Card>
        )}
      </div>
    </div>
  );
}
