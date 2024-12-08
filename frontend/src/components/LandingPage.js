// LandingPage.js
import React, { useRef } from "react";
import { useNavigate } from "react-router-dom";
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import logo from '../assets/ventaura-logo-full-small-dark.png'; 

const LandingPage = () => {
  const navigate = useNavigate();
  const featuresRef = useRef(null);

  const scrollToContent = (e) => {
    e.preventDefault();  // Prevent default behavior
    e.stopPropagation(); // Stop event bubbling
    featuresRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start' 
    });
  };
  
  return (
    <div className={layoutStyles['landing-container']}>
      {/* Fixed Left Side */}
      <div className={layoutStyles['landing-left']}>
        <img 
          src={logo}
          alt="Ventaura Logo" 
          className={layoutStyles['landing-logo']}
        />
        <button 
          onClick={() => navigate("/login")} 
          className={buttonStyles['button-56']}
        >
          Get Started
        </button>
      </div>

      {/* Scrollable Right Side */}
      <div className={layoutStyles['landing-right']}>
        <div className={layoutStyles['content-wrapper']}>
          {/* Hero Section */}
          <section className={layoutStyles['hero-section']}>
            <h1>Discover Your Next Experience</h1>
            <p>Personalized event recommendations that match your interests</p>
            <div 
                className={layoutStyles['scroll-indicator']} 
                onClick={scrollToContent}
            >
                <div className={layoutStyles['scroll-arrow']}></div>
            </div>
          </section>
          {/* How It Works Section */}
          <section ref={featuresRef} className={layoutStyles['how-it-works']}>
            <h2>How It Works</h2>
            <div className={layoutStyles['steps-container']}>
              <div className={layoutStyles['step-card']}>
                <span className={layoutStyles['step-number']}>1</span>
                <h3>Create Account</h3>
                <p>Sign up and tell us what you love</p>
              </div>
              <div className={layoutStyles['step-card']}>
                <span className={layoutStyles['step-number']}>2</span>
                <h3>Set Preferences</h3>
                <p>Customize your event preferences</p>
              </div>
              <div className={layoutStyles['step-card']}>
                <span className={layoutStyles['step-number']}>3</span>
                <h3>Discover Events</h3>
                <p>Get personalized recommendations</p>
              </div>
            </div>
          </section>

          {/* Feature Cards */}
          <div className={layoutStyles['feature-cards']}>
            <div className={layoutStyles['feature-card']}>
              <h3>Discover</h3>
              <p>Find events that match your unique interests and preferences</p>
            </div>
            <div className={layoutStyles['feature-card']}>
              <h3>Connect</h3>
              <p>Join a community of like-minded event enthusiasts</p>
            </div>
            <div className={layoutStyles['feature-card']}>
              <h3>Experience</h3>
              <p>Create unforgettable memories at carefully curated events</p>
            </div>
            <div className={layoutStyles['feature-card']}>
              <h3>Share</h3>
              <p>Post your own events and share them with the community</p>
            </div>
          </div>


          {/* Testimonial Section - Enhanced */}
          <section className={layoutStyles['testimonial-section']}>
            <h2>What People Say</h2>
            <blockquote>
              "Finally, an event platform that gets me"
            </blockquote>
          </section>

          {/* New Call to Action Section */}
          <section className={layoutStyles['cta-section']}>
            <h2>Ready to Start Your Journey?</h2>
            <p>Join thousands of others discovering amazing events every day</p>
            <button 
              onClick={() => navigate("/login")} 
              className={buttonStyles['button-56']}
            >
              Get Started Now
            </button>
          </section>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
