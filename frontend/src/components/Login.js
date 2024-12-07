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
  const navigate = useNavigate();

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
        () => setMessage("Unable to retrieve your location.")
      );
    }
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://localhost:5152/api/users/login",
        formData
      );
      
      // Save the userId to localStorage
      localStorage.setItem("userId", response.data.userId);
      
      navigate("/for-you", { state: { userId: response.data.userId } });
    } catch (error) {
      setMessage("Invalid email or password.");
    }
  };

  return (
    <div className={layoutStyles.pageContainer}>
      <div className={formsStyles.loginContainer}>
        <h2 className={formsStyles.heading}>Login</h2>
        <form onSubmit={handleSubmit} className={formsStyles.form}>
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            className={formsStyles.formInput}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            className={formsStyles.formInput}
            required
          />
          <button type="submit" className={buttonStyles.formButton}>
            Login
          </button>
        </form>
        {message && <p className={formsStyles.message}>{message}</p>}
        <p className={formsStyles.helperText}>
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
