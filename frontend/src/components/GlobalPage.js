// GlobalPage.js

import React, { useState, useEffect } from "react";
import { Link, useNavigate, NavLink } from "react-router-dom";
import axios from "axios";
import { Dropdown, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { FaUserCircle, FaSignOutAlt, FaUser, FaCog } from 'react-icons/fa';

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';
import formsStyles from '../styles/modules/forms.module.css'; // Reuse formsStyles from For You Page
import EventCard from './EventCard.js'; 
import logoFull from '../assets/ventaura-logo-full-small-dark.png'; 
import logo from '../assets/ventaura-logo-white.png'; 
import Footer from '../components/footer';


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
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); 
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

  // Handle Manual Logout
  const handleManualLogout = async () => {
    if (!userId) {
      alert("No user ID found in local storage.");
      return;
    }
  
    try {
      const response = await axios.post(
        `http://localhost:5152/api/combined-events/logout?userId=${userId}`
      );
  
      // Check if response.data is defined and has a Message property
      if (response.data && response.data.Message) {
        alert(response.data.Message);
      } else {
        alert("Logout successful");
      }
  
      // Remove userId from localStorage
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
    
    // Log the entire response data for inspection
    console.log("API Response:", response.data);
    
    // Determine the number of events fetched
    const fetchedEvents = response.data.events || [];
    const eventCount = fetchedEvents.length;
    
    // Update the events state
    setEvents(fetchedEvents);
    
    // Log the number of events fetched
    console.log(`Number of events fetched: ${eventCount}`);
    
    // Update the message to include the number of events
    // setMessage(response.data.Message || `Events fetched successfully. Number of events: ${eventCount}`);
  } catch (error) {
    console.error("Error fetching events:", error);
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

  // Optional: Fetch initial events or handle other side effects here

  return (
    <div className={layoutStyles['page-container']}>
      {/* Header */}
      <header 
        className={`${layoutStyles.header} ${!showHeader ? layoutStyles.hidden : ''}`}
      >
        {/* Sidebar Toggle Button */}
        <button 
          className={`${buttonStyles['sidebar-handle']} ${isSidebarOpen ? buttonStyles.open : ''}`} 
          onClick={() => setIsSidebarOpen(!isSidebarOpen)} 
          aria-label="Toggle Sidebar"
        ></button>

        {/* Logo */}
        <div className={layoutStyles['logo-container']}>
          <img src={logoFull} alt="Logo" className={navigationStyles['logo-header']} />
        </div>

        {/* Center Buttons */}
        <div className={layoutStyles['center-buttons-container']}>
          <NavLink 
            to="/global-page" 
            className={({ isActive }) => 
              isActive ? `${buttonStyles['button-56']} ${buttonStyles.active}` : buttonStyles['button-56']
            }
            end
          >
            Global
          </NavLink>
          <NavLink 
            to="/for-you" 
            className={({ isActive }) => 
              isActive ? `${buttonStyles['button-56']} ${buttonStyles.active}` : buttonStyles['button-56']
            }
            end
          >
            For You
          </NavLink>
          <NavLink 
            to="/post-event-page" 
            className={({ isActive }) => 
              isActive ? `${buttonStyles['button-56']} ${buttonStyles.active}` : buttonStyles['button-56']
            }
            end
          >
            Post Event
          </NavLink>
        </div>

        {/* User Profile Dropdown */}
        <div className={layoutStyles['header-right']}>
          <Dropdown drop="down">
            <Dropdown.Toggle 
              variant="none" 
              id="dropdown-basic" 
              className={buttonStyles['profile-dropdown-toggle']}
              aria-label="User Profile Menu"
            >
              <FaUserCircle size={28} />
            </Dropdown.Toggle>

            <Dropdown.Menu className={layoutStyles['dropdown-menu']}>
              <Dropdown.Item onClick={() => navigate("/settings")}>
                <FaUser className={layoutStyles['dropdown-icon']} /> Profile
              </Dropdown.Item>
              <Dropdown.Divider className={layoutStyles['dropdown-divider']} />
              <Dropdown.Item onClick={handleManualLogout}>
                <FaSignOutAlt className={layoutStyles['dropdown-icon']} /> Logout
              </Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </div>
      </header>

      {/* Main layout container */}
      <div className={layoutStyles['main-layout']}>
        {/* Left Navigation Sidebar */}
        <div className={`${layoutStyles.sidebar} ${isSidebarOpen ? layoutStyles.open : ''}`}>
          
          {/* Top Section: Logo and Navigation Links */}
          <div className={navigationStyles['top-section']}>
            {/* Logo Container */}
            <div className={navigationStyles['logo-container']}>
              <img src={logo} alt="Logo" className={navigationStyles['logo']} />
            </div>

            {/* Close Sidebar Button */}
            <button 
              className={buttonStyles['close-sidebar']} 
              onClick={() => setIsSidebarOpen(false)}
              aria-label="Close Sidebar"
            />
            
            {/* Navigation Links Container */}
            <div className={navigationStyles['links-container']}>
              <Link to="/for-you" className={navigationStyles['sidebar-link']} onClick={() => setIsSidebarOpen(false)}>
                For You
              </Link>
              <Link to="/about-us" className={navigationStyles['sidebar-link']} onClick={() => setIsSidebarOpen(false)}>
                About Us
              </Link>
              <Link to="/contact-us" className={navigationStyles['sidebar-link']} onClick={() => setIsSidebarOpen(false)}>
                Contact Us
              </Link>
            </div>
          </div>

          {/* Bottom Section: Logout Button */}
          <button 
            onClick={handleManualLogout} 
            className={buttonStyles['logout-button']}
          >
            Logout
          </button>
        </div>
        
        {/* Main Content Area */}
        <main className={layoutStyles['main-content']}>
          {/* Filters Section */}
          <div className={formsStyles['filters-container']}>
            <h2 className={formsStyles['heading']}>Search Events</h2>
            <form onSubmit={handleSearch} className={formsStyles.form} noValidate>
              {/* City Input */}
              <div className={formsStyles['form-group']}>
                <label htmlFor="city" className={formsStyles['form-label']}>City</label>
                <input
                  type="text"
                  id="city"
                  name="city"
                  placeholder="Enter city name"
                  value={city}
                  onChange={handleCityChange}
                  className={formsStyles['form-input']}
                  required
                  aria-required="true"
                  aria-label="City Name"
                />
              </div>

              {/* Event Type Select */}
              <div className={formsStyles['form-group']}>
                <label htmlFor="eventType" className={formsStyles['form-label']}>Event Type</label>
                <select 
                  name="eventType" 
                  id="eventType"
                  value={filters.eventType} 
                  onChange={handleFilterChange}
                  className={formsStyles['form-input']}
                >
                  <option value="">Select Event Type</option>
                  {eventTypes.map((type) => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              {/* Max Distance Input */}
              <div className={formsStyles['form-group']}>
                <label htmlFor="maxDistance" className={formsStyles['form-label']}>Max Distance (km)</label>
                <input 
                  type="number" 
                  name="maxDistance" 
                  id="maxDistance"
                  placeholder="Enter maximum distance"
                  value={filters.maxDistance} 
                  onChange={handleFilterChange} 
                  className={formsStyles['form-input']} 
                  min="0"
                />
              </div>

              {/* Max Price Input */}
              <div className={formsStyles['form-group']}>
                <label htmlFor="maxPrice" className={formsStyles['form-label']}>Max Price ($)</label>
                <input 
                  type="number" 
                  name="maxPrice" 
                  id="maxPrice"
                  placeholder="Enter maximum price"
                  value={filters.maxPrice} 
                  onChange={handleFilterChange} 
                  className={formsStyles['form-input']} 
                  min="0"
                />
              </div>

              {/* Buttons */}
              <div className={formsStyles['button-container']}>
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
          </div>

          {/* Message Display */}
          {message && <p className={layoutStyles.message}>{message}</p>}

          {/* Events Grid */}
          <div className={layoutStyles['event-grid']}>
            {events.map((event, index) => (
              <EventCard key={index} event={event} />
            ))}
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default GlobalPage;
