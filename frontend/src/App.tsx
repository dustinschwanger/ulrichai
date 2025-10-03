import React, { useState, useMemo, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline, CircularProgress, Box } from '@mui/material';
import { Toaster } from 'react-hot-toast';
import AuthCheck from './components/auth/AuthCheck';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { theme, darkTheme } from './styles/theme';
import './App.css';

// Eager load critical components
import Login from './components/auth/Login';
import Register from './components/auth/Register';

// Lazy load other components for code splitting
const Layout = lazy(() => import('./components/Layout'));
const Chat = lazy(() => import('./components/Chat'));
const Admin = lazy(() => import('./components/Admin'));
const LMSLayout = lazy(() => import('./components/lms/LMSLayout'));
const StudentDashboard = lazy(() => import('./components/lms/dashboards/StudentDashboard'));
const CourseCatalog = lazy(() => import('./components/lms/courses/CourseCatalog'));
const CourseDetail = lazy(() => import('./components/lms/courses/CourseDetail'));
const MyCourses = lazy(() => import('./components/lms/courses/MyCourses'));
const CourseViewer = lazy(() => import('./components/lms/courses/CourseViewer'));
const CoursePreview = lazy(() => import('./components/lms/CoursePreview'));
const InstructorDashboard = lazy(() => import('./components/lms/instructor/InstructorDashboard'));
const CourseBuilder = lazy(() => import('./components/lms/instructor/CourseBuilder/CourseBuilder'));
const CourseEditor = lazy(() => import('./components/lms/instructor/CourseBuilder/CourseEditor'));
const AdminDashboard = lazy(() => import('./components/lms/admin/AdminDashboard'));
const CourseVersions = lazy(() => import('./components/lms/admin/CourseVersions'));

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
          <Suspense fallback={<LoadingFallback />}>
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

                {/* Course Preview Route */}
                <Route path="courses/:courseId/preview" element={<CoursePreview />} />

                {/* Admin Routes - Consolidated for both instructors and admins */}
                <Route path="admin">
                  <Route index element={<AdminDashboard />} />
                  <Route path="dashboard" element={<AdminDashboard />} />
                  <Route path="courses" element={<CourseBuilder />} />
                  <Route path="courses/new" element={<CourseBuilder />} />
                  <Route path="courses/:courseId" element={<CourseEditor />} />
                  <Route path="courses/:courseId/versions" element={<CourseVersions />} />
                  <Route path="courses/:courseId/version/:versionId" element={<CourseEditor />} />
                  <Route path="organizations" element={<div style={{ padding: 20 }}>Organizations Coming Soon</div>} />
                  <Route path="users" element={<div style={{ padding: 20 }}>User Management Coming Soon</div>} />
                  <Route path="students" element={<div style={{ padding: 20 }}>Students Coming Soon</div>} />
                  <Route path="analytics" element={<div style={{ padding: 20 }}>Platform Analytics Coming Soon</div>} />
                  <Route path="settings" element={<div style={{ padding: 20 }}>Admin Settings Coming Soon</div>} />
                  <Route path="settings/:section" element={<div style={{ padding: 20 }}>Settings Section Coming Soon</div>} />
                </Route>

                {/* Legacy instructor routes redirect to admin */}
                <Route path="instructor/*" element={<Navigate to="/lms/admin" replace />} />
              </Route>
            </Route>
          </Routes>
          </Suspense>
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