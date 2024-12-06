import React from 'react';
import {Link} from 'react-router-dom';
import styles from '../styles';

const Canceled = () => {
  return (
    <div className={styles.container}>
      <div className={styles.srRoot}>
        <div className={styles.srMain}>
          <header className={styles.srHeader}>
            <div className={styles.srHeaderLogo}></div>
          </header>
          <div className={`${styles.srPaymentSummary} ${styles.completedView}`}>
            <h1 className={styles.heading}>Your payment was canceled</h1>
            <Link to="/for-you" className={styles.link}>Return to For You page</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Canceled;
