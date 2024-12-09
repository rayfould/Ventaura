import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

// Import shared CSS modules
import styles from '../styles/modules/globalpage.module.css';
import EventCard from './EventCard.js'; 
import logo from '../assets/ventaura-logo-white.png'; 
import logoFull from '../assets/ventaura-logo-semi-full.png'; 

const eventTypes = [
  "Music", "Festivals", "Hockey", "Outdoors", "Workshops", "Conferences", 
  "Exhibitions", "Community", "Theater", "Family", "Nightlife", "Wellness", 
  "Holiday", "Networking", "Gaming", "Film", "Pets", "Virtual", 
  "Science", "Basketball", "Baseball", "Pottery", "Tennis", "Soccer", "Football", 
  "Fishing", "Hiking", "Food and Drink", "Other"
];

const GlobalPage = () => {
  const userId = localStorage.getItem("userId");
  const [city, setCity] = useState("");
  const [events, setEvents] = useState([]);
  const [message, setMessage] = useState("");
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(false);
  const [filters, setFilters] = useState({
    eventType: '',
    maxDistance: '',
    maxPrice: ''
  });
  const navigate = useNavigate();

  const handleCityChange = (e) => setCity(e.target.value);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => ({
      ...prevFilters,
      [name]: value
    }));
  };

  const handleEventTypeToggle = (type) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      eventType: prevFilters.eventType === type ? '' : type
    }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!city.trim()) {
      setMessage("Please enter a city name.");
      return;
    }
    try {
      const response = await axios.get(
        `http://localhost:5152/api/global-events/search`, 
        { 
          params: { 
            city, 
            userId, 
            eventType: filters.eventType, 
            maxDistance: filters.maxDistance, 
            maxPrice: filters.maxPrice 
          } 
        }
      );
      setEvents(response.data.events || []);
      setMessage(response.data.Message || "Events fetched successfully.");
    } catch (error) {
      setMessage("An error occurred while fetching events.");
    }
  };

  const handleManualLogout = async () => {
    if (!userId) {
      alert("No user ID found in local storage.");
      return;
    }
  
    try {
      const response = await axios.post(
        `http://localhost:5152/api/combined-events/logout?userId=${userId}`
      );
      localStorage.removeItem("userId");
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
    <div className={styles['page-container']}>

      {/* Header */}
      <header className={styles.header}>
        <div className={styles['location-container']}>
          <img src={logoFull} alt="Logo" className={styles['logo-header']} />
        </div>

        <button 
          className={styles['open-sidebar-right']} 
          onClick={() => setIsRightSidebarOpen(true)} 
          aria-label="Open Sidebar"
        >
          ☰
        </button>
      </header>

      {/* Main Content Area */}
      <main className={styles['main-content']}>

        {/* Search Form */}
        <form 
          onSubmit={handleSearch} 
          className={`${styles.searchForm} ${styles.formMarginTop}`}
        >
          <input 
            type="text" 
            value={city} 
            onChange={handleCityChange} 
            placeholder="Search for a city" 
            className={styles.formInput} 
            required 
          />
          <button type="submit" className={styles.button}>
            Search
          </button>
        </form>

        {/* Filter Section */}
        <div className={styles['filter-section']}>
          <h3>Filters</h3>

          <select 
            name="eventType" 
            value={filters.eventType} 
            onChange={handleFilterChange}
            className={styles.formInput}
          >
            <option value="">Select Event Type</option>
            {eventTypes.map((type) => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>

          <input 
            type="number" 
            name="maxDistance" 
            placeholder="Max Distance (km)" 
            value={filters.maxDistance} 
            onChange={handleFilterChange} 
            className={styles.formInput}
          />

          <input 
            type="number" 
            name="maxPrice" 
            placeholder="Max Price" 
            value={filters.maxPrice} 
            onChange={handleFilterChange} 
            className={styles.formInput}
          />
        </div>

        {message && <p className={styles.message}>{message}</p>}

        {/* Event Grid */}
        <div className={styles['event-grid']}>
          {events.map((event, index) => (
            <EventCard key={index} event={event} />
          ))}
        </div>
      </main>

      {/* Right Sidebar */}
      <div className={`${styles['sidebar-right']} ${isRightSidebarOpen ? styles.open : ''}`}>
        <button 
          className={styles['close-sidebar-right']} 
          onClick={() => setIsRightSidebarOpen(false)}
        >
          ×
        </button>

        <button 
          onClick={handleManualLogout} 
          className={styles['logout-button']}
        >
          Logout
        </button>

        <Link to="/for-you" className={styles['sidebar-link']}>
          For You
        </Link>
        <Link to="/global-page" className={styles['sidebar-link']}>
          Global
        </Link>
      </div>
    </div>
  );
};

export default GlobalPage;
