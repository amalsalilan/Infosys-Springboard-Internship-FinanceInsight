import React from 'react';
import { Navigate } from 'react-router-dom';

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  
  // Check if token exists and is not expired
  const isAuthenticated = () => {
    if (!token) {
      return false;
    }
    
    try {
      // Decode JWT token to check expiration
      const tokenData = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      
      if (tokenData.exp < currentTime) {
        // Token expired, remove it
        localStorage.removeItem('token');
        return false;
      }
      
      return true;
    } catch (error) {
      // Invalid token format
      localStorage.removeItem('token');
      return false;
    }
  };

  return isAuthenticated() ? children : <Navigate to="/login" replace />;
};

export default PrivateRoute;