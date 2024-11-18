import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useLocation, useNavigate } from "react-router-dom"; 
import axios from "axios";
import "../styles.css";

const GlobalPage = () => {
  const userId = localStorage.getItem("userId"); // Retrieve userId from localStorage or session
  const [city, setCity] = useState("");
  const [events, setEvents] = useState([]);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleCityChange = (e) => {
    setCity(e.target.value);
  };

  const handleSearch = async (e) => {
    e.preventDefault(); // Prevent page reload
    if (!city.trim()) {
      setMessage("Please enter a city name.");
      return;
    }

    try {
      const response = await axios.get(
        `http://localhost:5152/api/global-events/search`,
        { params: { city, userId } } // Pass the city and userId
      );
      setEvents(response.data.events || []);
      setMessage(response.data.Message || "Events fetched successfully.");
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data.Message || "Error fetching events.");
      } else {
        setMessage("An error occurred while fetching events.");
      }
    }
  };

  return (
    <div className="container">

      {/* Centered Buttons */}
      <div className="center-buttons-container">
        <button onClick={() => navigate('/for-you')} className="for-you-button">
            For You
        </button>
        <button onClick={() => navigate('/global-page')} className="global-page-button">
            Global Page
        </button>
     </div>

      {/* Content */}
      <h1>Global Events</h1>
      <p>Enter a city name to search for events happening there:</p>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="City Name"
          value={city}
          onChange={handleCityChange}
          className="form-input"
          required
        />
        <button type="submit" className="form-button">
          Search
        </button>
      </form>
      {message && <p className="message">{message}</p>}
      <div className="boxes-container">
        {events.map((event, index) => (
          <div className="box" key={index}>
            <h3>{event.title}</h3>
            <p>{event.description}</p>
            <p>
              <strong>Location:</strong> {event.location}
            </p>
            <p>
              <strong>Start:</strong>{" "}
              {event.start
                ? new Date(event.start).toLocaleString()
                : "N/A"}
            </p>
            <p>
              <strong>Source:</strong> {event.source}
            </p>
            <p>
              <strong>Type:</strong> {event.type}
            </p>
            <p>
              <strong>Price:</strong>{" "}
              {event.currencyCode && event.amount
                ? `${event.currencyCode} ${event.amount}`
                : "Free"}
            </p>
            <p>
              <strong>Distance:</strong>{" "}
              {event.distance ? `${event.distance.toFixed(2)} km` : "N/A"}
            </p>
            <a
              href={event.url}
              target="_blank"
              rel="noopener noreferrer"
              className="event-link"
            >
              View More
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GlobalPage;

