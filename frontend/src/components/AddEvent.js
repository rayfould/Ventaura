// AddEvent.js
import React, { useState } from 'react';
import axios from "axios";
import { Link, useNavigate } from 'react-router-dom';

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';
import formsStyles from '../styles/modules/forms.module.css';

const AddEvent = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const [userId, setUserId] = useState(localStorage.getItem("userId"));

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
  

  return (
    <div className={layoutStyles['page-container']}>
      {/* Header */}
      <header className={layoutStyles.header}>
        <button
          className={`${buttonStyles['sidebar-handle']} ${isSidebarOpen ? buttonStyles.open : ''}`}
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          aria-label="Toggle Sidebar"
        >
          {/* This button is styled to show/hide the sidebar, no icon text needed as styling might handle it */}
        </button>
        <h1 className={layoutStyles['header-title']}>Add Your Own Event</h1>
        <div className={layoutStyles['header-right']}>
          <button 
            className={buttonStyles['settings-button']} 
            onClick={() => navigate("/settings")}
            aria-label="Go to Settings"
          >
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
          className={buttonStyles['logout-button']}
        >
          Logout
        </button>
      </div>

      {/* Main Content */}
      <main className={layoutStyles.container}>
        <p className={formsStyles.formDescription}>
          By posting your event here, you gain affordable, effective advertising 
          that reaches a wide audience. We’ll match your event with users whose 
          preferences align with what you offer, ensuring that the right people 
          discover it.
        </p>
        <p className={formsStyles.formDescription}>
          To add a new event, please proceed with the payment process.
        </p>
        <p className={formsStyles.formDescription}>
          Once the payment is completed, you’ll be redirected to fill out your event details.
        </p>

        <form
          className={formsStyles.form}
          action="http://localhost:5152/api/create-checkout-session"
          method="POST"
        >
          <button 
            type="submit" 
            className={buttonStyles.primaryButton}
          >
            Make Payment
          </button>
        </form>
      </main>
    </div>
  );
};

export default AddEvent;
