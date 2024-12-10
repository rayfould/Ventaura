// src/components/Footer.jsx
import React from 'react';
import styles from '../styles/modules/Footer.module.css';
import { Link } from 'react-router-dom'; // Ensure react-router-dom is installed
import { FaFacebookF, FaTwitter, FaInstagram, FaLinkedinIn } from 'react-icons/fa';
import logo from '../assets/ventaura-logo-full-small-dark.png'; 

const Footer = () => {
  const handleSubscribe = (e) => {
    e.preventDefault();
    const email = e.target.email.value;
    // Implement subscription logic here (e.g., API call)
    alert(`Subscribed with ${email}`);
    e.target.reset();
  };

  return (
    <footer className={styles.footer}>
      <div className={styles.footerContainer}>
        {/* Logo Section */}
        <div className={styles.logoSection}>
          <img src={logo} alt="Your Company Logo" className={styles.logo} />
        </div>

        {/* Navigation Links */}
        <div className={styles.navSection}>
          <h4 className={styles.sectionTitle}>Navigate</h4>
          <ul className={styles.navList}>
            <li><Link to="/for-you" className={styles.navLink}>For You</Link></li>
            <li><Link to="/global" className={styles.navLink}>Global</Link></li>
            <li><Link to="/post-event-page" className={styles.navLink}>Post Event</Link></li>
            <li><Link to="/about" className={styles.navLink}>About Us</Link></li>
            <li><Link to="/contact" className={styles.navLink}>Contact Us</Link></li>
            {/* Add more links as needed */}
          </ul>
        </div>

        {/* Legal Information */}
        <div className={styles.legalSection}>
          <h4 className={styles.sectionTitle}>Legal</h4>
          <ul className={styles.legalList}>
            <li><Link to="/privacy" className={styles.navLink}>Privacy Policy</Link></li>
            <li><Link to="/terms" className={styles.navLink}>Terms of Service</Link></li>
            <li><Link to="/disclaimer" className={styles.navLink}>Disclaimer</Link></li>
            {/* Add more legal links as needed */}
          </ul>
        </div>

        {/* Social Media Links (Optional) */}
        <div className={styles.socialSection}>
          <h4 className={styles.sectionTitle}>Connect</h4>
          <div className={styles.socialIcons}>
            <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" aria-label="Facebook" className={styles.socialLink}>
              <FaFacebookF />
            </a>
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" aria-label="Twitter" className={styles.socialLink}>
              <FaTwitter />
            </a>
            <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" aria-label="Instagram" className={styles.socialLink}>
              <FaInstagram />
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn" className={styles.socialLink}>
              <FaLinkedinIn />
            </a>
            {/* Add more social links as needed */}
          </div>
        </div>

        {/* Newsletter Section */}
        <div className={styles.newsletterSection}>
          <h4 className={styles.sectionTitle}>Newsletter</h4>
          <form className={styles.newsletterForm} onSubmit={handleSubscribe}>
            <input 
              type="email" 
              name="email"
              placeholder="Your email address" 
              className={styles.newsletterInput} 
              required 
              aria-label="Email Address"
            />
            <button type="submit" className={styles.subscribeButton}>Subscribe</button>
          </form>
        </div>
      </div>

      {/* Footer Bottom */}
      <div className={styles.footerBottom}>
        <p>&copy; {new Date().getFullYear()} Ventaura. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
