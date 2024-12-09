// Success.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import postEventStyles from '../styles//modules/postevent.module.css'; // New PostEvent-specific styles

// Expanded list of event types
const eventTypes = [
  "Music", "Festivals", "Hockey", "Outdoors", "Workshops", "Conferences", 
  "Exhibitions", "Community", "Theater", "Family", "Nightlife", "Wellness", 
  "Holiday", "Networking", "Gaming", "Film", "Pets", "Virtual", 
  "Science", "Basketball", "Baseball", "Pottery", "Tennis", "Soccer", "Football", 
  "Fishing", "Hiking", "Food and Drink", "Lectures", "Fashion", "Motorsports", "Dance", "Comedy", "Other"
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
  const navigate = useNavigate();

  // Get the session ID from the URL query parameters
  const urlParams = new URLSearchParams(window.location.search);
  const sessionId = urlParams.get('session_id');

  useEffect(() => {
    if (sessionId) {
      setMessage("Payment Successful! Please add event details.");
    } else {
      setMessage("Payment Unsuccessful.");
    }
  }, [sessionId]);

  // Load Google Places API for Autocomplete
  useEffect(() => {
    if (!window.google) {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyAMyuR3lvyF98orSC-z8SyIEdekVsguXWs&libraries=places`;
      script.async = true;
      script.defer = true;
      document.body.appendChild(script);
      script.onload = () => initializeAutocomplete();
    } else {
      initializeAutocomplete();
    }
  }, []);

  const initializeAutocomplete = () => {
    const input = document.querySelector('input[name="eventLocation"]');
    if (input) {
      const autocomplete = new window.google.maps.places.Autocomplete(input, {
        types: ['geocode'] // Restrict the suggestions to addresses only
      });

      autocomplete.addListener('place_changed', () => {
        const place = autocomplete.getPlace();
        if (place && place.formatted_address) {
          setFormData((prevData) => ({
            ...prevData,
            eventLocation: place.formatted_address
          }));
        }
      });
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission

    // Extract date and time from form data
    const date = formData.eventDate; // "2024-12-08"
    const time = formData.eventTime; // "00:49"

    // Combine into an ISO 8601 string
    // Append 'T' to separate date and time, and 'Z' for UTC if necessary
    formData.start = `${date}T${time}:00.000Z`;

    try {
      // Prepare the payload
      const payload = {
        Title: formData.eventTitle,
        Description: formData.eventDescription,
        Location: formData.eventLocation,
        Start: new Date(formData.start).toISOString(),
        Source: "Host",
        Type: formData.eventType,
        CurrencyCode: "USD", // or as needed
        Amount: parseFloat(formData.price),
        URL: formData.contactInfo, // Verify if this is the intended use
        HostUserId: 1 // Add logic to set the HostUserId
      };
      

      // Send the POST request
      const response = await fetch('http://localhost:5152/api/combined-events/create-host-event', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      // Check for response status
      if (!response.ok) {
        if (response.status === 409) {
          console.error("Conflict error: An event with this title already exists for this host.");
          alert("An event with this title already exists for this host.");
        } else if (response.status === 400) {
          console.error("Bad request: Validation failed.");
          alert("Validation failed. Please check your input.");
        } else {
          console.error("Unexpected error occurred.");
          alert("An unexpected error occurred. Please try again later.");
        }
        return;
      }

      const result = await response.json();
      console.log("Host event created successfully:", result);
      alert("Host event created successfully!");
    } catch (error) {
      console.error("An error occurred while creating the event:", error);
      alert("An error occurred while creating the event.");
    }
    navigate("/for-you"); // Redirect to the /for-you page
  };

  return (
    <div className={layoutStyles['page-container']}>
      {sessionId ? (
        <>
          <header className={layoutStyles.header}>
            <h1 className={layoutStyles['header-title']}>
              Event Details:
            </h1>
          </header>

          <form onSubmit={handleSubmit} className={postEventStyles['post-event-form']}>
            <div className={postEventStyles['form-group']}>
              <label className={postEventStyles['label']}>Event Title:</label>
              <input
                type="text"
                name="eventTitle"
                value={formData.eventTitle}
                onChange={handleChange}
                className={postEventStyles['form-input']}
                required
              />
            </div>

            <div className={postEventStyles['form-group']}>
              <label className={postEventStyles['label']}>Event Description:</label>
              <textarea
                name="eventDescription"
                value={formData.eventDescription}
                onChange={handleChange}
                className={postEventStyles['form-input']}
                required
              />
            </div>

            <div className={postEventStyles['form-group']}>
              <label className={postEventStyles['label']}>Location:</label>
              <input
                type="text"
                name="eventLocation"
                value={formData.eventLocation}
                onChange={handleChange}
                className={postEventStyles['form-input']}
                required
              />
            </div>

            <div className={postEventStyles['form-group']}>
              <label className={postEventStyles['label']}>Date:</label>
              <input
                type="date"
                name="eventDate"
                value={formData.eventDate}
                onChange={handleChange}
                className={postEventStyles['form-input']}
                required
              />
            </div>

            <div className={postEventStyles['form-group']}>
              <label className={postEventStyles['label']}>Time:</label>
              <input
                type="time"
                name="eventTime"
                value={formData.eventTime}
                onChange={handleChange}
                className={postEventStyles['form-input']}
                required
              />
            </div>

            <div className={postEventStyles['form-group']}>
              <label className={postEventStyles['label']}>Event Type:</label>
              <select
                name="eventType"
                value={formData.eventType}
                onChange={handleChange}
                className={postEventStyles['form-select']}
                required
              >
                <option value="">Select event type</option>
                {eventTypes.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div className={postEventStyles['form-group']}>
              <label className={postEventStyles['label']}>Price (USD):</label>
              <input
                type="number"
                name="price"
                value={formData.price}
                onChange={handleChange}
                className={postEventStyles['form-input']}
                required
              />
            </div>

            <div className={postEventStyles['form-group']}>
              <label className={postEventStyles['label']}>Contact Info (Phone number):</label>
              <input
                type="text"
                name="contactInfo"
                value={formData.contactInfo}
                onChange={handleChange}
                className={postEventStyles['form-input']}
                required
              />
            </div>

            <button type="submit" className={postEventStyles['submit-button']}>
              Submit Event
            </button>
          </form>
        </>
      ) : (
        <p className={postEventStyles['message']}>{message}</p>
      )}
    </div>
  );
};

export default Success;
