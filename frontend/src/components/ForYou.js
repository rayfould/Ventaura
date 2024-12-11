// src/pages/ForYou.js

import React, { useState, useEffect, useMemo } from "react";
import axios from "axios";
import Papa from 'papaparse';
import { useNavigate, Link, NavLink } from "react-router-dom";
import { Dropdown, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { FaUserCircle, FaSignOutAlt, FaUser } from 'react-icons/fa'; 

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';
import formsStyles from '../styles/modules/forms.module.css';
import logo from '../assets/ventaura-logo-white-smooth.png'; 
import logoFull from '../assets/ventaura-logo-full-small-dark.png'; 
import LoadingOverlay from '../components/LoadingOverlay';
import Footer from '../components/footer';
import EventCard from '../components/EventCard.js'; // Corrected import path

const ForYou = () => {
  const [userData, setUserData] = useState({
    preferences: [],
    dislikes: [],
    priceRange: "",
    maxDistance: ""
  });

  const navigate = useNavigate();
  const [userId] = useState(localStorage.getItem("userId"));
  const [events, setEvents] = useState([]);
  const [message, setMessage] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); 
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(false); 
  const [progress, setProgress] = useState(0);
  const isLoading = progress < 100;
  const MIN_DISPLAY_TIME = 100; // 10 seconds
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

  const uniqueOptions = [
    "Baseball", "Basketball", "Comedy", "Community", "Conferences", 
    "Dance", "Exhibitions", "Family", "Fashion", "Festivals", 
    "Film", "Fishing", "Food and Drink", "Football", "Gaming", 
    "Hiking", "Hockey", "Holiday", "Lectures", "Motorsports", 
    "Music", "Networking", "Nightlife", "Outdoors", 
    "Pets", "Pottery", "Science", "Soccer", "Tennis", 
    "Theater", "Virtual", "Wellness", "Workshops", "Other"
  ];

  const handleChange = (e) => {
    setUserData({ ...userData, [e.target.name]: e.target.value });
  };

  const handlePriceRangeSelect = (price) => {
    setUserData((prevData) => ({
      ...prevData,
      priceRange: price, // Set only one option at a time
    }));
  };

  const priceOptions = ["$", "$$", "$$$", "Irrelevant"]; // **Defined priceOptions**

  // Timeout duration in milliseconds (30 minutes)
  const TIMEOUT_DURATION = 30 * 60 * 1000;

  // Define handleSubmit inside the component
  const handleSubmit = async (e) => {
    e.preventDefault(); 
    try {
      const userId = localStorage.getItem("userId"); // Retrieve userId from localStorage

      // Prepare the request data
      const updateData = {
        userId: userId,
        preferences: userData.preferences.join(", "), // Assuming preferences is an array
        dislikes: userData.dislikes.join(", "), 
        priceRange: userData.priceRange.toString(), 
        maxDistance: Number(userData.maxDistance) 
      };

      // Make the PUT request to the server
      const response = await axios.put(
        `http://localhost:5152/api/users/updatePreferences`,
        updateData
      );

      setMessage(response.data.Message || "User information updated successfully.");

      setTimeout(() => {
        window.location.reload();
      }, 100); 
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data.Message || "An error occurred.");
      } else {
        setMessage("An error occurred while updating preferences.");
      }
    }

    // Optionally, reset the message after some time
    setTimeout(() => {
      setMessage('');
    }, 10000);
  };

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
        console.log("Fetching events...");
        const fetchEventsResponse = await axios.get(
          `http://localhost:5152/api/combined-events/fetch?userId=${userId}`,
          {
            onDownloadProgress: (progressEvent) => {
              const { loaded, total } = progressEvent;
              if (total) {
                const percentCompleted = Math.round((loaded / total) * 50);
                setProgress((prevProgress) => Math.max(prevProgress, percentCompleted));
              }
            }
          }
        );
        console.log("Events fetched:", fetchEventsResponse.data.insertedEvents);
        // Optionally, you can decide to skip this if CSV data is the final source
        // setEvents(fetchEventsResponse.data.insertedEvents || []);

        // === Step 2: Call Ranking API ===
        try {
          console.log("Calling Ranking API...");
          const rankingResponse = await axios.post(
            `http://localhost:8000/rank-events/${userId}`, // FastAPI endpoint
            null, // No body needed as per your C# controller
            {
              headers: {
                'Content-Type': 'application/json',
                // Include authentication headers if required
              }
            }
          );

          console.log("Ranking API Response:", rankingResponse.data);
          if (rankingResponse.data.success) {
            console.log("Ranking successful:", rankingResponse.data.message);
            // Optionally, update state or notify the user
          } else {
            console.error("Ranking failed:", rankingResponse.data.message);
            setMessage("Ranking failed: " + (rankingResponse.data.message || "Unknown error."));
            // Proceed to fetch CSV data
          }
        } catch (rankingError) {
          console.error("Error calling Ranking API:", rankingError);
          setMessage("An error occurred while ranking events.");
          // Proceed to fetch CSV data
        }

        // === Step 3: Fetch CSV Data ===
        console.log("Fetching CSV data...");
        const fetchCSVResponse = await axios.get(
          `http://localhost:5152/api/combined-events/get-csv?userId=${userId}`,
          {
            responseType: 'blob', // To handle CSV as binary data
            onDownloadProgress: (progressEvent) => {
              const { loaded, total } = progressEvent;
              if (total) {
                const percentCompleted = Math.round((loaded / total) * 50) + 50;
                setProgress((prevProgress) => Math.max(prevProgress, percentCompleted));
              }
            }
          }
        );

        console.log("CSV data fetched");
        // === Step 4: Parse CSV Data ===
        const reader = new FileReader();
        reader.onload = () => {
          const csvString = reader.result;
          Papa.parse(csvString, {
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
              console.log("CSV Parsing complete:", results.data);
              setEvents(results.data);
              setDataLoaded(true); // Data loading complete
            },
            error: (error) => {
              console.error("CSV Parsing Error:", error);
              setProgress(100); // Hide the overlay
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

  // UseEffect to fetch user data for preferences bar
  useEffect(() => {
    if (!dataLoaded || !timerDone) return; // Ensure data is loaded and timer is done

    const fetchUserData = async () => {
      try {
        const response = await axios.get(`http://localhost:5152/api/users/${userId}`);
        const cleanData = (data) => {
          return data.replace(/[^a-zA-Z0-9, ]/g, '').split(',').map(item => item.trim());
        };
        
        const preferences = cleanData(response.data.preferences);
        const dislikes = cleanData(response.data.dislikes);
        
        setUserData((prevData) => ({
          ...prevData,
          preferences: preferences,
          dislikes: dislikes,
          priceRange: response.data.priceRange,
          maxDistance: response.data.maxDistance,
        }));
      } catch (error) {
        console.log("Error fetching form data:", error);
      }
    };
    fetchUserData();
  }, [dataLoaded, timerDone, userId]);

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
    setUserData((prevData) => {
      const newPreferences = new Set(prevData.preferences);
      const newDislikes = new Set(prevData.dislikes);

      if (newPreferences.has(preference)) {
        newPreferences.delete(preference);
      } else {
        newPreferences.add(preference);
        newDislikes.delete(preference);
      }

      return { 
        ...prevData, 
        preferences: Array.from(newPreferences), 
        dislikes: Array.from(newDislikes) 
      };
    });
  };

  const handleDislikeToggle = (dislike) => {
    setUserData((prevData) => {
      const newDislikes = new Set(prevData.dislikes);
      const newPreferences = new Set(prevData.preferences);

      if (newDislikes.has(dislike)) {
        newDislikes.delete(dislike);
      } else {
        newDislikes.add(dislike);
        newPreferences.delete(dislike);
      }

      return { 
        ...prevData, 
        dislikes: Array.from(newDislikes), 
        preferences: Array.from(newPreferences) 
      };
    });
  };

  // Handle scroll to show/hide header based on scroll position
  const [showHeader, setShowHeader] = useState(true);
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
          {message && <p className={layoutStyles.message}>{message}</p>}
          <div className={layoutStyles['event-grid']}>
            {events && events.length > 0 ? (
              events.map((event, index) => (
                <EventCard key={event.id || index} event={event} /> // Preferably use event.id
              ))
            ) : (
              !isLoading && dataLoaded && <p>No events found.</p>
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
          <div className={formsStyles['preferences-container']}>
            <p>Show More:</p>
            <div className={formsStyles['pref-button-container']}>
              {uniqueOptions.map((preference) => (
                <button
                  type="button"
                  key={preference}
                  onClick={() => handlePreferenceToggle(preference)}
                  className={`${layoutStyles['preference-button']} ${
                    userData.preferences.includes(preference) ? layoutStyles['selected'] : ''
                  }`}
                >
                  {preference}
                </button>
              ))}
            </div>
          </div>

          <div className={formsStyles['preferences-container']}>
            <p className={layoutStyles.sectionTitle}>Show Less:</p>
            <div className={formsStyles['pref-button-container']}>
              {uniqueOptions.map((dislike) => (
                <button
                  type="button"
                  key={dislike}
                  onClick={() => handleDislikeToggle(dislike)}
                  className={`${layoutStyles['dislike-button']} ${
                    userData.dislikes.includes(dislike) ? layoutStyles['selected'] : ''
                  }`}
                >
                  {dislike}
                </button>
              ))}
            </div>
          </div>


          {/* Price Range Section */}
          <div className={formsStyles['preferences-container']}>
            <p className={layoutStyles.sectionTitle}>Select Price Range:</p>
            <div className={formsStyles['price-button-container']}>
              {priceOptions.map((price) => (
                <button
                  type="button"
                  key={price}
                  onClick={() => handlePriceRangeSelect(price)}
                  className={`${layoutStyles['prices-button']} ${
                    userData.priceRange === price ? layoutStyles['selected'] : ''
                  }`}
                >
                  {price}
                </button>
              ))}
            </div>
          </div>
          <div className={formsStyles['preferences-container']}>
            <p className={layoutStyles['section-title']}>Select Distance(km):</p>
            <input
              type="number"  // Use type="number" instead of type="integer"
              name="maxDistance"  // Corrected the typo (was MaxDistanct)
              placeholder="Max Distance (km)"  // Optional: Placeholder to guide user input
              value={userData.maxDistance}
              onChange={handleChange}
              className={formsStyles.slider}
              min="1"  // Set a minimum distance
              max="100" // Set a maximum distance
              required
            />
          </div>
          {/* Update Information Button */}
          <form onSubmit={handleSubmit}>
            <button type="submit" className={buttonStyles['update-preferences-button']}>
              Update information
            </button>
          </form>
          <p>. </p>
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
      <Footer />
    </div>
    
  );
};

export default ForYou;
