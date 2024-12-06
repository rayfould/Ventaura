// Canceled.jsx
import React from 'react';
import { Link } from 'react-router-dom';

// Import shared CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import navigationStyles from '../styles/modules/navigation.module.css';

const Canceled = () => {
  return (
    <div className={layoutStyles.container}>
      <div className={layoutStyles.contentBox}>
        <header className={layoutStyles.header}>
          <div className={layoutStyles.logo}></div> {/* Ensure logo styling is in layout.module.css */}
        </header>
        <div className={layoutStyles.messageBox}>
          <h1 className={layoutStyles.heading}>Your payment was canceled</h1>
          <Link to="/for-you" className={buttonStyles.linkButton}>
            Return to For You page
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Canceled;
