// Success.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import formsStyles from '../styles/modules/forms.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';

// Expanded list of event types
const eventTypes = [
  "Music", "Festivals", "Hockey", "Outdoors", "Workshops", "Conferences", 
  "Exhibitions", "Community", "Theater", "Family", "Nightlife", "Wellness", 
  "Holiday", "Networking", "Gaming", "Film", "Pets", "Virtual", "Charity", 
  "Science", "Basketball", "Pottery", "Tennis", "Soccer", "Football", 
  "Fishing", "Hiking"
];

const Success = () => {
  const [formData, setFormData] = useState({
    eventTitle: "",
    eventDescription: "",
    eventLocation: "",
    eventDate: "",
    eventTime: "",
    eventType: "",
    price: "",
    contactInfo: "",
  });

  const [message, setMessage] = useState("");
  const navigate = useNavigate(); // Initialize navigate hook

  // Get the session ID from the URL query parameters
  const urlParams = new URLSearchParams(window.location.search);
  const sessionId = urlParams.get('session_id');

  useEffect(() => {
    if (sessionId) {
      setMessage("Payment Successful! Please fill out the event details below.");
    } else {
      setMessage("Payment Unsuccessful.");
    }
  }, [sessionId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Handle form submission (e.g., POST to your backend)
    navigate("/for-you");
  };

  return (
    <div className={layoutStyles.pageContainer}>
      {sessionId ? (
        <>
          <header className={layoutStyles.header}>
            <h2 className={layoutStyles.pageTitle}>
              Payment Successful! Add Event Details:
            </h2>
          </header>

          <form onSubmit={handleSubmit} className={formsStyles.eventForm}>
            <div className={formsStyles.formGroup}>
              <label className={formsStyles.label}>Event Title:</label>
              <input
                type="text"
                name="eventTitle"
                value={formData.eventTitle}
                onChange={handleChange}
                className={formsStyles.formInput}
                required
              />
            </div>

            <div className={formsStyles.formGroup}>
              <label className={formsStyles.label}>Event Description:</label>
              <textarea
                name="eventDescription"
                value={formData.eventDescription}
                onChange={handleChange}
                className={formsStyles.formInput}
                required
              />
            </div>

            <div className={formsStyles.formGroup}>
              <label className={formsStyles.label}>Location:</label>
              <input
                type="text"
                name="eventLocation"
                value={formData.eventLocation}
                onChange={handleChange}
                className={formsStyles.formInput}
                required
              />
            </div>

            <div className={formsStyles.formGroup}>
              <label className={formsStyles.label}>Date:</label>
              <input
                type="date"
                name="eventDate"
                value={formData.eventDate}
                onChange={handleChange}
                className={formsStyles.formInput}
                required
              />
            </div>

            <div className={formsStyles.formGroup}>
              <label className={formsStyles.label}>Time:</label>
              <input
                type="time"
                name="eventTime"
                value={formData.eventTime}
                onChange={handleChange}
                className={formsStyles.formInput}
                required
              />
            </div>

            {/* Replace the hardcoded options with a map over eventTypes */}
            <div className={formsStyles.formGroup}>
              <label className={formsStyles.label}>Event Type:</label>
              <select
                name="eventType"
                value={formData.eventType}
                onChange={handleChange}
                className={formsStyles.formSelect}
                required
              >
                <option value="">Select event type</option>
                {eventTypes.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div className={formsStyles.formGroup}>
              <label className={formsStyles.label}>Price (USD):</label>
              <input
                type="number"
                name="price"
                value={formData.price}
                onChange={handleChange}
                className={formsStyles.formInput}
                required
              />
            </div>

            <div className={formsStyles.formGroup}>
              <label className={formsStyles.label}>Contact Info (Phone number):</label>
              <input
                type="text"
                name="contactInfo"
                value={formData.contactInfo}
                onChange={handleChange}
                className={formsStyles.formInput}
                required
              />
            </div>

            <button type="submit" className={buttonStyles.formButton}>
              Submit Event
            </button>
          </form>
        </>
      ) : (
        <p className={formsStyles.message}>{message}</p>
      )}
    </div>
  );
};

export default Success;

