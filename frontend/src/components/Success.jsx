// Success.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import formsStyles from '../styles/modules/forms.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import '../styles/variables.module.css';


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
    // Here you can handle form submission to add the event to the database
    // For now, we'll just redirect to the /for-you page
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
                <option value="Festival-Fairs">Festival/Fair</option>
                <option value="Music">Music</option>
                <option value="Performing-Arts">Performing Arts</option>
                <option value="Sports-Active-Life">Sports/Active Life</option>
                <option value="Nightlife">Nightlife</option>
                <option value="Film">Film</option>
                <option value="Kids-Family">Kids/Family</option>
                <option value="Food-And-Drink">Food And Drink</option>
                <option value="Other">Other</option>
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
