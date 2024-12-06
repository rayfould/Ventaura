import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
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


// Create a ProtectedRoute component
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem("userId"); // Check if user is logged in
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/create-account" element={<CreateAccount />} />
        <Route path="/" element={<LandingPage />} />
        
        {/* Protected routes */}
        <Route path="/for-you" element={
          <ProtectedRoute>
            <ForYou />
          </ProtectedRoute>
        } />
        <Route path="/contact-us" element={
          <ProtectedRoute>
            <ContactUs />
          </ProtectedRoute>
        } />
        <Route path="/about-us" element={
          <ProtectedRoute>
            <AboutUs />
          </ProtectedRoute>
        } />
        <Route path="/global-page" element={
          <ProtectedRoute>
            <GlobalPage />
          </ProtectedRoute>
        } />
        <Route path="/post-event-page" element={
          <ProtectedRoute>
            <AddEvent />
          </ProtectedRoute>
        } />
        <Route path="/checkout" element={
          <ProtectedRoute>
            <Checkout />
          </ProtectedRoute>
        } />
        <Route path="/success.html" element={
          <ProtectedRoute>
            <Success />
          </ProtectedRoute>
        } />
        <Route path="/canceled.html" element={
          <ProtectedRoute>
            <Canceled />
          </ProtectedRoute>
        } />
        <Route path="/settings" element={
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        } />
        
        {/* Catch all route - redirect to login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
