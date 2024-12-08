// CreateAccount.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

import layoutStyles from '../styles/layout.module.css';
import formsStyles from '../styles/modules/forms.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';

const CreateAccount = () => {
  const [formData, setFormData] = useState({
    email: "",
    firstName: "",
    lastName: "",
    latitude: "",
    longitude: "",
    preferences: [],
    dislikes: [],
    priceRange: 50, 
    maxDistance: 10, 
    password: "",
  });

  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
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
        (error) => {
          console.error("Error fetching location: ", error);
          setMessage("Unable to retrieve your location. Please enter manually.");
        }
      );
    } else {
      console.error("Geolocation is not supported by this browser.");
      setMessage("Geolocation is not supported by your browser.");
    }
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handlePreferenceToggle = (preference) => {
    setFormData((prevData) => {
      const newPreferences = prevData.preferences.includes(preference)
        ? prevData.preferences.filter((item) => item !== preference)
        : [...prevData.preferences, preference];
      return { ...prevData, preferences: newPreferences };
    });
  };

  const handleDislikeToggle = (dislike) => {
    setFormData((prevData) => {
      const newDislikes = prevData.dislikes.includes(dislike)
        ? prevData.dislikes.filter((item) => item !== dislike)
        : [...prevData.dislikes, dislike];
      return { ...prevData, dislikes: newDislikes };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage("");

    const requestData = {
      ...formData,
      latitude: Number(formData.latitude),
      longitude: Number(formData.longitude),
      priceRange: formData.priceRange.toString(),
      maxDistance: Number(formData.maxDistance),
      preferences: formData.preferences.join(", "),
      dislikes: formData.dislikes.join(", "),
      passwordHash: formData.password,
      isLoggedIn: false,
    };

    try {
      const response = await axios.post(
        "http://localhost:5152/api/users/create-account",
        requestData
      );
      setMessage(response.data.Message);
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data.Message || "Error creating account.");
      } else {
        setMessage("An error occurred. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={layoutStyles['page-container']}>
      <div className={formsStyles['account-container']}>
        <h2 className={formsStyles['heading']}>Create Account</h2>

        {message && <p className={formsStyles['error-message']}>{message}</p>}

        <form onSubmit={handleSubmit} className={formsStyles.form}>
          <input 
            type="email" 
            name="email" 
            placeholder="Email" 
            value={formData.email} 
            onChange={handleChange} 
            className={formsStyles['form-input']} 
            required 
          />
          <input 
            type="text" 
            name="firstName" 
            placeholder="First Name" 
            value={formData.firstName} 
            onChange={handleChange} 
            className={formsStyles['form-input']} 
            required 
          />
          <input 
            type="text" 
            name="lastName" 
            placeholder="Last Name" 
            value={formData.lastName} 
            onChange={handleChange} 
            className={formsStyles['form-input']} 
            required 
          />

          <h3 className={formsStyles['subheading']}>Select Preferences</h3>
          <div className={formsStyles['grid-container']}>
            {["Music", "Festivals", "Hockey", "Outdoors", "Workshops", "Conferences", 
              "Exhibitions", "Community", "Theater", "Family", "Nightlife", "Wellness", 
              "Holiday", "Networking", "Gaming", "Film", "Pets", "Virtual", "Charity", 
              "Science", "Basketball", "Pottery", "Tennis", "Soccer", "Football", 
              "Fishing", "Hiking"].map((preference) => (
              <button 
                key={preference} 
                type="button" 
                onClick={() => handlePreferenceToggle(preference)} 
                className={`${buttonStyles['preference-button']} ${formData.preferences.includes(preference) ? buttonStyles['selected'] : ''}`}
              >
                {preference}
              </button>
            ))}
          </div>

          <h3 className={formsStyles['subheading']}>Select Dislikes</h3>
          <div className={formsStyles['grid-container']}>
            {["Music", "Festivals", "Hockey", "Outdoors", "Workshops", "Conferences", 
              "Exhibitions", "Community", "Theater", "Family", "Nightlife", "Wellness", 
              "Holiday", "Networking", "Gaming", "Film", "Pets", "Virtual", "Charity", 
              "Science", "Basketball", "Pottery", "Tennis", "Soccer", "Football", 
              "Fishing", "Hiking"].map((dislike) => (
              <button 
                key={dislike} 
                type="button" 
                onClick={() => handleDislikeToggle(dislike)} 
                className={`${buttonStyles['dislike-button']} ${formData.dislikes.includes(dislike) ? buttonStyles['selected'] : ''}`}
              >
                {dislike}
              </button>
            ))}
          </div>

          <h3 className={formsStyles['subheading']}>Price Range: ${formData.priceRange}</h3>
          <input 
            type="range" 
            name="priceRange" 
            min="0" 
            max="100" 
            value={formData.priceRange} 
            onChange={handleChange} 
            className={formsStyles['slider']} 
          />

          <h3 className={formsStyles['subheading']}>Max Distance: {formData.maxDistance} km</h3>
          <input 
            type="range" 
            name="maxDistance" 
            min="1" 
            max="100" 
            value={formData.maxDistance} 
            onChange={handleChange} 
            className={formsStyles['slider']} 
          />

          <input 
            type="password" 
            name="password" 
            placeholder="Password" 
            value={formData.password} 
            onChange={handleChange} 
            className={formsStyles['form-input']} 
            required 
          />

          <button 
            type="submit" 
            className={`${buttonStyles['form-button']} ${isLoading ? buttonStyles['loading'] : ''}`} 
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        {message && <p className={formsStyles['error-message']}>{message}</p>}
      </div>
    </div>
  );
};

export default CreateAccount;

