// LandingPage.js
import React from "react";
import { useNavigate } from "react-router-dom";

// Import shared CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import '../styles/variables.module.css';


const LandingPage = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate("/login");
  };

  return (
    <div className={`${layoutStyles.container} ${layoutStyles.landingContainer}`}>
      <h1 className={layoutStyles.title}>Ventaura</h1>
      <p className={layoutStyles.description}>Your personalized event recommendation platform.</p>
      <button 
        onClick={handleLogin} 
        className={buttonStyles.primaryButton}
      >
        Log In
      </button>
    </div>
  );
};

export default LandingPage;
