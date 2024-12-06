// src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './styles/index.css';  // Only import global styles here

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
