import React from "react";
import { useNavigate } from "react-router-dom";

const LandingPage = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate("/login");
  };

  return (
    <div className="landing-container">
      <h1>Ventaura</h1>
      <p>Your personalized event recommendation platform.</p>
      <button onClick={handleLogin} className="form-button">
        Log In
      </button>
    </div>
  );
};

export default LandingPage;
