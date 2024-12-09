import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';
import globalPageStyles from '../styles/modules/globalpage.module.css';
import EventCard from './EventCard.js'; 
import logoFull from '../assets/ventaura-logo-semi-full.png'; 

const eventTypes = [
  "Music", "Festivals", "Hockey", "Outdoors", "Workshops", "Conferences", 
  "Exhibitions", "Community", "Theater", "Family", "Nightlife", "Wellness", 
  "Holiday", "Networking", "Gaming", "Film", "Pets", "Virtual", 
  "Science", "Basketball", "Baseball", "Pottery", "Tennis", "Soccer", "Football", 
  "Fishing", "Hiking", "Food and Drink", "Pottery", "Other"
];

const GlobalPage = () => {
  const navigate = useNavigate();
  const [userId, setUserId] = useState(localStorage.getItem("userId"));
  const [city, setCity] = useState("");
  const [events, setEvents] = useState([]);
  const [message, setMessage] = useState("");
  const [showHeader, setShowHeader] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [filters, setFilters] = useState({
    eventType: '',
    maxDistance: '',
    maxPrice: ''
  });

  // Handle input changes for city name
  const handleCityChange = (e) => setCity(e.target.value);

  // Handle filter changes
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => ({
      ...prevFilters,
      [name]: value
    }));
  };

  // Handle the search button click
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

  // Handle clear filters
  const handleClearFilters = () => {
    setFilters({
      eventType: '',
      maxDistance: '',
      maxPrice: ''
    });
  };

  // Handle scroll to hide/show header
  const handleScroll = () => {
    if (typeof window !== 'undefined') {
      const currentScrollY = window.scrollY;
      setShowHeader(currentScrollY <= lastScrollY || currentScrollY < 100);
      setLastScrollY(currentScrollY);
    }
  };

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.addEventListener('scroll', handleScroll);
      return () => window.removeEventListener('scroll', handleScroll);
    }
  }, [lastScrollY]);

  return (
    <div className={globalPageStyles['page-container']}>

      {/* Header */}
      <header 
        className={`${layoutStyles.header} ${!showHeader ? layoutStyles.hidden : ''}`}
      >
        <div className={layoutStyles['logo-container']}>
          <img src={logoFull} alt="Logo" className={navigationStyles['logo-header']} />
        </div>

        <div className={layoutStyles['center-buttons-container']}>
          <button 
            onClick={() => navigate('/for-you')} 
            className={`${buttonStyles['button-56']}`}
          >
            For You
          </button>
          <button 
            onClick={() => navigate('/global-page')} 
            className={`${buttonStyles['button-56']}`}
          >
            Global
          </button>
        </div>
      </header>

      {/* Main layout container */}
      <div className={globalPageStyles['page-container']}>
        <main className={globalPageStyles['search-container']}>

          <form onSubmit={handleSearch} className={globalPageStyles['search-form']}>
            <input 
              type="text" 
              value={city} 
              onChange={handleCityChange} 
              placeholder="Search for a city" 
              className={globalPageStyles['form-input']} 
              required 
            />

            <select 
              name="eventType" 
              value={filters.eventType} 
              onChange={handleFilterChange}
              className={globalPageStyles['form-input']}
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
              className={globalPageStyles['form-input']} 
            />

            <input 
              type="number" 
              name="maxPrice" 
              placeholder="Max Price ($)" 
              value={filters.maxPrice} 
              onChange={handleFilterChange} 
              className={globalPageStyles['form-input']} 
            />

            <div className={globalPageStyles['button-container']}>
              <button type="submit" className={`${buttonStyles.button}`}>
                Search
              </button>
              <button 
                type="button" 
                onClick={handleClearFilters} 
                className={`${buttonStyles.button} ${buttonStyles['clear-filters-button']}`}
              >
                Clear Filters
              </button>
            </div>
          </form>

          {message && <p className={layoutStyles.message}>{message}</p>}

          <div className={layoutStyles['event-grid']}>
            {events.map((event, index) => (
              <EventCard key={index} event={event} />
            ))}
          </div>
        </main>
      </div>
    </div>
  );
};

export default GlobalPage;
