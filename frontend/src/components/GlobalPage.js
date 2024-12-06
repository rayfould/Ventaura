import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import styles from '../styles';

const GlobalPage = () => {
  const userId = localStorage.getItem("userId");
  const [city, setCity] = useState("");
  const [events, setEvents] = useState([]);
  const [message, setMessage] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();

  const handleCityChange = (e) => {
    setCity(e.target.value);
  };

  const handleSearch = async (e) => {
    if (!userId) {
      setMessage("User is not logged in.");
      navigate("/login");
      return;
    }

    e.preventDefault();
    if (!city.trim()) {
      setMessage("Please enter a city name.");
      return;
    }

    try {
      const response = await axios.get(
        `http://localhost:5152/api/global-events/search`,
        { params: { city, userId } }
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

  const handleManualLogout = async () => {
    try {
      await axios.post(
        `http://localhost:5152/api/combined-events/logout?userId=${userId}`
      );

      localStorage.removeItem("userId");
      alert("Logged out successfully.");
      navigate("/login");
    } catch (error) {
      alert("An error occurred while logging out.");
    }
  };

  return (
    <div className={styles.pageContainer}>
      {/* Header */}
      <header className={styles.header}>
        <button
          className={styles.sidebarButton}
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        >
          ☰
        </button>
        {/* Settings Icon Button */}
        <button
          className={styles.settingsButton}
          onClick={() => navigate("/settings")}
        >
          ⚙️
        </button>
      </header>

      {/* Sidebar */}
      <div className={`${styles.sidebar} ${isSidebarOpen ? styles.open : ''}`}>
        <button 
          className={styles.closeSidebar} 
          onClick={() => setIsSidebarOpen(false)}
        >
          X
        </button>
        <Link to="/for-you" className={styles.sidebarLink}>
          For You
        </Link>
        <Link to="/about-us" className={styles.sidebarLink}>
          About Us
        </Link>
        <Link to="/contact-us" className={styles.sidebarLink}>
          Contact Us
        </Link>
        <Link to="/post-event-page" className={styles.sidebarLink}>
          Post An Event
        </Link>
        <Link className={styles.sidebarLink} onClick={handleManualLogout}>
          Logout
        </Link>
      </div>

      {/* Centered Buttons */}
      <div className={styles.centerButtonsContainer}>
        <button onClick={() => navigate('/for-you')} className={styles.forYouButton}>
          For You
        </button>
        <button onClick={() => navigate('/global-page')} className={styles.globalPageButton}>
          Global Page
        </button>
      </div>

      {/* Main Content */}
      <div className={styles.homeContainer}>
        <h1 className={styles.heading}>Global Events</h1>
        <p className={styles.text}>Enter a city name to search for events happening there:</p>
        <form onSubmit={handleSearch} className={styles.searchForm}>
          <input
            type="text"
            placeholder="City Name"
            value={city}
            onChange={handleCityChange}
            className={styles.formInput}
            required
          />
          <button type="submit" className={styles.formButton}>
            Search
          </button>
        </form>
        {message && <p className={styles.message}>{message}</p>}
        <div className={styles.boxesContainer}>
          {events.map((event, index) => (
            <div className={styles.box} key={index}>
              <h3 className={styles.boxTitle}>{event.title}</h3>
              <p className={styles.boxDescription}>{event.description}</p>
              <p className={styles.boxDetail}>
                <strong>Location:</strong> {event.location}
              </p>
              <p className={styles.boxDetail}>
                <strong>Start:</strong> {event.start ? new Date(event.start).toLocaleString() : "N/A"}
              </p>
              <p className={styles.boxDetail}>
                <strong>Source:</strong> {event.source}
              </p>
              <p className={styles.boxDetail}>
                <strong>Type:</strong> {event.type}
              </p>
              <p className={styles.boxDetail}>
                <strong>Price:</strong> {event.currencyCode && event.amount ? `${event.currencyCode} ${event.amount}` : "Free"}
              </p>
              <p className={styles.boxDetail}>
                <strong>Distance:</strong> {event.distance ? `${event.distance.toFixed(2)} km` : "N/A"}
              </p>
              <a
                href={event.url}
                target="_blank"
                rel="noopener noreferrer"
                className={styles.eventLink}
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