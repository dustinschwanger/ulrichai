import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Avatar,
  Stack,
  LinearProgress,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add,
  School,
  People,
  TrendingUp,
  MonetizationOn,
  Edit,
  Delete,
  MoreVert,
  Visibility,
  Assessment,
  Schedule,
  Star,
  ArrowUpward,
  ArrowDownward,
  CalendarToday,
  Message,
  Assignment,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

const InstructorDashboard = () => {
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);

  // Mock data
  const stats = {
    totalCourses: 6,
    totalStudents: 1847,
    avgRating: 4.6,
    monthlyRevenue: 12450,
    completionRate: 72,
    engagementRate: 85,
  };

  const courses = [
    {
      id: '1',
      title: 'Introduction to Machine Learning',
      students: 456,
      revenue: 4590,
      rating: 4.8,
      status: 'published',
      lastUpdated: '2 days ago',
      completion: 78,
    },
    {
      id: '2',
      title: 'Advanced Python Programming',
      students: 312,
      revenue: 3120,
      rating: 4.7,
      status: 'published',
      lastUpdated: '1 week ago',
      completion: 65,
    },
    {
      id: '3',
      title: 'Data Structures & Algorithms',
      students: 523,
      revenue: 0,
      rating: 4.9,
      status: 'published',
      lastUpdated: '3 days ago',
      completion: 82,
    },
    {
      id: '4',
      title: 'Web Development Bootcamp',
      students: 0,
      revenue: 0,
      rating: 0,
      status: 'draft',
      lastUpdated: '1 hour ago',
      completion: 0,
    },
  ];

  const recentActivity = [
    { type: 'enrollment', student: 'John Doe', course: 'Machine Learning', time: '2 hours ago' },
    { type: 'review', student: 'Jane Smith', course: 'Python Programming', rating: 5, time: '4 hours ago' },
    { type: 'completion', student: 'Mike Johnson', course: 'Data Structures', time: '6 hours ago' },
    { type: 'question', student: 'Sarah Wilson', course: 'Machine Learning', time: '8 hours ago' },
  ];

  const enrollmentData = [
    { month: 'Jan', enrollments: 120 },
    { month: 'Feb', enrollments: 145 },
    { month: 'Mar', enrollments: 168 },
    { month: 'Apr', enrollments: 195 },
    { month: 'May', enrollments: 210 },
    { month: 'Jun', enrollments: 245 },
  ];

  const revenueData = [
    { month: 'Jan', revenue: 8500 },
    { month: 'Feb', revenue: 9200 },
    { month: 'Mar', revenue: 10100 },
    { month: 'Apr', revenue: 11300 },
    { month: 'May', revenue: 11800 },
    { month: 'Jun', revenue: 12450 },
  ];

  const courseDistribution = [
    { name: 'Machine Learning', value: 456, color: '#667eea' },
    { name: 'Python', value: 312, color: '#764ba2' },
    { name: 'Data Structures', value: 523, color: '#f093fb' },
    { name: 'Web Dev', value: 189, color: '#fda4af' },
  ];

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, courseId: string) => {
    setAnchorEl(event.currentTarget);
    setSelectedCourse(courseId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedCourse(null);
  };

  const StatCard = ({ icon, title, value, change, color }: any) => (
    <Paper sx={{ p: 3, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Avatar sx={{ bgcolor: `${color}.light`, color: `${color}.main` }}>
          {icon}
        </Avatar>
        {change && (
          <Chip
            size="small"
            icon={change > 0 ? <ArrowUpward /> : <ArrowDownward />}
            label={`${Math.abs(change)}%`}
            color={change > 0 ? 'success' : 'error'}
            variant="outlined"
          />
        )}
      </Box>
      <Typography variant="h4" fontWeight="600">
        {value}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {title}
      </Typography>
    </Paper>
  );

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" fontWeight="600" gutterBottom>
            Instructor Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage your courses and track student progress
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => navigate('/lms/instructor/create-course')}
          sx={{
            background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
          }}
        >
          Create New Course
        </Button>
      </Box>

      {/* Stats Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<School />}
            title="Total Courses"
            value={stats.totalCourses}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<People />}
            title="Total Students"
            value={stats.totalStudents.toLocaleString()}
            change={12}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<Star />}
            title="Average Rating"
            value={stats.avgRating}
            change={3}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<MonetizationOn />}
            title="Monthly Revenue"
            value={`$${stats.monthlyRevenue.toLocaleString()}`}
            change={8}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Enrollment Trends
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={enrollmentData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="enrollments" stroke="#667eea" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Student Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={courseDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {courseDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Tabs Section */}
      <Paper sx={{ mb: 4 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ px: 2 }}>
          <Tab label="My Courses" />
          <Tab label="Recent Activity" />
          <Tab label="Revenue" />
          <Tab label="Student Messages" />
        </Tabs>
      </Paper>

      {/* My Courses Tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {courses.map((course) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={course.id}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Chip
                      size="small"
                      label={course.status}
                      color={course.status === 'published' ? 'success' : 'default'}
                    />
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, course.id)}
                    >
                      <MoreVert />
                    </IconButton>
                  </Box>

                  <Typography variant="h6" gutterBottom>
                    {course.title}
                  </Typography>

                  <Stack spacing={1} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <People fontSize="small" color="action" />
                      <Typography variant="body2" color="text.secondary">
                        {course.students} students
                      </Typography>
                    </Box>
                    {course.rating > 0 && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Star fontSize="small" color="action" />
                        <Typography variant="body2" color="text.secondary">
                          {course.rating} rating
                        </Typography>
                      </Box>
                    )}
                    {course.revenue > 0 && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <MonetizationOn fontSize="small" color="action" />
                        <Typography variant="body2" color="text.secondary">
                          ${course.revenue.toLocaleString()}
                        </Typography>
                      </Box>
                    )}
                  </Stack>

                  {course.completion > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Avg. Completion
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {course.completion}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={course.completion}
                        sx={{ height: 6, borderRadius: 1 }}
                      />
                    </Box>
                  )}

                  <Typography variant="caption" color="text.secondary">
                    Updated {course.lastUpdated}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small" startIcon={<Edit />}>
                    Edit
                  </Button>
                  <Button size="small" startIcon={<Visibility />}>
                    View
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* Recent Activity Tab */}
      <TabPanel value={tabValue} index={1}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Activity</TableCell>
                <TableCell>Student</TableCell>
                <TableCell>Course</TableCell>
                <TableCell>Time</TableCell>
                <TableCell align="right">Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recentActivity.map((activity, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <Chip
                      size="small"
                      label={activity.type}
                      color={
                        activity.type === 'enrollment' ? 'success' :
                        activity.type === 'completion' ? 'info' :
                        activity.type === 'review' ? 'warning' : 'default'
                      }
                    />
                  </TableCell>
                  <TableCell>{activity.student}</TableCell>
                  <TableCell>{activity.course}</TableCell>
                  <TableCell>{activity.time}</TableCell>
                  <TableCell align="right">
                    <Button size="small">View</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Revenue Tab */}
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Revenue Overview
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="revenue" fill="#667eea" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Student Messages Tab */}
      <TabPanel value={tabValue} index={3}>
        <Stack spacing={2}>
          <Button
            variant="outlined"
            startIcon={<Message />}
            sx={{ alignSelf: 'flex-start' }}
          >
            Compose Announcement
          </Button>
          <Typography variant="body2" color="text.secondary">
            No new messages. Student messages will appear here.
          </Typography>
        </Stack>
      </TabPanel>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          navigate(`/lms/instructor/course/${selectedCourse}/edit`);
          handleMenuClose();
        }}>
          <Edit fontSize="small" sx={{ mr: 1 }} />
          Edit Course
        </MenuItem>
        <MenuItem onClick={() => {
          navigate(`/lms/instructor/course/${selectedCourse}/students`);
          handleMenuClose();
        }}>
          <People fontSize="small" sx={{ mr: 1 }} />
          View Students
        </MenuItem>
        <MenuItem onClick={() => {
          navigate(`/lms/instructor/course/${selectedCourse}/analytics`);
          handleMenuClose();
        }}>
          <Assessment fontSize="small" sx={{ mr: 1 }} />
          Analytics
        </MenuItem>
        <MenuItem onClick={handleMenuClose} sx={{ color: 'error.main' }}>
          <Delete fontSize="small" sx={{ mr: 1 }} />
          Delete Course
        </MenuItem>
      </Menu>
    </Container>
  );
};

export default InstructorDashboard;