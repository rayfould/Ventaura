// AboutUs.js
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { Dropdown, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { FaUserCircle, FaSignOutAlt, FaUser, FaCog } from 'react-icons/fa'; 

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';
import logo from '../assets/ventaura-logo-white-smooth.png'; 
import Footer from '../components/footer';


const AboutUs = () => {
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
      <header className={layoutStyles['header-side']}>
        <button 
          className={`${buttonStyles['sidebar-handle']} ${isSidebarOpen ? buttonStyles.open : ''}`} 
          onClick={() => setIsSidebarOpen(!isSidebarOpen)} 
          aria-label="Toggle Sidebar"
        >
        </button>
        <h1 className={layoutStyles['header-title']}>About Us</h1>
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

      {/* Sidebar */}
      <div className={`${layoutStyles.sidebar} ${isSidebarOpen ? layoutStyles.open : ''}`}>
        <div className={navigationStyles['top-section']}>
          <div className={navigationStyles['logo-container']}>
            <img src={logo} alt="Logo" className={navigationStyles['logo']} />
          </div>
          <button 
            className={buttonStyles['close-sidebar']} 
            onClick={() => setIsSidebarOpen(false)}
            aria-label="Close Sidebar"
          />
          <div className={navigationStyles['links-container']}>
            <Link to="/for-you" className={navigationStyles['sidebar-link']}>For You</Link>
            <Link to="/about-us" className={navigationStyles['sidebar-link']}>About Us</Link>
            <Link to="/contact-us" className={navigationStyles['sidebar-link']}>Contact Us</Link>
          </div>
        </div>
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
      <Footer />
    </div>
  );
};

export default AboutUs;

