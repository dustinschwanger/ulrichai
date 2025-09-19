import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { Box, Typography, Button } from '@mui/material';
import { Lock } from '@mui/icons-material';
import { useAppSelector } from '../../store/hooks';
import { selectUserRole } from '../../store/slices/authSlice';

interface RoleBasedRouteProps {
  allowedRoles: Array<'student' | 'instructor' | 'admin' | 'super_admin'>;
  redirectTo?: string;
  children?: React.ReactNode;
}

const RoleBasedRoute: React.FC<RoleBasedRouteProps> = ({
  allowedRoles,
  redirectTo = '/lms/dashboard',
  children,
}) => {
  const userRole = useAppSelector(selectUserRole);

  // Check if user has one of the allowed roles
  const hasRequiredRole = userRole && allowedRoles.includes(userRole);

  if (!hasRequiredRole) {
    // Show access denied page instead of redirect for better UX
    if (!redirectTo) {
      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100vh',
            gap: 3,
            textAlign: 'center',
            p: 3,
          }}
        >
          <Lock sx={{ fontSize: 64, color: 'error.main' }} />
          <Typography variant="h4" gutterBottom>
            Access Denied
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 500 }}>
            You don't have permission to access this page.
            {allowedRoles.includes('instructor' as any) &&
              ' This page is only available to instructors and administrators.'}
            {allowedRoles.includes('admin' as any) &&
              ' This page is only available to administrators.'}
          </Typography>
          <Button
            variant="contained"
            href="/lms/dashboard"
            sx={{ mt: 2 }}
          >
            Go to Dashboard
          </Button>
        </Box>
      );
    }

    return <Navigate to={redirectTo} replace />;
  }

  // Render children or outlet for nested routes
  return children ? <>{children}</> : <Outlet />;
};

export default RoleBasedRoute;