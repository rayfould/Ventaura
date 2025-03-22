// Settings.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { Dropdown, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { FaUserCircle, FaSignOutAlt, FaUser, FaCog } from 'react-icons/fa'; 

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import formsStyles from '../styles/modules/forms.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import createAccountStyles from '../styles/modules/createaccount.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';
import logoFull from '../assets/ventaura-logo-full-small-dark.png'; 
import Footer from '../components/footer';
import { API_BASE_URL } from '../config';

const Settings = () => {
  const [userData, setUserData] = useState({
    email: "",
    firstName: "",
    lastName: "",
  });
  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmNewPassword: "",
  });
  const [message, setMessage] = useState("");
  const [passwordMessage, setPasswordMessage] = useState("");
  const navigate = useNavigate(); // Initialize navigate hook
  const [userId, setUserId] = useState(localStorage.getItem("userId")); // Retrieve userId from localStorage

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/users/${userId}`);
        setUserData({
          email: response.data.email,
          firstName: response.data.firstName,
          lastName: response.data.lastName,
        });
      } catch (error) {
        console.log("Error fetching user data:", error);
      }
    };
    fetchUserData();
  }, [navigate, userId]);

  const handleChange = (e) => {
    setUserData({ ...userData, [e.target.name]: e.target.value });
  };

  const handlePasswordChange = (e) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value });
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const userId = localStorage.getItem("userId"); // Retrieve userId from localStorage

      // Prepare the request data
      const updateData = {
        userId: userId,
        email: userData.email, // Include the updated email
        firstName: userData.firstName, // Include the updated first name
        lastName: userData.lastName, // Include the updated last name
      };

      // Make the PUT request to the server
      const response = await axios.put(
        `${API_BASE_URL}/api/users/updatePreferences`,
        updateData
      );

      setMessage(response.data.Message || "User information updated successfully.");
    } catch (error) {
      
      if (error.response) {
        setMessage(error.response.data.Message || "Error updating user data.");
      } else {
        setMessage("An error occurred while updating data. Please try again.");
      }
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();

    // Simple validation
    if (passwordData.newPassword !== passwordData.confirmNewPassword) {
      setPasswordMessage("New passwords do not match.");
      return;
    }

    if (passwordData.newPassword.length < 8) {
      setPasswordMessage("Password must be at least 8 characters long.");
      return;
    }

    try {
      const changePasswordData = {
        userId: userId,
        currentPassword: passwordData.currentPassword,
        newPassword: passwordData.newPassword,
      };

      const response = await axios.put(
        `${API_BASE_URL}/api/users/changePassword`,
        changePasswordData
      );

      setPasswordMessage(response.data.Message || "Password updated successfully.");
      setPasswordData({ currentPassword: "", newPassword: "", confirmNewPassword: "" });
    } catch (error) {
      setPasswordMessage(error.response?.data?.Message || "Error changing password.");
    }
  };

  return (
    <div className={layoutStyles['page-container']}>
      <header className={layoutStyles['header-side']}>
        <div className={layoutStyles['logo-container-side']}>
          <img src={logoFull} alt="Logo" className={navigationStyles['logo-header']} />
        </div>
        <button
          className={buttonStyles.button}
          onClick={() => navigate("/for-you")}
        >
          Back
        </button>
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

      <div className={formsStyles['settings-container']}>
        <h2 className={createAccountStyles['create-account-heading']}>Account Details</h2>
        <form onSubmit={handleSubmit} className={formsStyles['settings-form']}>
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={userData.email}
            onChange={handleChange}
            className={createAccountStyles['form-input']}
            required
          />
          <input
            type="text"
            name="firstName"
            placeholder="First Name"
            value={userData.firstName}
            onChange={handleChange}
            className={createAccountStyles['form-input']}
            required
          />
          <input
            type="text"
            name="lastName"
            placeholder="Last Name"
            value={userData.lastName}
            onChange={handleChange}
            className={createAccountStyles['form-input']}
            required
          />
          <button type="submit" className={createAccountStyles['create-account-button']}>
            Update Settings
          </button>
        </form>

        {message && <p className={formsStyles.message}>{message}</p>}

        <h2 className={createAccountStyles['create-account-heading2']}>Change Password</h2>
        <form onSubmit={handleChangePassword} className={formsStyles['settings-form']}>
          <input
            type="password"
            name="currentPassword"
            placeholder="Current Password"
            value={passwordData.currentPassword}
            onChange={handlePasswordChange}
            className={createAccountStyles['form-input']}
            required
          />
          <input
            type="password"
            name="newPassword"
            placeholder="New Password"
            value={passwordData.newPassword}
            onChange={handlePasswordChange}
            className={createAccountStyles['form-input']}
            required
          />
          <input
            type="password"
            name="confirmNewPassword"
            placeholder="Confirm New Password"
            value={passwordData.confirmNewPassword}
            onChange={handlePasswordChange}
            className={createAccountStyles['form-input']}
            required
          />
          <button type="submit" className={createAccountStyles['create-account-button']}>
            Update Password
          </button>
        </form>

        {message && <p className={formsStyles.message}>{message}</p>}

      </div>
      <Footer />
    </div>
  );
};

export default Settings;
