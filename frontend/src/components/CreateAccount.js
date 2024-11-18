import React, { useState, useEffect } from "react";
import axios from "axios";

const CreateAccount = () => {
  const [formData, setFormData] = useState({
    email: "",
    firstName: "",
    lastName: "",
    latitude: "",
    longitude: "",
    preferences: [],
    priceRange: "",
    crowdSize: "",
    password: "",
  });
  const [message, setMessage] = useState("");

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

  const handlePreferenceToggle = (preference) => {
    setFormData((prevData) => {
      const newPreferences = prevData.preferences.includes(preference)
        ? prevData.preferences.filter((item) => item !== preference)
        : [...prevData.preferences, preference];
      return { ...prevData, preferences: newPreferences };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://localhost:5152/api/users/create-account", {
        ...formData,
        preferences: formData.preferences.join(", "),
      });
      setMessage("Account created successfully!");
    } catch {
      setMessage("Error creating account. Please try again.");
    }
  };

  return (
    <div className="container">
      <h2>Create Account</h2>
      <form onSubmit={handleSubmit} className="form">
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          className="form-input"
          required
        />
        <input
          type="text"
          name="firstName"
          placeholder="First Name"
          value={formData.firstName}
          onChange={handleChange}
          className="form-input"
          required
        />
        <input
          type="text"
          name="lastName"
          placeholder="Last Name"
          value={formData.lastName}
          onChange={handleChange}
          className="form-input"
          required
        />
        <div>
          <h3>Preferences:</h3>
          {["Music", "Sports", "Food"].map((pref) => (
            <button
              key={pref}
              type="button"
              className={`preference-button ${
                formData.preferences.includes(pref) ? "selected" : ""
              }`}
              onClick={() => handlePreferenceToggle(pref)}
            >
              {pref}
            </button>
          ))}
        </div>
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          className="form-input"
          required
        />
        <button type="submit" className="form-button">
          Create Account
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default CreateAccount;
