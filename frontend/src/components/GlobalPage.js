import React, { useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom"; // Import Link for navigation
import "../styles.css";

const GlobalPage = () => {
  const [city, setCity] = useState("");
  const [events, setEvents] = useState([]);
  const [message, setMessage] = useState("");

  const handleCityChange = (e) => {
    setCity(e.target.value);
  };

  const handleSearch = async () => {
    if (!city.trim()) {
      setMessage("Please enter a city name.");
      return;
    }

    try {
      const response = await axios.get(
        `http://localhost:5152/api/global-events/search`,
        { params: { city } }
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
    <div>
      <header className="header">
        <Link to="/for-you" className="global-link">
          For You
        </Link>
        <h1 className="page-title">Global Events</h1>
      </header>
      <div className="container">
        <h2>Search Events by City</h2>
        <p>Enter a city name to find events and activities happening there.</p>
        <div className="form">
          <input
            type="text"
            name="city"
            placeholder="Enter city name"
            value={city}
            onChange={handleCityChange}
            className="form-input"
          />
          <button onClick={handleSearch} className="form-button">
            Search
          </button>
        </div>
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
                {event.start ? new Date(event.start).toLocaleString() : "N/A"}
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
    </div>
  );
};

export default GlobalPage;
