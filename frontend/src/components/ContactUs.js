// ContactUs.js
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';

const ContactUs = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();

  const handleManualLogout = () => {
    // Handle logout logic here (optional, based on your app's requirements)
    alert("Logged out (logout logic not implemented).");
    navigate("/login");
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
      <div className={`${layoutStyles.sidebar} ${isSidebarOpen ? layoutStyles.open : ''}`}>
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

      {/* Main Content */}
      <div className={layoutStyles.container}>
        <h2 className={layoutStyles.heading}>Contact Us</h2>
        <p className={layoutStyles.text}>For support or inquiries, email us at support@ventaura.com.</p>
      </div>
    </div>
  );
};

export default ContactUs;
