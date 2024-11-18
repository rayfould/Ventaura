import React, { useState, useEffect } from "react";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles.css"; // Import the global CSS

const ForYou = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { userId } = location.state || {};
  const [events, setEvents] = useState([]);
  const [message, setMessage] = useState("");

  // Timeout duration in milliseconds (30 minutes)
  const TIMEOUT_DURATION = 30 * 60 * 1000;

  useEffect(() => {
    if (!userId) {
      setMessage("No user ID found. Please log in first.");
      return;
    }

    const fetchEvents = async () => {
      try {
        const response = await axios.get(
          `http://localhost:5152/api/combined-events/fetch?userId=${userId}`
        );
        setMessage(response.data.Message);
        setEvents(response.data.insertedEvents || []);
      } catch (error) {
        if (error.response) {
          setMessage(error.response.data || "Error fetching events.");
        } else {
          setMessage("An error occurred while fetching events.");
        }
      }
    };

    fetchEvents();

    // Setup inactivity logout
    let timeout;

    const resetTimeout = () => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        handleAutoLogout();
      }, TIMEOUT_DURATION);
    };

    const handleAutoLogout = async () => {
      try {
        await axios.post(
          `http://localhost:5152/api/combined-events/logout?userId=${userId}`
        );
        navigate("/login");
      } catch (error) {
        console.error("Error logging out due to inactivity:", error);
      }
    };

    const handleActivity = () => {
      resetTimeout();
    };

    // Add event listeners for user activity
    window.addEventListener("mousemove", handleActivity);
    window.addEventListener("keypress", handleActivity);
    window.addEventListener("click", handleActivity);

    resetTimeout();

    return () => {
      clearTimeout(timeout);
      window.removeEventListener("mousemove", handleActivity);
      window.removeEventListener("keypress", handleActivity);
      window.removeEventListener("click", handleActivity);
    };
  }, [userId, navigate]);

  const handleManualLogout = async () => {
    try {
      const response = await axios.post(
        `http://localhost:5152/api/combined-events/logout?userId=${userId}`
      );
      alert(response.data.Message);
      navigate("/login");
    } catch (error) {
      if (error.response) {
        alert(error.response.data.Message || "Error logging out.");
      } else {
        alert("An error occurred while logging out.");
      }
    }
  };

  return (
    <div>
      <header className="header">
        <button
          className="logout-button"
          onClick={handleManualLogout}
        >
          Logout
        </button>
        <h1>For You</h1>
      </header>

      <div className="sidebar">
        <button
          className="open-sidebar"
          onClick={() => {
            // Logic for opening a sidebar, if any
          }}
        >
          ☰
        </button>
      </div>

      <div className="home-container">
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
    </div>
  );
};

export default ForYou;
