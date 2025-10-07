import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import FinanceNERTool from "./FinanceNERTool";
import Login from "./Login";
import Register from "./Register";
import PrivateRoute from "./PrivateRoute";

function App() {
  return (
    <Router>
      <div>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected routes */}
          <Route 
            path="/ner-tool" 
            element={
              <PrivateRoute>
                <FinanceNERTool />
              </PrivateRoute>
            } 
          />
          
          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/ner-tool" replace />} />
          
          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/ner-tool" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
