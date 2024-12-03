import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles.css'; // Ensure to import global CSS

const AddEvent = () => {
  const history = useNavigate();

  return (
    <div className="add-event-container">
      <header className="header">
        <h2 className="page-title">Add Event Here:</h2>
      </header>

      <form className="event-form">
        {/* Submit Button - only enabled if the form is valid */}
        <form action="http://localhost:5152/api/create-checkout-session" method="POST">
          <button 
            type="submit" 
            role="link" 
            className="submit-button" 
          >
            Make Payment
          </button>
        </form>
      </form>
    </div>
  );
};

export default AddEvent;
