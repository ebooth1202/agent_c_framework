import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import AppRoutes from '@/Routes';
import { SessionProvider } from '@/contexts/SessionContext';

function App() {
  return (
    <SessionProvider>
      <Router>
        <AppRoutes />
      </Router>
    </SessionProvider>
  );
}

export default App;