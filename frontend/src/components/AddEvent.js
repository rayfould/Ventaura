import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles.css'; // Ensure to import global CSS

const AddEvent = () => {
  const history = useNavigate();

  // Initialize state for each form field
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: '',
    date: '',
    time: '',
    eventType: '',
    price: '',
    contact: ''
  });

  const [errors, setErrors] = useState({});

  // Get the current date in YYYY-MM-DD format
  const currentDate = new Date().toISOString().split('T')[0];

  // Handle form data changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  // Handle form submission and validate inputs
  const handleSubmit = (e) => {
    e.preventDefault();

    // Validate the form data
    const newErrors = {};
    if (!formData.title) newErrors.title = 'Event title is required';
    if (formData.description.length < 50) newErrors.description = 'Event description must be at least 50 characters';
    if (!formData.location) newErrors.location = 'Location is required';
    if (!formData.date) newErrors.date = 'Event date is required';
    if (new Date(formData.date) <= new Date(currentDate)) newErrors.date = 'Event date must be in the future';
    if (!formData.time) newErrors.time = 'Event time is required';
    if (!formData.eventType) newErrors.eventType = 'Event type is required';
    if (!formData.price || isNaN(formData.price) || formData.price <= 0) newErrors.price = 'Price must be a positive number';
    
    // Validate the contact info (phone number)
    if (!formData.contact || !/^\d{10}$/.test(formData.contact)) {
      newErrors.contact = 'Please enter a valid phone number (10 digits)';
    }

    // If there are errors, display them
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
    } else {
      // If no errors, proceed to the next page (e.g., Event Confirmation page)
      history.push('/next-page');  // Replace '/next-page' with your actual route
    }
  };

  // Determine if the form is valid
  const isFormValid = Object.keys(errors).length === 0 &&
    formData.title && 
    formData.description && 
    formData.location && 
    formData.date && 
    formData.time && 
    formData.eventType && 
    formData.price && 
    formData.contact && 
    /^\d{10}$/.test(formData.contact); // Ensure the phone number is valid

  return (
    <div className="add-event-container">
      <header className="header">
        <h2 className="page-title">Add New Event</h2>
      </header>

      <form onSubmit={handleSubmit} className="event-form">
        <div className="form-group">
          <label>Event Title:</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className="form-input"
            required
          />
          {errors.title && <p className="error-message">{errors.title}</p>}
        </div>

        <div className="form-group">
          <label>Event Description:</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            className="form-input"
            required
          />
          {errors.description && <p className="error-message">{errors.description}</p>}
        </div>

        <div className="form-group">
          <label>Location:</label>
          <input
            type="text"
            name="location"
            value={formData.location}
            onChange={handleChange}
            className="form-input"
            required
          />
          {errors.location && <p className="error-message">{errors.location}</p>}
        </div>

        <div className="form-group">
          <label>Date:</label>
          <input
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            className="form-input"
            required
            min={currentDate}  // Prevent selecting past dates
          />
          {errors.date && <p className="error-message">{errors.date}</p>}
        </div>

        <div className="form-group">
          <label>Time:</label>
          <input
            type="time"
            name="time"
            value={formData.time}
            onChange={handleChange}
            className="form-input"
            required
          />
          {errors.time && <p className="error-message">{errors.time}</p>}
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
            <option value="fishing">Fishing</option>
            <option value="museum">Museum</option>
            <option value="escape_room">Escape Room</option>
          </select>
          {errors.eventType && <p className="error-message">{errors.eventType}</p>}
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
          {errors.price && <p className="error-message">{errors.price}</p>}
        </div>

        <div className="form-group">
          <label>Contact Info (Phone number):</label>
          <input
            type="text"
            name="contact"
            value={formData.contact}
            onChange={handleChange}
            className="form-input"
            required
          />
          {errors.contact && <p className="error-message">{errors.contact}</p>}
        </div>

        {/* Submit Button - only enabled if the form is valid */}
        <form action="http://localhost:5152/api/create-checkout-session" method="POST">
          <button 
            type="submit" 
            role="link" 
            className="submit-button" 
            disabled={!isFormValid}
          >
            Submit Event
          </button>
        </form>
      </form>
    </div>
  );
};

export default AddEvent;
