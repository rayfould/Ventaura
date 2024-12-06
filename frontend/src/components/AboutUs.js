import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import styles from '../styles';

const AboutUs = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();

  const handleManualLogout = () => {
    // Handle logout logic here (optional, based on your app's requirements)
    alert("Logged out (logout logic not implemented).");
    navigate("/login");
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

      {/* Main Content */}
      <div className={styles.container}>
        <h2 className={styles.heading}>About Us</h2>
        <p className={styles.text}>
          Ventaura is a personalized event recommendation platform designed to help
          you discover the best events, activities, and experiences tailored to
          your preferences and location.
        </p>
      </div>
    </div>
  );
};

export default AboutUs;
