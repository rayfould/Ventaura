// CreateAccount.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

// Import specific CSS modules
import layoutStyles from '../styles/layout.module.css';
import formsStyles from '../styles/modules/forms.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import postEventStyles from '../styles/modules/postevent.module.css';

// **Preference & Dislike Mapping**
const preferenceMapping = {
  "Festivals": "Festivals-Fairs",
  "Outdoors": "Sports-active-life",
  "Exhibitions": "Visual-Arts",
  "Community": "Charities",
  "Theater": "Performing-Arts",
  "Family": "Kids-Family",
  "Film": "Film",
  "Charity": "Charities",
};

const uniqueOptions = [
  "Music", "Festivals", "Hockey", "Outdoors", "Workshops", "Conferences", 
  "Exhibitions", "Community", "Theater", "Family", "Nightlife", "Wellness", 
  "Holiday", "Networking", "Gaming", "Film", "Pets", "Virtual", "Charity", 
  "Science", "Basketball", "Pottery", "Tennis", "Soccer", "Football", 
  "Fishing", "Hiking"
];

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
  const navigate = useNavigate();

  // Get user's live location using Geolocation API
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

  const handleSliderChange = (e) => {
    setFormData((prevData) => ({
      ...prevData,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Map preferences and dislikes according to the preferenceMapping object
    const mappedPreferences = formData.preferences.map(preference => 
      preferenceMapping[preference] || preference
    );

    const mappedDislikes = formData.dislikes.map(dislike => 
      preferenceMapping[dislike] || dislike
    );

    // Prepare the data to send
    const requestData = {
      ...formData,
      latitude: Number(formData.latitude),
      longitude: Number(formData.longitude),
      priceRange: formData.priceRange.toString(),
      maxDistance: Number(formData.maxDistance),
      preferences: mappedPreferences.join(", "),
      dislikes: mappedDislikes.join(", "),
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
    }
  };

  return (
    <div className={postEventStyles['post-event-container']}>
      <h2 className={postEventStyles['post-event-heading']}>Create Account</h2>
      <form onSubmit={handleSubmit} className={postEventStyles['post-event-form']}>
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          className={postEventStyles['form-input']}
          required
        />
        <input
          type="text"
          name="firstName"
          placeholder="First Name"
          value={formData.firstName}
          onChange={handleChange}
          className={postEventStyles['form-input']}
          required
        />
        <input
          type="text"
          name="lastName"
          placeholder="Last Name"
          value={formData.lastName}
          onChange={handleChange}
          className={postEventStyles['form-input']}
          required
        />

        <div className={postEventStyles['form-group']}>
          <h3 className={formsStyles.subheading}>Select Preferences:</h3>
          <div className={formsStyles['grid-container']}>
            {uniqueOptions.map((preference) => (
              <button
                type="button"
                key={preference}
                onClick={() => handlePreferenceToggle(preference)}
                className={`${buttonStyles['preference-button']} ${formData.preferences.includes(preference) ? buttonStyles['selected'] : ''}`}
              >
                {preference}
              </button>
            ))}
          </div>
        </div>

        <div className={postEventStyles['form-group']}>
          <h3 className={formsStyles.subheading}>Select Dislikes:</h3>
          <div className={formsStyles['grid-container']}>
            {uniqueOptions.map((dislike) => (
              <button
                type="button"
                key={dislike}
                onClick={() => handleDislikeToggle(dislike)}
                className={`${buttonStyles['dislike-button']} ${formData.dislikes.includes(dislike) ? buttonStyles['selected'] : ''}`}
              >
                {dislike}
              </button>
            ))}
          </div>
        </div>

        <div className={formsStyles.priceRangeSection}>
          <h3 className={formsStyles.subheading}>Select Price Range:</h3>
          <label htmlFor="priceRange" className={formsStyles.rangeLabel}>
            Average Price: ${formData.priceRange}
          </label>
          <input
            type="range"
            id="priceRange"
            name="priceRange"
            min="0"
            max="100"
            step="1"
            value={formData.priceRange}
            onChange={handleSliderChange}
            className={formsStyles.slider}
          />
        </div>

        <div className={formsStyles.priceRangeSection}>
          <h3 className={formsStyles.subheading}>Select Max Distance:</h3>
          <label htmlFor="maxDistance" className={formsStyles.rangeLabel}>
            Max Distance: ${formData.maxDistance}
          </label>
          <input
            type="range"
            id="maxDistance"
            name="maxDistance"
            min="0"
            max="100"
            step="1"
            value={formData.maxDistance}
            onChange={handleSliderChange}
            className={formsStyles.slider}
          />
        </div>

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          className={postEventStyles['form-input']}
          required
        />
        <button type="submit" className={buttonStyles.formButton}>
          Create Account
        </button>
      </form>
      {message && <p className={formsStyles.message}>{message}</p>}
    </div>
  );
};

export default CreateAccount;



