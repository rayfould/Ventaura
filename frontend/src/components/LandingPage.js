// LandingPage.js
import React from "react";
import { useNavigate } from "react-router-dom";
import layoutStyles from '../styles/layout.module.css';
import buttonStyles from '../styles/modules/buttons.module.css';
import logo from '../assets/ventaura-logo-full-small-dark.png'; 

const LandingPage = () => {
  const navigate = useNavigate();

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


          {/* Testimonial Section */}
          <section className={layoutStyles['testimonial-section']}>
            <blockquote>
              "Finally, an event platform that gets me"
            </blockquote>
          </section>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
