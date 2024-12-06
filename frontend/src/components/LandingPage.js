import React from "react";
import { useNavigate } from "react-router-dom";
import styles from '../styles';
console.log('Styles object:', styles);

const LandingPage = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate("/login");
  };

  return (
    <div className={styles.landingContainer}>
      <h1 className={styles.title}>Ventaura</h1>
      <p className={styles.description}>Your personalized event recommendation platform.</p>
      <button 
        onClick={handleLogin} 
        className={styles.formButton}
      >
        Log In
      </button>
    </div>
  );
};

export default LandingPage;