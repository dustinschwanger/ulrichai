import React, { useState, useMemo, Suspense, lazy, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ThemeProvider, CssBaseline, CircularProgress, Box } from '@mui/material';
import { Toaster } from 'react-hot-toast';
import { theme, darkTheme } from './styles/theme';
import './App.css';

// Lazy load components for code splitting
const Layout = lazy(() => import('./components/Layout'));
const Chat = lazy(() => import('./components/Chat'));
const Admin = lazy(() => import('./components/Admin'));

// Loading fallback component
const LoadingFallback = () => (
  <Box
    sx={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      width: '100%',
    }}
  >
    <CircularProgress size={60} />
  </Box>
);

// Google Analytics page tracking component
const GAPageTracker = () => {
  const location = useLocation();

  useEffect(() => {
    // Track page view on route change
    if (typeof window.gtag !== 'undefined') {
      window.gtag('event', 'page_view', {
        page_path: location.pathname + location.search,
        page_title: document.title,
      });
    }
  }, [location]);

  return null;
};

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
        <GAPageTracker />
        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            {/* Root redirects to chat */}
            <Route path="/" element={<Navigate to="/chat" replace />} />

            {/* AI Chat Routes */}
            <Route path="/chat" element={<Layout isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} />}>
              <Route index element={<Chat />} />
              <Route path="admin" element={<Admin />} />
            </Route>
          </Routes>
        </Suspense>
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