import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardMedia,
  CardContent,
  Typography,
  LinearProgress,
  Button,
  Tabs,
  Tab,
  Chip,
  Paper,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Stack,
} from '@mui/material';
import {
  PlayArrow,
  AccessTime,
  CalendarToday,
  MoreVert,
  TrendingUp,
  EmojiEvents,
  Schedule,
  Assignment,
  VideoLibrary,
  CheckCircle,
  School,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useGetMyEnrollmentsQuery } from '../../../store/api/courseApi';
import type { EnrolledCourse } from '../../../store/api/courseApi';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

const MyCourses = () => {
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);

  const { data: enrolledCourses, isLoading } = useGetMyEnrollmentsQuery();

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, courseId: string) => {
    setAnchorEl(event.currentTarget);
    setSelectedCourse(courseId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedCourse(null);
  };

  const handleContinueCourse = (courseId: string) => {
    navigate(`/lms/course/${courseId}/learn`);
  };

  const formatLastAccessed = (date: string) => {
    const days = Math.floor((Date.now() - new Date(date).getTime()) / (1000 * 60 * 60 * 24));
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    return `${days} days ago`;
  };

  const activeCourses = enrolledCourses?.filter(c => c.enrollmentStatus === 'active') || [];
  const completedCourses = enrolledCourses?.filter(c => c.enrollmentStatus === 'completed') || [];

  const CourseCard = ({ course }: { course: EnrolledCourse }) => (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 3,
        }
      }}
    >
      <Box sx={{ position: 'relative' }}>
        <CardMedia
          component="img"
          height="160"
          image={course.thumbnailUrl || 'https://via.placeholder.com/400x200'}
          alt={course.title}
        />
        {course.progressPercentage > 0 && (
          <Box
            sx={{
              position: 'absolute',
              top: 12,
              right: 12,
              bgcolor: 'rgba(0, 0, 0, 0.7)',
              color: 'white',
              borderRadius: 2,
              px: 1.5,
              py: 0.5,
            }}
          >
            <Typography variant="caption" fontWeight="600">
              {course.progressPercentage}%
            </Typography>
          </Box>
        )}
      </Box>

      <CardContent sx={{ flexGrow: 1, p: 2 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" fontWeight="600" gutterBottom>
            {course.title}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {course.instructor?.firstName} {course.instructor?.lastName}
          </Typography>
        </Box>

        <LinearProgress
          variant="determinate"
          value={course.progressPercentage}
          sx={{ mb: 1, height: 6, borderRadius: 1 }}
        />

        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
          {course.completedLessons} of {course.totalLessons} lessons completed
        </Typography>

        {course.nextLesson && (
          <Paper
            elevation={0}
            sx={{
              bgcolor: 'action.hover',
              p: 1.5,
              borderRadius: 1,
              mb: 2
            }}
          >
            <Typography variant="caption" color="text.secondary" display="block">
              Next Lesson
            </Typography>
            <Typography variant="body2" fontWeight="500">
              {course.nextLesson.title}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {course.nextLesson.duration} min • {course.nextLesson.moduleTitle}
            </Typography>
          </Paper>
        )}

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <AccessTime fontSize="small" color="action" />
            <Typography variant="caption" color="text.secondary">
              {formatLastAccessed(course.lastAccessedAt!)}
            </Typography>
          </Box>
          {course.estimatedCompletion && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <CalendarToday fontSize="small" color="action" />
              <Typography variant="caption" color="text.secondary">
                Est. {new Date(course.estimatedCompletion).toLocaleDateString()}
              </Typography>
            </Box>
          )}
        </Box>

        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={() => handleContinueCourse(course.id)}
            sx={{ flexGrow: 1 }}
          >
            Continue
          </Button>
          <IconButton
            size="small"
            onClick={(e) => handleMenuOpen(e, course.id)}
          >
            <MoreVert />
          </IconButton>
        </Box>
      </CardContent>

      {course.certificate?.available && (
        <Box sx={{ px: 2, pb: 2 }}>
          <Chip
            icon={<EmojiEvents />}
            label="Certificate Available"
            color="success"
            size="small"
            sx={{ width: '100%' }}
          />
        </Box>
      )}
    </Card>
  );

  const StatsCard = ({ icon, title, value, color }: any) => (
    <Paper sx={{ p: 3, height: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Avatar sx={{ bgcolor: `${color}.light`, color: `${color}.main` }}>
          {icon}
        </Avatar>
        <Box>
          <Typography variant="h4" fontWeight="600">
            {value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
        </Box>
      </Box>
    </Paper>
  );

  if (isLoading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Typography>Loading your courses...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="600" gutterBottom>
          My Learning
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Continue your learning journey and track your progress
        </Typography>
      </Box>

      {/* Stats Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            icon={<School />}
            title="Active Courses"
            value={activeCourses.length}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            icon={<CheckCircle />}
            title="Completed"
            value={completedCourses.length}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            icon={<Schedule />}
            title="Learning Hours"
            value="48.5"
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            icon={<TrendingUp />}
            title="Avg. Progress"
            value={`${Math.round(
              activeCourses.reduce((acc, c) => acc + c.progressPercentage, 0) /
              (activeCourses.length || 1)
            )}%`}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Course Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} sx={{ px: 2 }}>
          <Tab label={`All Courses (${enrolledCourses?.length || 0})`} />
          <Tab label={`In Progress (${activeCourses.length})`} />
          <Tab label={`Completed (${completedCourses.length})`} />
        </Tabs>
      </Paper>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {enrolledCourses?.map((course) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={course.id}>
              <CourseCard course={course} />
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          {activeCourses.map((course) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={course.id}>
              <CourseCard course={course} />
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        {completedCourses.length > 0 ? (
          <Grid container spacing={3}>
            {completedCourses.map((course) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={course.id}>
                <CourseCard course={course} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <School sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No completed courses yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Complete your first course to see it here
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate('/lms/courses')}
            >
              Browse Courses
            </Button>
          </Box>
        )}
      </TabPanel>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          navigate(`/lms/course/${selectedCourse}`);
          handleMenuClose();
        }}>
          <VideoLibrary fontSize="small" sx={{ mr: 1 }} />
          View Course Details
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <Assignment fontSize="small" sx={{ mr: 1 }} />
          View Assignments
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <EmojiEvents fontSize="small" sx={{ mr: 1 }} />
          View Certificate
        </MenuItem>
      </Menu>

      {/* Empty State */}
      {enrolledCourses?.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <School sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Start Your Learning Journey
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            You haven't enrolled in any courses yet. Browse our catalog to find courses that interest you.
          </Typography>
          <Button
            variant="contained"
            size="large"
            startIcon={<VideoLibrary />}
            onClick={() => navigate('/lms/courses')}
          >
            Browse Courses
          </Button>
        </Box>
      )}
    </Container>
  );
};

export default MyCourses;