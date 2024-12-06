import React from 'react';
import styles from '../styles';

const Checkout = () => {
  return (
    <div className={styles.srRoot}>
      <div className={styles.srMain}>
        <section className={styles.container}>
          <div>
            <h1 className={styles.heading}>Add event to database</h1>
            <h4 className={styles.subheading}>Purchase a place on our website</h4>
            <div className={styles.pashaImage}>
              <img
                alt="Random asset from Picsum"
                src="https://thumbs.dreamstime.com/b/advertising-word-cloud-business-concept-56936998.jpg"
                width="140"
                height="160"
              />
            </div>
          </div>

          <form 
            action="http://localhost:5152/api/create-checkout-session" 
            method="POST"
            className={styles.checkoutForm}
          >
            <button 
              id="submit" 
              role="link"
              className={styles.submitButton}
            >
              Buy
            </button>
          </form>
        </section>
      </div>
    </div>
  );
};

export default Checkout;
