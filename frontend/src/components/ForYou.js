// ForYou.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import Papa from 'papaparse';
import { usePapaParse } from 'react-papaparse';
import EventCard from './EventCard.js';  
import { useLocation, useNavigate, Link } from "react-router-dom";

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';
import formsStyles from '../styles/modules/forms.module.css';

const ForYou = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { userId } = location.state || {};
  const [events, setEvents] = useState([]);
  const [message, setMessage] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(false);
  const { readString } = usePapaParse();
  const [csvData, setCsvData] = useState([]);

  // Form data state for handling form input
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
    const userId = localStorage.getItem("userId"); // Retrieve userId from localStorage

    if (!userId) {
      alert("No user ID found in local storage.");
      return;
    }

    try {
      const response = await axios.post(
        `http://localhost:5152/api/combined-events/logout?userId=${userId}`
      );

      // Remove the userId from localStorage
      localStorage.removeItem("userId");

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

  useEffect(() => {
    const hardcodedUserId = 1; // Hardcode userId for testing
    console.log("========= START DEBUG =========");
    console.log("Using hardcoded userId:", hardcodedUserId);
  
    const fetchCSVData = async () => {
      try {
        console.log("🚀 Starting CSV fetch");
        
        // First API call with hardcoded userId
        console.log("Making first API call to /fetch");
        const fetchResponse = await axios.get(`http://localhost:5152/api/combined-events/fetch?userId=${hardcodedUserId}`);
        console.log("📥 Fetch Response:", fetchResponse.data);
        
        // Second API call with hardcoded userId
        console.log("Making second API call to /get-csv");
        const csvResponse = await axios.get(`http://localhost:5152/api/combined-events/get-csv?userId=${hardcodedUserId}`);
        console.log("📄 Got CSV data");
        
        Papa.parse(csvResponse.data, {
          header: true,
          complete: (results) => {
            console.log("✅ Parse complete!");
            console.log("📊 Number of events:", results.data.length);
            console.log("📝 First event:", results.data[0]);
            setEvents(results.data);
          },
          error: (error) => {
            console.log("❌ Parse error:", error);
          }
        });
  
      } catch (error) {
        console.log("❌ ERROR:", error);
        if (error.response) {
          console.log("❌ Error Response:", error.response.data);
        }
      }
    };
  
    // Call fetchCSVData directly without userId check
    fetchCSVData();
    
  }, [navigate, TIMEOUT_DURATION]); // Remove userId from dependencies since we're hardcoding it
  
  const handleCSVData = (csvString) => {
    readString(csvString, {
      worker: true,
      complete: (results) => {
        // Filter out empty rows and set the data
        const filteredData = results.data.filter(row => 
          Object.values(row).some(value => value !== '')
        );
        setCsvData(filteredData);
        setEvents(filteredData); // Update your existing events state
      },
      header: true, // This assumes your CSV has headers matching your event properties
    });
  };

  const testEvent = {
    title: "Test Event",
    type: "Concert",
    start: "2024-12-06T19:00:00",
    distance: 2.5,
    amount: 25.00,
    currencyCode: "USD",
    url: "#"
  };

  return (
    <div className={layoutStyles['page-container']}>
      {/* Header stays at top */}
      <header className={layoutStyles.header}>
      <button className={buttonStyles['sidebar-button']} onClick={() => setIsSidebarOpen(!isSidebarOpen)} aria-label="Toggle Sidebar">
        <span></span>
        <span></span>
        <span></span>
      </button>
        <div className={layoutStyles['center-buttons-container']}>
          <button onClick={() => navigate('/for-you')} className={buttonStyles['for-you-button']}>
            For You
          </button>
          <button onClick={() => navigate('/global-page')} className={buttonStyles['global-page-button']}>
            Global Page
          </button>
        </div>
        <div className={layoutStyles['header-right']}>
          <button className={buttonStyles['settings-button']} onClick={() => navigate("/settings")}>
            ⚙️
          </button>
          <button className={buttonStyles['open-sidebar-right']} onClick={() => setIsRightSidebarOpen(true)}>
            ☰ Preferences
          </button>
        </div>
      </header>

      {/* Main layout container */}
      <div className={layoutStyles['main-layout']}>
        {/* Left Navigation Sidebar */}
        <div className={`${layoutStyles.sidebar} ${isSidebarOpen ? layoutStyles.open : ''}`}>
          
          {/* Top Section: Close Button and Navigation Links */}
          <div className={navigationStyles['top-section']}>
            <button 
              className={buttonStyles['close-sidebar']} 
              onClick={() => setIsSidebarOpen(false)}
              aria-label="Close Sidebar"
            >
              X
            </button>

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
              <Link to="/post-event-page" className={navigationStyles['sidebar-link']} onClick={() => setIsSidebarOpen(false)}>
                Post An Event
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
            {events && events.map((event, index) => (
              <EventCard key={index} event={event} />
            ))}
          </div>
        </main>

        {/* Right Preferences Sidebar */}
        <div className={`${layoutStyles['sidebar-right']} ${isRightSidebarOpen ? layoutStyles.open : ''}`}>
          <button className={navigationStyles['close-sidebar-right']} onClick={() => setIsRightSidebarOpen(false)}>
            ×
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
    </div>
  );
};

export default ForYou;
