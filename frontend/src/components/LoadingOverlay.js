import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import styles from '../styles/modules/LoadingOverlay.module.css'; 
import logoFull from '../assets/ventaura-logo-full-small-dark.png'; 

const LoadingOverlay = ({ isLoading }) => {
  const [animateOverlay, setAnimateOverlay] = useState(false);
  const [animateBar, setAnimateBar] = useState(false);

  useEffect(() => {
    if (isLoading) {
      setAnimateOverlay(false); // Start off-screen
      const overlayTimer = setTimeout(() => {
        setAnimateOverlay(true); // Slide down
      }, 10);
      const barTimer = setTimeout(() => setAnimateBar(true), 510); // Animate bar after slide down
      return () => {
        clearTimeout(overlayTimer);
        clearTimeout(barTimer);
      };
    } else {
      // When loading ends, trigger slide-up animation.
      setTimeout(() => setAnimateOverlay(false), 10);
      // Keep the bar visible during the slide-up.
    }
  }, [isLoading]);

  return (
    <div 
      className={`${styles.overlay} ${animateOverlay ? styles.show : ''}`} 
      aria-hidden={!isLoading}
    >
      <div className={styles.logoContainer}>
        <img src={logoFull} alt="Logo" className={styles.logo} />
      </div>
      <div 
        className={`${styles.loadingBar} ${animateBar ? styles.loading : ''}`} 
        aria-label="Loading"
      ></div>
    </div>
  );
};

LoadingOverlay.propTypes = {
  isLoading: PropTypes.bool.isRequired,
};

export default LoadingOverlay;
