import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles.css"; // Import the global CSS
import { useNavigate } from "react-router-dom"; // Import useNavigate hook

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
    navigate("/for-you"); // Redirect to the /for-you page
  };

  return (
    <div className="add-event-container">
      {sessionId ? (
        <>
          <header className="header">
            <h2 className="page-title">Payment Successful, Add Event Details:</h2>
          </header>

          <form onSubmit={handleSubmit} className="event-form">
            <div className="form-group">
              <label>Event Title:</label>
              <input
                type="text"
                name="eventTitle"
                value={formData.eventTitle}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>

            <div className="form-group">
              <label>Event Description:</label>
              <textarea
                name="eventDescription"
                value={formData.eventDescription}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>

            <div className="form-group">
              <label>Location:</label>
              <input
                type="text"
                name="eventLocation"
                value={formData.eventLocation}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>

            <div className="form-group">
              <label>Date:</label>
              <input
                type="date"
                name="eventDate"
                value={formData.eventDate}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>

            <div className="form-group">
              <label>Time:</label>
              <input
                type="time"
                name="eventTime"
                value={formData.eventTime}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>

            <div className="form-group">
              <label>Event Type:</label>
              <select
                name="eventType"
                value={formData.eventType}
                onChange={handleChange}
                className="form-input"
                required
              >
                <option value="">Select event type</option>
                <option value="festival">Festival</option>
                <option value="concert">Concert</option>
                <option value="conference">Conference</option>
                <option value="workshop">Workshop</option>
              </select>
            </div>

            <div className="form-group">
              <label>Price (USD):</label>
              <input
                type="number"
                name="price"
                value={formData.price}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>

            <div className="form-group">
              <label>Contact Info (Phone number):</label>
              <input
                type="text"
                name="contactInfo"
                value={formData.contactInfo}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>

            <button type="submit" className="form-button">
              Submit Event
            </button>
          </form>
        </>
      ) : (
        <p className="message">{message}</p>
      )}
    </div>
  );
};

export default Success;
