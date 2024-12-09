// src/pages/ForYou.js

import React, { useState, useEffect } from "react";
import axios from "axios";
import Papa from 'papaparse';
import { usePapaParse } from 'react-papaparse';
import EventCard from './EventCard.js';  
import { useNavigate, Link } from "react-router-dom";
import { Dropdown, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { FaUserCircle, FaSignOutAlt, FaUser, FaCog } from 'react-icons/fa'; 

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';
import formsStyles from '../styles/modules/forms.module.css';
import logo from '../assets/ventaura-logo-white.png'; 
import logoFull from '../assets/ventaura-logo-full-small-dark.png'; 
import LoadingOverlay from '../components/LoadingOverlay';

const ForYou = () => {
  const navigate = useNavigate();
  const [userId, setUserId] = useState(localStorage.getItem("userId"));
  const [events, setEvents] = useState([]);
  const [message, setMessage] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); 
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(false); 
  const { readString } = usePapaParse();
  const [csvData, setCsvData] = useState([]);
  const [showHeader, setShowHeader] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0); 
  const [userLocation, setUserLocation] = useState('Loading...');
  const [coordinates, setCoordinates] = useState(null);
  const [progress, setProgress] = useState(0);
  const isLoading = progress < 100;
  const MIN_DISPLAY_TIME = 10000; // 10 seconds
  const [timerDone, setTimerDone] = useState(false);
  const [dataLoaded, setDataLoaded] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    firstName: "",
    lastName: "",
    latitude: "",
    longitude: "",
    preferences: [],
    dislikes: [],
    priceRange: 50, // Default value for the slider
    password: "",
  });

  // Timeout duration in milliseconds (30 minutes)
  const TIMEOUT_DURATION = 30 * 60 * 1000;

  useEffect(() => {
    if (!userId) {
      setMessage("No user ID found. Please log in first.");
      navigate("/login");
      return;
    }

    let timer = null;

    const fetchData = async () => {
      try {
        // === Start Minimum Display Timer ===
        timer = setTimeout(() => {
          setTimerDone(true);
          console.log("Timer done");
        }, MIN_DISPLAY_TIME);

        // === Step 1: Fetch Events ===
        /* const fetchEventsResponse = await axios.get(
          `http://localhost:5152/api/combined-events/fetch?userId=${userId}`,
          {
            onDownloadProgress: (progressEvent) => {
              const { loaded, total } = progressEvent;
              if (total) {
                // Assuming this call represents 50% of the total progress
                const percentCompleted = Math.round((loaded / total) * 50);
                setProgress((prevProgress) => {
                  // Ensure we don't decrease progress
                  return Math.max(prevProgress, percentCompleted);
                });
              }
            }
          }
        );
        setMessage(fetchEventsResponse.data.Message || "");
        setEvents(fetchEventsResponse.data.insertedEvents || []); */

        // === Step 2: Fetch CSV Data ===
        const fetchCSVResponse = await axios.get(
          `http://localhost:5152/api/combined-events/get-csv?userId=${userId}`,
          {
            responseType: 'blob', // To handle CSV as binary data
            onDownloadProgress: (progressEvent) => {
              const { loaded, total } = progressEvent;
              if (total) {
                // This call represents the remaining 50% of the total progress
                const percentCompleted = Math.round((loaded / total) * 50) + 50;
                setProgress((prevProgress) => {
                  return Math.max(prevProgress, percentCompleted);
                });
              }
            }
          }
        );

        // === Step 3: Parse CSV Data ===
        const reader = new FileReader();
        reader.onload = () => {
          const csvString = reader.result;
          Papa.parse(csvString, {
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
              setEvents(results.data);
              setDataLoaded(true); // Data loading complete
              console.log("Data loaded");
            },
            error: (error) => {
              console.error("CSV Parsing Error:", error);
              setProgress(100); // Even on error, hide the overlay
            }
          });
        };
        reader.onerror = () => {
          console.error("FileReader Error:", reader.error);
          setProgress(100); // Hide the overlay on error
        };
        reader.readAsText(fetchCSVResponse.data);

      } catch (error) {
        console.error("Data Fetching Error:", error);
        setMessage(error.response?.data?.message || "An error occurred while fetching data.");
        setProgress(100); // Hide the overlay even if there's an error
      }
    };

    fetchData();

    // === Setup Inactivity Logout ===
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

    // Cleanup function
    return () => {
      if (timer) clearTimeout(timer);
      clearTimeout(timeout);
      window.removeEventListener("mousemove", handleActivity);
      window.removeEventListener("keypress", handleActivity);
      window.removeEventListener("click", handleActivity);
    };
  }, [userId, navigate]);

  // New useEffect to watch both dataLoaded and timerDone
  useEffect(() => {
    if (dataLoaded && timerDone) {
      setProgress(100); // Hide the overlay
      console.log("Both dataLoaded and timerDone are true. Hiding overlay.");
    }
  }, [dataLoaded, timerDone]);

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

  const handlePreferenceToggle = (preference) => {
    setFormData((prevData) => {
      const newPreferences = prevData.preferences.includes(preference)
        ? prevData.preferences.filter((item) => item !== preference)
        : [...prevData.preferences, preference];
      return { ...prevData, preferences: newPreferences };
    });
  };

  const handleDislikeToggle = (dislike) => {
    setFormData((prevData) => {
      const newDislikes = prevData.dislikes.includes(dislike)
        ? prevData.dislikes.filter((item) => item !== dislike)
        : [...prevData.dislikes, dislike];
      return { ...prevData, dislikes: newDislikes }
    });
  }

  const handleSliderChange = (e) => {
    setFormData((prevData) => ({
      ...prevData,
      priceRange: e.target.value,
    }));
  };

  // Handle scroll to show/hide header based on scroll position
  const handleScroll = () => {
    if (typeof window !== 'undefined') {
      const currentScrollY = window.scrollY;
      const threshold = 100; // Adjust this value as needed
      setShowHeader(currentScrollY < threshold);
    }
  };

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.addEventListener('scroll', handleScroll);
      // Initialize header visibility based on initial scroll position
      handleScroll();
      return () => window.removeEventListener('scroll', handleScroll);
    }
  }, []);

  // Determine active page
  const isActive = (path) => {
    return navigate.location && navigate.location.pathname === path;
  };

  return (
    <div className={layoutStyles['page-container']}>
      {/* Loading Overlay */}
      <LoadingOverlay isVisible={isLoading} progress={progress} />

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
          <button 
            onClick={() => navigate('/global-page')} 
            className={`${buttonStyles['button-56']}`}
          >
            Global
          </button>
          <button 
            onClick={() => navigate('/for-you')} 
            className={`${buttonStyles['button-56']}`}
          >
            For You
          </button>
          <button 
            onClick={() => navigate('/post-event-page')} 
            className={`${buttonStyles['button-56']}`}
          >
            Post Event
          </button>
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
          {message && <p className={layoutStyles.message}>{message}</p>}
          <div className={layoutStyles['event-grid']}>
            {events && events.length > 0 ? (
              events.map((event) => (
                <EventCard key={event.id || event.index} event={event} /> // Preferably use event.id
              ))
            ) : (
              !isLoading && <p>No events found.</p>
            )}
          </div>
        </main>

        {/* Right Preferences Sidebar */}
        <div className={`${layoutStyles['sidebar-right']} ${isRightSidebarOpen ? layoutStyles.open : ''}`}>
          {/* Close Sidebar Button */}
          <button 
              className={buttonStyles['close-sidebar-right']} 
              onClick={() => setIsRightSidebarOpen(false)}
              aria-label="Close Sidebar"
          >
          </button>
          {/* Likes Section */}
          <div className={formsStyles.preferencesSection}>
            <p className={formsStyles.sectionTitle}>Likes:</p>
            {["Festivals-Fairs", "Music", "Performing-Arts", "Visual-Arts", "Sports-active-life", "Nightlife", "Film", "Charities", "Kids-Family", "Food-and-Drink", "Other"].map((preference) => (
              <button
                type="button"
                key={preference}
                onClick={() => handlePreferenceToggle(preference)}
                className={`${buttonStyles['preference-button']} ${
                  formData.preferences.includes(preference) ? buttonStyles.selected : ''
                }`}
              >
                {preference}
              </button>
            ))}
          </div>

          {/* Dislikes Section */}
          <div className={formsStyles.preferencesSection}>
            <p className={formsStyles.sectionTitle}>Dislikes:</p>
            {["Festivals-Fairs", "Music", "Performing-Arts", "Visual-Arts", "Sports-active-life", "Nightlife", "Film", "Charities", "Kids-Family", "Food-and-Drink", "Other"].map((dislike) => (
              <button
                type="button"
                key={dislike}
                onClick={() => handleDislikeToggle(dislike)}
                className={`${buttonStyles['dislike-button']} ${
                  formData.dislikes.includes(dislike) ? buttonStyles.selected : ''
                }`}
              >
                {dislike}
              </button>
            ))}
          </div>

          {/* Price Range Section */}
          <div className={formsStyles.priceRangeSection}>
            <h3 className={formsStyles.subheading}>Select Price Range:</h3>
            <label htmlFor="priceRange" className={formsStyles.rangeLabel}>
              Average Price: ${formData.priceRange}
            </label>
            <input
              type="range"
              id="priceRange"
              name="priceRange"
              min="0"
              max="100"
              step="1"
              value={formData.priceRange}
              onChange={handleSliderChange}
              className={formsStyles.slider}
            />
          </div>

          {/* Update Information Button */}
          <button type="submit" className={buttonStyles.button}>
            Update information
          </button>
        </div>
      </div>

      {/* Preferences FAB */}
      <OverlayTrigger
        placement="top"
        overlay={<Tooltip id="fab-tooltip">Tune Your Feed</Tooltip>}
      >
        <button 
          className={buttonStyles['preferences-fab']} 
          onClick={() => setIsRightSidebarOpen(true)}
          aria-label="Tune Your Feed"
        >
          ⚡
        </button>
      </OverlayTrigger>
    </div>
  );
};

export default ForYou;
