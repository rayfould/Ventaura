// GlobalPage.js
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

// Import shared CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';
import formsStyles from '../styles/modules/forms.module.css';
import '../styles/variables.module.css';


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
    <div className={layoutStyles.pageContainer}>
      {/* Header */}
      <header className={layoutStyles.header}>
        <button
          className={buttonStyles.sidebarButton}
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        >
          ☰
        </button>
        {/* Settings Icon Button */}
        <button
          className={buttonStyles.settingsButton}
          onClick={() => navigate("/settings")}
        >
          ⚙️
        </button>
      </header>

      {/* Sidebar */}
      <div className={`${navigationStyles.sidebar} ${isSidebarOpen ? navigationStyles.open : ''}`}>
        <button 
          className={buttonStyles.closeSidebar} 
          onClick={() => setIsSidebarOpen(false)}
        >
          X
        </button>
        <Link to="/for-you" className={navigationStyles.sidebarLink}>
          For You
        </Link>
        <Link to="/about-us" className={navigationStyles.sidebarLink}>
          About Us
        </Link>
        <Link to="/contact-us" className={navigationStyles.sidebarLink}>
          Contact Us
        </Link>
        <Link to="/post-event-page" className={navigationStyles.sidebarLink}>
          Post An Event
        </Link>
        <button 
          onClick={handleManualLogout} 
          className={navigationStyles.sidebarLink}
        >
          Logout
        </button>
      </div>

      {/* Centered Buttons */}
      <div className={layoutStyles.centerButtonsContainer}>
        <button 
          onClick={() => navigate('/for-you')} 
          className={buttonStyles.forYouButton}
        >
          For You
        </button>
        <button 
          onClick={() => navigate('/global-page')} 
          className={buttonStyles.globalPageButton}
        >
          Global Page
        </button>
      </div>

      {/* Main Content */}
      <div className={layoutStyles.homeContainer}>
        <h1 className={layoutStyles.heading}>Global Events</h1>
        <p className={layoutStyles.text}>Enter a city name to search for events happening there:</p>
        <form onSubmit={handleSearch} className={formsStyles.searchForm}>
          <input
            type="text"
            placeholder="City Name"
            value={city}
            onChange={handleCityChange}
            className={buttonStyles.formInput} // Assuming formInput is defined in buttons.module.css
            required
          />
          <button type="submit" className={buttonStyles.formButton}>
            Search
          </button>
        </form>
        {message && <p className={layoutStyles.message}>{message}</p>}
        <div className={layoutStyles.eventGrid}>
          {events.map((event, index) => (
            <div className={layoutStyles.box} key={index}>
              <h3 className={layoutStyles.boxTitle}>{event.title}</h3>
              <p className={layoutStyles.boxDescription}>{event.description}</p>
              <p className={layoutStyles.boxDetail}>
                <strong>Location:</strong> {event.location}
              </p>
              <p className={layoutStyles.boxDetail}>
                <strong>Start:</strong> {event.start ? new Date(event.start).toLocaleString() : "N/A"}
              </p>
              <p className={layoutStyles.boxDetail}>
                <strong>Source:</strong> {event.source}
              </p>
              <p className={layoutStyles.boxDetail}>
                <strong>Type:</strong> {event.type}
              </p>
              <p className={layoutStyles.boxDetail}>
                <strong>Price:</strong> {event.currencyCode && event.amount ? `${event.currencyCode} ${event.amount}` : "Free"}
              </p>
              <p className={layoutStyles.boxDetail}>
                <strong>Distance:</strong> {event.distance ? `${event.distance.toFixed(2)} km` : "N/A"}
              </p>
              <a
                href={event.url}
                target="_blank"
                rel="noopener noreferrer"
                className={buttonStyles.eventLink} // Assuming eventLink is defined in buttons.module.css
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
