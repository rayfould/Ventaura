import React, { createContext, useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoadingOverlay from './components/LoadingOverlay';
import Login from './components/Login';
import CreateAccount from './components/CreateAccount';
import LandingPage from './components/LandingPage';
import ForYou from './components/ForYou';
import ContactUs from './components/ContactUs';
import AboutUs from './components/AboutUs';
import GlobalPage from './components/GlobalPage';
import AddEvent from './components/AddEvent';
import Checkout from './components/Checkout';
import Success from './components/Success';
import Canceled from './components/Canceled';
import Settings from './components/Settings';

export const LoadingContext = createContext();

const ProtectedRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem("userId");
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (isLoading) {
      setIsVisible(true);
    } else {
      const timer = setTimeout(() => setIsVisible(false), 600);
      return () => clearTimeout(timer);
    }
  }, [isLoading]);

  return (
    <LoadingContext.Provider value={{ isLoading, setIsLoading }}>
      <Router>
        {isVisible ? <LoadingOverlay isLoading={isLoading} /> : null}
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/create-account" element={<CreateAccount />} />
          <Route path="/" element={<LandingPage />} />
          <Route path="/for-you" element={<ProtectedRoute><ForYou /></ProtectedRoute>} />
          <Route path="/contact-us" element={<ProtectedRoute><ContactUs /></ProtectedRoute>} />
          <Route path="/about-us" element={<ProtectedRoute><AboutUs /></ProtectedRoute>} />
          <Route path="/global-page" element={<ProtectedRoute><GlobalPage /></ProtectedRoute>} />
          <Route path="/post-event-page" element={<ProtectedRoute><AddEvent /></ProtectedRoute>} />
          <Route path="/checkout" element={<ProtectedRoute><Checkout /></ProtectedRoute>} />
          <Route path="/success.html" element={<ProtectedRoute><Success /></ProtectedRoute>} />
          <Route path="/canceled.html" element={<ProtectedRoute><Canceled /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </LoadingContext.Provider>
  );
}

export default App;
