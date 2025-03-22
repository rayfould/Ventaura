// AddEvent.js
import React, { useState } from 'react';
import axios from "axios";
import { Link, useNavigate, NavLink } from 'react-router-dom';
import { Dropdown, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { FaUserCircle, FaSignOutAlt, FaUser, FaCog } from 'react-icons/fa';

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';
import formsStyles from '../styles/modules/forms.module.css';
import logo from '../assets/ventaura-logo-white-smooth.png'; 
import Footer from '../components/footer';
import logoFull from '../assets/ventaura-logo-full-small-dark.png'; 
import { API_BASE_URL } from '../config';


const AddEvent = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const [userId, setUserId] = useState(localStorage.getItem("userId"));
  const [showHeader, setShowHeader] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  const handleNavigateToSuccess = () => {
    navigate("/success");
  };

  const handleManualLogout = async () => {
    if (!userId) {
      alert("No user ID found in local storage.");
      return;
    }
  
  
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/combined-events/logout?userId=${userId}`
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
  // Handle scroll to hide/show header
  const handleScroll = () => {
    if (typeof window !== 'undefined') {
      const currentScrollY = window.scrollY;
      setShowHeader(currentScrollY <= lastScrollY || currentScrollY < 100);
      setLastScrollY(currentScrollY);
    }
  };
  

  return (
    <div className={layoutStyles['page-container']}>
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
      <main className={layoutStyles['side-container']}>
      <div className={layoutStyles['container-title']}>
        <h1>Post Your Event</h1>
        <div className={layoutStyles['title-underline']}></div>
      </div>
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
        <div className={layoutStyles.gap}></div>

        <form
          className={formsStyles.form}
          // Removed action and method attributes
        >
          <button 
            type="button" // Added type="button" to prevent form submission
            onClick={handleNavigateToSuccess} 
            className={buttonStyles.primaryButton}
            >
              Make Payment
          </button>
        </form>
      </main>
      <Footer />
    </div>
  );
};

export default AddEvent;
