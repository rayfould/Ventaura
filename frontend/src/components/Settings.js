import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles.css"; // Import the global CSS
import { useNavigate } from "react-router-dom"; // Import useNavigate hook

const Settings = () => {
  const [userData, setUserData] = useState({
    email: "",
    firstName: "",
    lastName: "",
  });
  const [message, setMessage] = useState("");
  const navigate = useNavigate(); // Initialize navigate hook

  useEffect(() => {
    // Fetch the user's existing data when the component mounts
    const fetchUserData = async () => {
      try {
        const userId = localStorage.getItem("userId"); // Retrieve userId from localStorage
        if (userId) {
          const response = await axios.get(
            `http://localhost:5152/api/users/get-user-data?userId=${userId}`
          );
          setUserData({
            email: response.data.email || "",
            firstName: response.data.firstName || "",
            lastName: response.data.lastName || "",
          });
        } else {
          setMessage("User not found. Please log in again.");
          navigate("/login"); // Redirect to login if userId is not found
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
        setMessage("Error fetching user data. Please try again later.");
      }
    };

    fetchUserData();
  }, [navigate]);

  const handleChange = (e) => {
    setUserData({ ...userData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const userId = localStorage.getItem("userId"); // Retrieve userId from localStorage

      const response = await axios.post(
        `http://localhost:5152/api/users/update-user-data?userId=${userId}`,
        userData
      );

      setMessage(response.data.Message || "User data updated successfully.");
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data.Message || "Error updating user data.");
      } else {
        setMessage("An error occurred while updating data. Please try again.");
      }
    }
  };

  return (
    <div className="container">
      <header className="header">
        <button
          className="sidebar-button"
          onClick={() => navigate("/for-you")}
        >
          Back
        </button>
      </header>

      <h2>Settings</h2>
      <form onSubmit={handleSubmit} className="form">
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={userData.email}
          onChange={handleChange}
          className="form-input"
          required
        />
        <input
          type="text"
          name="firstName"
          placeholder="First Name"
          value={userData.firstName}
          onChange={handleChange}
          className="form-input"
          required
        />
        <input
          type="text"
          name="lastName"
          placeholder="Last Name"
          value={userData.lastName}
          onChange={handleChange}
          className="form-input"
          required
        />
        <button type="submit" className="form-button">
          Update Settings
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default Settings;
