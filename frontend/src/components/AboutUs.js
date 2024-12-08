// AboutUs.js
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';

const AboutUs = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();

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

  return (
    <div className={layoutStyles['page-container']}>
      {/* Header */}
      <header className={layoutStyles.header}>
        <button 
          className={`${buttonStyles['sidebar-handle']} ${isSidebarOpen ? buttonStyles.open : ''}`} 
          onClick={() => setIsSidebarOpen(!isSidebarOpen)} 
          aria-label="Toggle Sidebar"
        >
        </button>
        <h1 className={layoutStyles['header-title']}>About Us</h1>
        <div className={layoutStyles['header-right']}>
          <button className={buttonStyles['settings-button']} onClick={() => navigate("/settings")}>
            ⚙️
          </button>
        </div>
      </header>

      {/* Sidebar */}
      <div className={`${layoutStyles.sidebar} ${isSidebarOpen ? layoutStyles.open : ''}`}>
        <button 
          className={buttonStyles['close-sidebar']} 
          onClick={() => setIsSidebarOpen(false)} 
          aria-label="Close Sidebar"
        />
        <Link to="/for-you" className={navigationStyles['sidebar-link']}>
          For You
        </Link>
        <Link to="/about-us" className={navigationStyles['sidebar-link']}>
          About Us
        </Link>
        <Link to="/contact-us" className={navigationStyles['sidebar-link']}>
          Contact Us
        </Link>
        <Link to="/post-event-page" className={navigationStyles['sidebar-link']}>
          Post An Event
        </Link>
        {/* Bottom Section: Logout Button */}
        <button 
            onClick={handleManualLogout} 
            className={buttonStyles['logout-button']}
          >
            Logout
        </button>
      </div>

      {/* Main Content */}
      <main className={`${layoutStyles['main-content']} ${layoutStyles['center-content']}`}>
        <p className={layoutStyles.text}>
          At Ventaura, we're passionate about connecting people with experiences that enrich their 
          lives and bring communities closer together. Our mission is to provide a personalized 
          platform where users can discover events, activities, and destinations tailored to their 
          unique preferences and locations. 
        </p>

        <p className={layoutStyles.text}>
          Whether you're looking for a live concert, a local workshop, or hidden gems in your city, Ventaura is your trusted guide to finding it all. 
          By leveraging cutting-edge technology, dynamic data sources, and user-focused design, we aim to make exploring 
          your world effortless and exciting. 
        </p>

        <p className={layoutStyles.text}>
          For businesses and individuals, Ventaura offers a seamless way to showcase and promote events, ensuring your opportunities reach the right audience at the right time.
        </p>

        <p className={layoutStyles.text}>
          Join us on this journey to turn ordinary moments into extraordinary memories. Start exploring with Ventaura today—your adventure awaits!
        </p>
      </main>
    </div>
  );
};

export default AboutUs;

