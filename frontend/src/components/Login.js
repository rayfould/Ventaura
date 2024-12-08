// Login.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import formsStyles from '../styles/modules/forms.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';

const Login = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    latitude: "",
    longitude: "",
  });
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false); 
  const navigate = useNavigate();

  // Get User's Location on Page Load
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

  // Handle Form Changes
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle Form Submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(""); 
    setIsLoading(true); 

    const payload = {
      email: formData.email,
      password: formData.password,
      latitude: formData.latitude,
      longitude: formData.longitude
    };

    console.log("Sending Payload:", payload);

    try {
      const response = await axios.post(
        "http://localhost:5152/api/users/login",
        payload
      );

      console.log("Response Data:", response.data); 

      if (response.status === 200 && response.data.userId) {
        // Save the userId to localStorage
        localStorage.setItem("userId", response.data.userId);
        navigate("/for-you", { state: { userId: response.data.userId } });
      } else {
        setMessage("Unexpected server response.");
      }
    } catch (error) {
      console.error("Error Response:", error.response); 
      setMessage(error.response?.data?.message || "Invalid email or password.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={layoutStyles['page-container']}>
      
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
