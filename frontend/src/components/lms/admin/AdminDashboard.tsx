import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Paper,
  IconButton,
  Stack,
  Tab,
  Tabs,
  Avatar,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  Divider,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Dashboard,
  School,
  People,
  Assessment,
  Settings,
  Add,
  TrendingUp,
  Schedule,
  Assignment,
  Group,
  Search,
  MoreVert,
  Edit,
  Visibility,
  Delete,
  ContentCopy,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useGetCoursesQuery } from '../../../features/lms/courseBuilderSlice';
import { useSelector } from 'react-redux';
import { RootState } from '../../../store/store';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const user = useSelector((state: RootState) => state.auth.user);
  const [tabValue, setTabValue] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: courses, isLoading } = useGetCoursesQuery();

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Stats cards data
  const stats = [
    {
      title: 'Total Courses',
      value: courses?.length || 0,
      icon: <School />,
      color: '#1976d2',
      trend: '+12%',
    },
    {
      title: 'Active Students',
      value: '1,234',
      icon: <People />,
      color: '#2e7d32',
      trend: '+8%',
    },
    {
      title: 'Course Completions',
      value: '892',
      icon: <Assignment />,
      color: '#ed6c02',
      trend: '+23%',
    },
    {
      title: 'Avg. Engagement',
      value: '87%',
      icon: <TrendingUp />,
      color: '#9c27b0',
      trend: '+5%',
    },
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          <Dashboard sx={{ mr: 2, verticalAlign: 'middle' }} />
          Admin Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome back, {user?.name || 'Administrator'}
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                  <Box>
                    <Typography color="text.secondary" variant="body2" gutterBottom>
                      {stat.title}
                    </Typography>
                    <Typography variant="h4" component="div">
                      {stat.value}
                    </Typography>
                    <Chip
                      label={stat.trend}
                      size="small"
                      color="success"
                      sx={{ mt: 1 }}
                    />
                  </Box>
                  <Avatar
                    sx={{
                      bgcolor: stat.color,
                      width: 56,
                      height: 56,
                    }}
                  >
                    {stat.icon}
                  </Avatar>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Main Content Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="admin dashboard tabs"
          sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
        >
          <Tab label="Courses" />
          <Tab label="Students" />
          <Tab label="Instructors" />
          <Tab label="Analytics" />
          <Tab label="Settings" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {/* Courses Tab */}
          <Box sx={{ px: 2 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
              <TextField
                placeholder="Search courses..."
                variant="outlined"
                size="small"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
                sx={{ minWidth: 300 }}
              />
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => navigate('/lms/admin/courses/new')}
              >
                Create Course
              </Button>
            </Stack>

            <Grid container spacing={3}>
              {courses?.filter((course: any) => 
                course.title.toLowerCase().includes(searchQuery.toLowerCase())
              ).map((course: any) => (
                <Grid item xs={12} md={6} lg={4} key={course.id}>
                  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    {course.thumbnail_url ? (
                      <Box
                        sx={{
                          height: 140,
                          backgroundImage: `url(${course.thumbnail_url})`,
                          backgroundSize: 'cover',
                          backgroundPosition: 'center',
                        }}
                      />
                    ) : (
                      <Box
                        sx={{
                          height: 140,
                          bgcolor: 'primary.light',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <School sx={{ fontSize: 60, color: 'primary.contrastText' }} />
                      </Box>
                    )}
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" gutterBottom noWrap>
                        {course.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        mb: 2,
                      }}>
                        {course.description || 'No description available'}
                      </Typography>
                      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                        <Chip
                          label={course.is_published ? 'Published' : 'Draft'}
                          size="small"
                          color={course.is_published ? 'success' : 'default'}
                        />
                        {course.versions?.length > 0 && (
                          <Chip
                            label={`${course.versions.length} versions`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Stack>
                    </CardContent>
                    <CardActions sx={{ px: 2, pb: 2 }}>
                      <Button
                        size="small"
                        startIcon={<Visibility />}
                        onClick={() => navigate(`/lms/course/${course.id}/learn`)}
                      >
                        Preview
                      </Button>
                      <Button
                        size="small"
                        onClick={() => navigate(`/lms/admin/courses/${course.id}/versions`)}
                      >
                        Versions
                      </Button>
                      <Button
                        size="small"
                        startIcon={<Edit />}
                        onClick={() => navigate(`/lms/instructor/courses/${course.id}/edit`)}
                      >
                        Edit
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {/* Students Tab */}
          <Box sx={{ px: 2 }}>
            <Typography variant="h6" gutterBottom>
              Student Management
            </Typography>
            <List>
              {[1, 2, 3, 4, 5].map((i) => (
                <React.Fragment key={i}>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar>{`S${i}`}</Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={`Student ${i}`}
                      secondary={`student${i}@example.com`}
                    />
                    <ListItemSecondaryAction>
                      <Chip label="Active" size="small" color="success" />
                    </ListItemSecondaryAction>
                  </ListItem>
                  {i < 5 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {/* Instructors Tab */}
          <Box sx={{ px: 2 }}>
            <Typography variant="h6" gutterBottom>
              Instructor Management
            </Typography>
            <List>
              {[1, 2, 3].map((i) => (
                <React.Fragment key={i}>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar>{`I${i}`}</Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={`Instructor ${i}`}
                      secondary={`${3 * i} courses assigned`}
                    />
                    <ListItemSecondaryAction>
                      <Button size="small">View Courses</Button>
                    </ListItemSecondaryAction>
                  </ListItem>
                  {i < 3 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          {/* Analytics Tab */}
          <Box sx={{ px: 2 }}>
            <Typography variant="h6" gutterBottom>
              Analytics & Reports
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Course Completion Rate
                  </Typography>
                  <Typography variant="h3" color="primary">
                    78%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Average across all courses
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Student Satisfaction
                  </Typography>
                  <Typography variant="h3" color="primary">
                    4.6/5.0
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Based on 523 reviews
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={4}>
          {/* Settings Tab */}
          <Box sx={{ px: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Settings
            </Typography>
            <List>
              <ListItem button onClick={() => navigate('/lms/admin/settings/organization')}>
                <ListItemText
                  primary="Organization Settings"
                  secondary="Manage organization details and branding"
                />
              </ListItem>
              <Divider />
              <ListItem button onClick={() => navigate('/lms/admin/settings/permissions')}>
                <ListItemText
                  primary="Permissions & Roles"
                  secondary="Configure user roles and access levels"
                />
              </ListItem>
              <Divider />
              <ListItem button onClick={() => navigate('/lms/admin/settings/integrations')}>
                <ListItemText
                  primary="Integrations"
                  secondary="Manage third-party integrations"
                />
              </ListItem>
            </List>
          </Box>
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default AdminDashboard;