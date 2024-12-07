// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/variables.css'; 


// Optional: Import global CSS if necessary (e.g., CSS resets)
// If you have global styles, consider converting them to a CSS module or keeping minimal global CSS
// import './styles/global.css'; 

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
