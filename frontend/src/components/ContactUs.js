// ContactUs.js
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';
import contactStyles from '../styles/modules/contactus.module.css'; // Import contact-specific styles

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
        <h1 className={layoutStyles['header-title']}>Contact Us</h1>
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
      <main className={contactStyles['contact-container']}>

        <p className={contactStyles['contact-text']}>
          For support or inquiries, email us at 
          <a href="mailto:support@ventaura.com" className={contactStyles['email-link']}> support@ventaura.com</a>.
        </p>

        <p className={contactStyles['contact-text']}>
          You can also follow us on social media for updates:
        </p>

        <div className={contactStyles['social-buttons-container']}>
          <a href="#" className={contactStyles['social-button']}>Facebook</a>
          <a href="#" className={contactStyles['social-button']}>Twitter</a>
          <a href="#" className={contactStyles['social-button']}>Instagram</a>
        </div>

        <p className={contactStyles['address']}>
          Or visit us at:<br />
          <span className={contactStyles['strong-text']}>123 Main Street, Suite 400</span><br />
          Boston, MA
        </p>
      </main>
    </div>
  );
};

export default ContactUs;
