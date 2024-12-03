import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles.css"; // Import the global CSS

const AboutUs = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();

  const handleManualLogout = () => {
    // Handle logout logic here (optional, based on your app's requirements)
    alert("Logged out (logout logic not implemented).");
    navigate("/login");
  };

  return (
    <div>
      {/* Header */}
      <header className="header">
        <button
          className="sidebar-button"
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        >
          ☰
        </button>
        {/* Settings Icon Button */}
        <button
          className="settings-button"
          onClick={() => navigate("/settings")}
        >
          ⚙️
        </button>
      </header>

      {/* Sidebar */}
      <div className={`sidebar ${isSidebarOpen ? "open" : ""}`}>
        <button className="close-sidebar" onClick={() => setIsSidebarOpen(false)}>
          X
        </button>
        <Link to="/for-you" className="sidebar-link">
          For You
        </Link>
        <Link to="/about-us" className="sidebar-link">
          About Us
        </Link>
        <Link to="/contact-us" className="sidebar-link">
          Contact Us
        </Link>
        <Link to="/post-event-page" className="sidebar-link">
          Post An Event
        </Link>
        <Link className="sidebar-link" onClick={handleManualLogout}>
          Logout
        </Link>
      </div>

      {/* Main Content */}
      <div className="container">
        <h2>About Us</h2>
        <p>
          Ventaura is a personalized event recommendation platform designed to help
          you discover the best events, activities, and experiences tailored to
          your preferences and location.
        </p>
      </div>
    </div>
  );
};

export default AboutUs;
