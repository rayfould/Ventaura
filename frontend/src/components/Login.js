  import React, { useState, useEffect } from "react";
  import axios from "axios";
  import { useNavigate, Link } from "react-router-dom";
  import styles from '../styles';

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
      <div className={styles.pageContainer}>
        <div className={styles.loginContainer}>
          <h2 className={styles.heading}>Login</h2>
          <form onSubmit={handleSubmit} className={styles.form}>
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              className={styles.formInput}
              required
            />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
              className={styles.formInput}
              required
            />
            <button type="submit" className={styles.formButton}>
              Login
            </button>
          </form>
          {message && <p className={styles.message}>{message}</p>}
          <p className={styles.helperText}>
            Don't have an account?{" "}
            <Link to="/create-account" className={styles.link}>
              Create one here
            </Link>
          </p>
        </div>
      </div>
    );
  };
  
  export default Login;
