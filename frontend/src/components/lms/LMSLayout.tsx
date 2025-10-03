import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Badge,
  useTheme,
  useMediaQuery,
  Collapse,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  School,
  LibraryBooks,
  Assignment,
  People,
  Analytics,
  Settings,
  Logout,
  ExpandLess,
  ExpandMore,
  Notifications,
  AccountCircle,
  VideoLibrary,
  SmartToy,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { selectCurrentUser, selectIsInstructor, selectIsAdmin } from '../../store/slices/authSlice';
import { useLogoutUserMutation } from '../../store/api/authApi';
import { logout } from '../../store/slices/authSlice';
import toast from 'react-hot-toast';

const drawerWidth = 280;

const LMSLayout: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const currentUser = useAppSelector(selectCurrentUser);
  const isInstructor = useAppSelector(selectIsInstructor);
  const isAdmin = useAppSelector(selectIsAdmin);

  const [logoutUser] = useLogoutUserMutation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [instructorMenuOpen, setInstructorMenuOpen] = useState(true);
  const [adminMenuOpen, setAdminMenuOpen] = useState(true);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    try {
      await logoutUser().unwrap();
      dispatch(logout());
      toast.success('Logged out successfully');
      navigate('/lms/login');
    } catch (error) {
      dispatch(logout());
      navigate('/lms/login');
    }
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  // Navigation items based on user role
  const studentNavItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/lms/dashboard' },
    { text: 'Browse Courses', icon: <School />, path: '/lms/courses' },
    { text: 'My Courses', icon: <LibraryBooks />, path: '/lms/my-courses' },
    { text: 'Assignments', icon: <Assignment />, path: '/lms/assignments' },
    { text: 'AI Assistant', icon: <SmartToy />, path: '/lms/ai-assistant' },
  ];

  // Admin navigation items (instructors and admins will both see these)
  const adminNavItems = [
    { text: 'Admin Dashboard', icon: <Dashboard />, path: '/lms/admin' },
    { text: 'Course Management', icon: <VideoLibrary />, path: '/lms/admin/courses' },
    { text: 'Organizations', icon: <People />, path: '/lms/admin/organizations' },
    { text: 'User Management', icon: <People />, path: '/lms/admin/users' },
    { text: 'Students', icon: <School />, path: '/lms/admin/students' },
    { text: 'Platform Analytics', icon: <Analytics />, path: '/lms/admin/analytics' },
    { text: 'Settings', icon: <Settings />, path: '/lms/admin/settings' },
  ];

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo/Title Section */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <School sx={{ fontSize: 32, color: 'primary.main' }} />
          <Box>
            <Typography variant="h6" fontWeight="bold">
              LMS Platform
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Learning Management System
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Navigation Items */}
      <Box sx={{ flex: 1, overflow: 'auto', py: 2 }}>
        {/* Student Navigation */}
        <List>
          {studentNavItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ px: 2 }}>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  borderRadius: 2,
                  mb: 0.5,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.light',
                    '& .MuiListItemIcon-root': {
                      color: 'primary.main',
                    },
                  },
                }}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        {/* Admin Section - Show for both instructors and admins */}
        {(isInstructor || isAdmin) && (
          <>
            <Divider sx={{ mx: 2, my: 1 }} />
            <List>
              <ListItemButton
                onClick={() => setAdminMenuOpen(!adminMenuOpen)}
                sx={{ px: 4 }}
              >
                <ListItemText primary="Admin Tools" primaryTypographyProps={{ fontWeight: 600 }} />
                {adminMenuOpen ? <ExpandLess /> : <ExpandMore />}
              </ListItemButton>
              <Collapse in={adminMenuOpen} timeout="auto" unmountOnExit>
                {adminNavItems.map((item) => (
                  <ListItem key={item.text} disablePadding sx={{ pl: 4, pr: 2 }}>
                    <ListItemButton
                      selected={location.pathname === item.path}
                      onClick={() => handleNavigation(item.path)}
                      sx={{
                        borderRadius: 2,
                        mb: 0.5,
                        '&.Mui-selected': {
                          backgroundColor: 'primary.light',
                          '& .MuiListItemIcon-root': {
                            color: 'primary.main',
                          },
                        },
                      }}
                    >
                      <ListItemIcon>{item.icon}</ListItemIcon>
                      <ListItemText primary={item.text} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </Collapse>
            </List>
          </>
        )}
      </Box>

      {/* User Info Section */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            {currentUser?.firstName?.[0]}{currentUser?.lastName?.[0]}
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" fontWeight="bold">
              {currentUser?.firstName} {currentUser?.lastName}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {currentUser?.role}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          backgroundColor: 'background.paper',
          color: 'text.primary',
          borderBottom: 1,
          borderColor: 'divider',
          boxShadow: 'none',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {/* Dynamic page title based on route */}
          </Typography>

          {/* Notifications */}
          <IconButton color="inherit" sx={{ mr: 1 }}>
            <Badge badgeContent={4} color="error">
              <Notifications />
            </Badge>
          </IconButton>

          {/* Profile Menu */}
          <IconButton
            onClick={handleProfileMenuOpen}
            color="inherit"
          >
            <AccountCircle />
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem onClick={() => { handleNavigation('/lms/profile'); handleProfileMenuClose(); }}>
              <ListItemIcon>
                <AccountCircle fontSize="small" />
              </ListItemIcon>
              Profile
            </MenuItem>
            <MenuItem onClick={() => { handleNavigation('/lms/settings'); handleProfileMenuClose(); }}>
              <ListItemIcon>
                <Settings fontSize="small" />
              </ListItemIcon>
              Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          mt: 8, // Account for AppBar height
          backgroundColor: 'grey.50',
          minHeight: '100vh',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default LMSLayout;