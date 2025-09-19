import React, { useState, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Chat from './components/Chat';
import Admin from './components/Admin';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import AuthCheck from './components/auth/AuthCheck';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LMSLayout from './components/lms/LMSLayout';
import StudentDashboard from './components/lms/dashboards/StudentDashboard';
import CourseCatalog from './components/lms/courses/CourseCatalog';
import CourseDetail from './components/lms/courses/CourseDetail';
import MyCourses from './components/lms/courses/MyCourses';
import CourseViewer from './components/lms/courses/CourseViewer';
import InstructorDashboard from './components/lms/instructor/InstructorDashboard';
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
      <AuthCheck>
        <Router>
          <Routes>
            {/* Root redirects to LMS */}
            <Route path="/" element={<Navigate to="/lms" replace />} />

            {/* Public LMS Routes */}
            <Route path="/lms/login" element={<Login />} />
            <Route path="/lms/register" element={<Register />} />

            {/* AI Chat App (preserved as separate feature) */}
            <Route path="/chat" element={<Layout isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} />}>
              <Route index element={<Chat />} />
              <Route path="admin" element={<Admin />} />
            </Route>

            {/* Protected LMS Routes */}
            <Route path="/lms" element={<ProtectedRoute />}>
              {/* Course Viewer - Outside LMSLayout for its own layout */}
              <Route path="course/:courseId/learn" element={<CourseViewer />} />

              {/* Routes with LMS Layout */}
              <Route element={<LMSLayout />}>
                <Route index element={<Navigate to="/lms/dashboard" replace />} />
                <Route path="dashboard" element={<StudentDashboard />} />
                <Route path="courses" element={<CourseCatalog />} />
                <Route path="course/:courseId" element={<CourseDetail />} />
                <Route path="my-courses" element={<MyCourses />} />
                <Route path="assignments" element={<div style={{ padding: 20 }}>Assignments Coming Soon</div>} />
                <Route path="profile" element={<div style={{ padding: 20 }}>Profile Coming Soon</div>} />
                <Route path="settings" element={<div style={{ padding: 20 }}>Settings Coming Soon</div>} />

                {/* AI Assistant integrated within LMS */}
                <Route path="ai-assistant" element={<Chat />} />

                {/* Instructor Routes */}
                <Route path="instructor">
                  <Route index element={<InstructorDashboard />} />
                  <Route path="dashboard" element={<InstructorDashboard />} />
                  <Route path="courses" element={<InstructorDashboard />} />
                  <Route path="create-course" element={<div style={{ padding: 20 }}>Create Course Coming Soon</div>} />
                  <Route path="students" element={<div style={{ padding: 20 }}>Students Coming Soon</div>} />
                  <Route path="analytics" element={<div style={{ padding: 20 }}>Analytics Coming Soon</div>} />
                </Route>

                {/* Admin Routes */}
                <Route path="admin">
                  <Route path="organizations" element={<div style={{ padding: 20 }}>Organizations Coming Soon</div>} />
                  <Route path="users" element={<div style={{ padding: 20 }}>User Management Coming Soon</div>} />
                  <Route path="analytics" element={<div style={{ padding: 20 }}>Platform Analytics Coming Soon</div>} />
                  <Route path="settings" element={<div style={{ padding: 20 }}>Admin Settings Coming Soon</div>} />
                </Route>
              </Route>
            </Route>
          </Routes>
        </Router>
      </AuthCheck>
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