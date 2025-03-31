// src/pages/Login.js

import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import { LoadingContext } from '../App';

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import formsStyles from '../styles/modules/forms.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import { API_BASE_URL } from '../config';

const Login = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    latitude: "",
    longitude: "",
  });
  const [message, setMessage] = useState("");
  const navigate = useNavigate();
  const { isLoading, setIsLoading } = useContext(LoadingContext);
  
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData((prevData) => ({
            ...prevData,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          }));
        },
        (error) => {
          console.error("Geolocation error:", error);
          setMessage("Unable to retrieve your location. Please enable location services.");
        }
      );
    } else {
      setMessage("Geolocation is not supported by your browser.");
    }
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(""); // Clear any previous messages
  
    // Store the timer ID so we can cancel if needed
    const timerId = setTimeout(() => {
      setIsLoading(true); // Trigger the loading overlay after 400ms
    }, 400);
  
    try {
      const response = await axios.post(`${API_BASE_URL}/api/users/login`, formData);
  
      // On success, cancel the timer to prevent a delayed overlay from appearing
      clearTimeout(timerId);
  
      localStorage.setItem("userId", response.data.userId);
      setMessage("Login successful! Redirecting...");
      navigate("/for-you", { state: { userId: response.data.userId } });
    } catch (error) {
      // Cancel the timer so the overlay never starts
      clearTimeout(timerId);
      setIsLoading(false);
      setMessage(error.response?.data?.message || "Invalid email or password.");
    }
  };
  

  return (
    <div className={layoutStyles['page-container']}>
      {/* Removed LoadingOverlay from Login.js */}

      <div className={formsStyles['login-container']}>
        <h2 className={formsStyles['heading']}>Login</h2>

        {message && <p className={formsStyles['error-message']}>{message}</p>}

        <form onSubmit={handleSubmit} className={formsStyles.form} noValidate>
          {/* Email Input */}
          <div className={formsStyles['form-group']}>
            <label htmlFor="email" className={formsStyles['form-label']}>Email</label>
            <input
              type="email"
              id="email"
              name="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              className={formsStyles['form-input']}
              required
              aria-required="true"
              aria-label="Email Address"
            />
          </div>

          {/* Password Input */}
          <div className={formsStyles['form-group']}>
            <label htmlFor="password" className={formsStyles['form-label']}>Password</label>
            <input
              type="password"
              id="password"
              name="password"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
              className={formsStyles['form-input']}
              required
              aria-required="true"
              aria-label="Password"
            />
          </div>

          <button 
            type="submit" 
            className={`${buttonStyles['form-button']} ${isLoading ? buttonStyles['loading'] : ''}`} 
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className={formsStyles['helper-text']}>
          Don't have an account?{" "}
          <Link to="/create-account" className={buttonStyles.link}>
            Create one here
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
