// ForYou.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import Papa from 'papaparse';
import { usePapaParse } from 'react-papaparse';
import EventCard from './EventCard.js';  
import { useLocation, useNavigate, Link } from "react-router-dom"; // Ensure 'Link' is imported here
import styles from '../styles';
  

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
      return { ...prevData, dislikes: newDislikes}
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
    <div className={styles.pageContainer}>
      {/* Header stays at top */}
      <header className={styles.header}>
        <button className={styles.sidebarButton} onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
          ☰
        </button>
        <div className={styles.centerButtonsContainer}>
          <button onClick={() => navigate('/for-you')} className={styles.forYouButton}>
            For You
          </button>
          <button onClick={() => navigate('/global-page')} className={styles.globalPageButton}>
            Global Page
          </button>
        </div>
        <div className={styles.headerRight}>
          <button className={styles.settingsButton} onClick={() => navigate("/settings")}>
            ⚙️
          </button>
          <button className={styles.openSidebarRight} onClick={() => setIsRightSidebarOpen(true)}>
            ☰ Preferences
          </button>
        </div>
      </header>

      {/* Main layout container */}
      <div className={styles.mainLayout}>
        {/* Left Sidebar */}
        <div className={`${styles.sidebar} ${isSidebarOpen ? styles.open : ''}`}>
          <button className={styles.closeSidebar} onClick={() => setIsSidebarOpen(false)}>
            X
          </button>
          {/* Replace Link with button for logout, use Link for navigation */}
          <Link to="/for-you" className={styles.sidebarLink} onClick={() => setIsSidebarOpen(false)}>
            For You
          </Link>
          <Link to="/about-us" className={styles.sidebarLink} onClick={() => setIsSidebarOpen(false)}>
            About Us
          </Link>
          <Link to="/contact-us" className={styles.sidebarLink} onClick={() => setIsSidebarOpen(false)}>
            Contact Us
          </Link>
          <Link to="/post-event-page" className={styles.sidebarLink} onClick={() => setIsSidebarOpen(false)}>
            Post An Event
          </Link>
          <button 
            onClick={handleManualLogout} 
            className={styles.sidebarLink}
          >
            Logout
          </button>
        </div>
        {/* Main Content */}
        <main className={styles.mainContent}>
          {message && <p className={styles.message}>{message}</p>}
          <div className={styles.eventGrid}>
            {events && events.map((event, index) => (
              <EventCard key={index} event={event} />
            ))}
          </div>
        </main>

        {/* Right Sidebar */}
        <div className={`${styles.sidebarRight} ${isRightSidebarOpen ? styles.open : ''}`}>
          <button className={styles.closeSidebarRight} onClick={() => setIsRightSidebarOpen(false)}>
            ×
          </button>

          <div className={styles.preferencesSection}>
            <p className={styles.sectionTitle}>Likes:</p>
            {["Festivals-Fairs", "Music", "Performing-Arts", "Visual-Arts", "Sports-active-life", "Nightlife", "Film", "Charities", "Kids-Family", "Food-and-Drink", "Other"].map((preference) => (
              <button
                type="button"
                key={preference}
                onClick={() => handlePreferenceToggle(preference)}
                className={`${styles.preferenceButton} ${
                  formData.preferences.includes(preference) ? styles.selected : ''
                }`}
              >
                {preference}
              </button>
            ))}
          </div>

          <div className={styles.preferencesSection}>
            <p className={styles.sectionTitle}>Dislikes:</p>
            {["Festivals-Fairs", "Music", "Performing-Arts", "Visual-Arts", "Sports-active-life", "Nightlife", "Film", "Charities", "Kids-Family", "Food-and-Drink", "Other"].map((dislike) => (
              <button
                type="button"
                key={dislike}
                onClick={() => handleDislikeToggle(dislike)}
                className={`${styles.dislikeButton} ${
                  formData.dislikes.includes(dislike) ? styles.selected : ''
                }`}
              >
                {dislike}
              </button>
            ))}
          </div>

          <div className={styles.priceRangeSection}>
            <h3 className={styles.subheading}>Select Price Range:</h3>
            <label htmlFor="priceRange" className={styles.rangeLabel}>
              Average Price: ${formData.priceRange}
            </label>
            <input
              type="range"
              id="priceRange"
              name="priceRange"
              min="0"
              max="100+"
              step="1"
              value={formData.priceRange}
              onChange={handleSliderChange}
              className={styles.slider}
            />
          </div>

          <button type="submit" className={styles.formButton}>
            Update information
          </button>
        </div>
      </div>
    </div>
  );
};

export default ForYou;
