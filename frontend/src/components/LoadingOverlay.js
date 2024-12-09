// src/components/LoadingOverlay.js

import React from "react";
import PropTypes from "prop-types";
import styles from '../styles/modules/LoadingOverlay.module.css'; 
import logoFull from '../assets/ventaura-logo-full-small-dark.png'; 

const LoadingOverlay = ({ isVisible, progress }) => {
  const isIndeterminate = progress === 0 && isVisible;

  return (
    <div 
      className={`${styles.overlay} ${isVisible ? styles.show : ''}`} 
      aria-hidden={!isVisible}
    >
      <div className={styles.logoContainer}>
        <img src={logoFull} alt="Logo" className={styles.logo} />
      </div>
      {isIndeterminate ? (
        <div 
          className={styles.indeterminateLoader} 
          aria-label="Loading"
        ></div>
      ) : (
        <div 
          className={styles.loadingBar} 
          style={{ width: `${progress}%` }} 
          aria-label={`Loading progress: ${progress}%`}
        ></div>
      )}
    </div>
  );
};

LoadingOverlay.propTypes = {
  isVisible: PropTypes.bool.isRequired,
  progress: PropTypes.number, // Progress from 0 to 100
};

LoadingOverlay.defaultProps = {
  progress: 0, // Default progress is 0%
};

export default LoadingOverlay;
