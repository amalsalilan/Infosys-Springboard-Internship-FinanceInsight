import React from 'react';
import { Toaster } from 'react-hot-toast';
import { Dashboard } from './components/dashboard/Dashboard';

function App() {
  return (
    <>
      <Dashboard />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#fff',
            color: '#374151',
            borderRadius: '8px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
          },
        }}
      />
    </>
  );
}

export default App;