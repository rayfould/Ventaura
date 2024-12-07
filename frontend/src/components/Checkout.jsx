// Checkout.jsx
import React from 'react';

// Import shared CSS modules
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';


const Checkout = () => {
  return (
    <div className={layoutStyles.container}>
      <div className={layoutStyles.contentBox}>
        <section className={layoutStyles.section}>
          <h1 className={layoutStyles.heading}>Add Event to Database</h1>
          <h4 className={layoutStyles.subheading}>Purchase a place on our website</h4>
          <div className={layoutStyles.imageContainer}>
            <img
              alt="Advertising Word Cloud"
              src="https://thumbs.dreamstime.com/b/advertising-word-cloud-business-concept-56936998.jpg"
              width="140"
              height="160"
              className={layoutStyles.image}
            />
          </div>
        </section>

        <form 
          action="http://localhost:5152/api/create-checkout-session" 
          method="POST"
          className={layoutStyles.form}
        >
          <button 
            id="submit" 
            role="link"
            className={buttonStyles.primaryButton}
          >
            Buy
          </button>
        </form>
      </div>
    </div>
  );
};

export default Checkout;
