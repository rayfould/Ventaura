import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "./components/LandingPage";
import Login from "./components/Login";
import CreateAccount from "./components/CreateAccount";
import ForYou from "./components/ForYou";
import ContactUs from "./components/ContactUs";
import AboutUs from "./components/AboutUs";
import GlobalPage from "./components/GlobalPage"; 
import AddEvent from "./components/AddEvent"; 
import Canceled from './components/Canceled.jsx';
import Success from './components/Success.jsx';
import Checkout from './components/Checkout.jsx';
import Settings from "./components/Settings.js"; 
import styles from './/styles';

function App() {
  return (
    <Router>
      <Routes>
        {/* Remove or comment out these if you want to bypass them */}
        {/* <Route path="/login" element={<Login />} />
        <Route path="/create-account" element={<CreateAccount />} /> */}
        
        {/* Direct to ForYou from both / and /login */}
        <Route path="/" element={<Navigate to="/for-you" replace />} />
        <Route path="/login" element={<Navigate to="/for-you" replace />} />
        
        {/* Your existing routes */}
        <Route path="/for-you" element={<ForYou />} />
        <Route path="/contact-us" element={<ContactUs />} />
        <Route path="/about-us" element={<AboutUs />} />
        <Route path="/global-page" element={<GlobalPage />} />
        <Route path="/post-event-page" element={<AddEvent />} />
        <Route path="/Checkout" element={<Checkout />} />
        <Route path="/success.html" element={<Success />} />
        <Route path="/canceled.html" element={<Canceled />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Router>
  );
}

export default App;
