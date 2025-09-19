import React, { useState, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Chat from './components/Chat';
import Admin from './components/Admin';
import { theme, darkTheme } from './styles/theme';
import './App.css';

function App() {
  // Theme state - can be controlled by user preference later
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Select theme based on mode
  const currentTheme = useMemo(
    () => (isDarkMode ? darkTheme : theme),
    [isDarkMode]
  );

  return (
    <ThemeProvider theme={currentTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<Layout isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} />}>
            <Route index element={<Chat />} />
            <Route path="admin" element={<Admin />} />
            {/* Placeholder routes for new features */}
            <Route path="dashboard" element={<div style={{ padding: 20 }}>Dashboard Coming Soon</div>} />
            <Route path="learning" element={<div style={{ padding: 20 }}>Learning Center Coming Soon</div>} />
            <Route path="analytics" element={<div style={{ padding: 20 }}>Analytics Coming Soon</div>} />
            <Route path="settings" element={<div style={{ padding: 20 }}>Settings Coming Soon</div>} />
            <Route path="help" element={<div style={{ padding: 20 }}>Help & Support Coming Soon</div>} />
          </Route>
        </Routes>
      </Router>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: isDarkMode ? '#1E293B' : '#FFFFFF',
            color: isDarkMode ? '#F9FAFB' : '#111827',
            border: `1px solid ${isDarkMode ? '#334155' : '#E5E7EB'}`,
            borderRadius: '8px',
            fontSize: '14px',
          },
          success: {
            iconTheme: {
              primary: '#10B981',
              secondary: '#FFFFFF',
            },
          },
          error: {
            iconTheme: {
              primary: '#EF4444',
              secondary: '#FFFFFF',
            },
          },
        }}
      />
    </ThemeProvider>
  );
}

export default App;