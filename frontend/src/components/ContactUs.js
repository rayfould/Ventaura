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
    alert("Logged out (logout logic not implemented).");
    navigate("/login");
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
        <button 
          onClick={handleManualLogout} 
          className={navigationStyles['sidebar-link']}
        >
          Logout
        </button>
      </div>

      {/* Main Content */}
      <main className={layoutStyles['main-content']}>
        <h2 className={layoutStyles.heading}>Contact Us</h2>
        <p className={layoutStyles.text}>For support or inquiries, email us at <a href="mailto:support@ventaura.com" className={navigationStyles.link}>support@ventaura.com</a>.</p>
        
        <p className={layoutStyles.text}>
          You can also follow us on social media for updates:
        </p>

        <div className={buttonStyles['button-container']}>
          <a href="#" className={buttonStyles['for-you-button']}>Facebook</a>
          <a href="#" className={buttonStyles['for-you-button']}>Twitter</a>
          <a href="#" className={buttonStyles['for-you-button']}>Instagram</a>
        </div>
        
        <p className={layoutStyles.text}>
          Or visit us at:<br />
          123 Main Street, Suite 400<br />
          Your City, Your State
        </p>
      </main>
    </div>
  );
};

export default ContactUs;

