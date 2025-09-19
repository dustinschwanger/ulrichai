import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  LinearProgress,
  Avatar,
  Chip,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  PlayCircleOutline,
  AccessTime,
  TrendingUp,
  CalendarToday,
  Assignment,
  School,
  EmojiEvents,
  ArrowForward,
  Book,
  VideoLibrary,
  Quiz,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '../../../store/hooks';
import { selectCurrentUser } from '../../../store/slices/authSlice';
import { useGetMyEnrollmentsQuery } from '../../../store/api/courseApi';

const StudentDashboard: React.FC = () => {
  const navigate = useNavigate();
  const currentUser = useAppSelector(selectCurrentUser);
  const { data: enrollments, isLoading } = useGetMyEnrollmentsQuery();

  // Mock data for demonstration
  const recentActivity = [
    {
      id: 1,
      type: 'video',
      title: 'Introduction to React Hooks',
      course: 'Advanced React Development',
      time: '2 hours ago',
      icon: <VideoLibrary />,
    },
    {
      id: 2,
      type: 'quiz',
      title: 'Module 3 Assessment',
      course: 'JavaScript Fundamentals',
      time: '5 hours ago',
      icon: <Quiz />,
    },
    {
      id: 3,
      type: 'reading',
      title: 'Chapter 4: State Management',
      course: 'Advanced React Development',
      time: '1 day ago',
      icon: <Book />,
    },
  ];

  const upcomingDeadlines = [
    {
      id: 1,
      title: 'Final Project Submission',
      course: 'Web Development',
      dueDate: 'Dec 25, 2025',
      daysLeft: 7,
    },
    {
      id: 2,
      title: 'Module 4 Quiz',
      course: 'JavaScript Fundamentals',
      dueDate: 'Dec 22, 2025',
      daysLeft: 4,
    },
  ];

  const achievements = [
    { id: 1, title: 'Fast Learner', description: 'Complete 3 modules in one week', earned: true },
    { id: 2, title: 'Quiz Master', description: 'Score 90% or higher on 5 quizzes', earned: true },
    { id: 3, title: 'Consistent', description: 'Login for 30 consecutive days', earned: false },
  ];

  return (
    <Box>
      {/* Welcome Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Welcome back, {currentUser?.firstName}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Continue your learning journey and track your progress.
        </Typography>
      </Box>

      {/* Stats Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 3,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <School sx={{ fontSize: 40, opacity: 0.9 }} />
              <Box>
                <Typography variant="h4" fontWeight="bold">
                  {enrollments?.length || 0}
                </Typography>
                <Typography variant="body2">Active Courses</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 3,
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <AccessTime sx={{ fontSize: 40, opacity: 0.9 }} />
              <Box>
                <Typography variant="h4" fontWeight="bold">
                  45h
                </Typography>
                <Typography variant="body2">Learning Time</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 3,
              background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
              color: 'white',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <TrendingUp sx={{ fontSize: 40, opacity: 0.9 }} />
              <Box>
                <Typography variant="h4" fontWeight="bold">
                  85%
                </Typography>
                <Typography variant="body2">Avg. Score</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 3,
              background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
              color: 'white',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <EmojiEvents sx={{ fontSize: 40, opacity: 0.9 }} />
              <Box>
                <Typography variant="h4" fontWeight="bold">
                  12
                </Typography>
                <Typography variant="body2">Achievements</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Current Courses */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h6" fontWeight="bold">
                  My Current Courses
                </Typography>
                <Button
                  size="small"
                  endIcon={<ArrowForward />}
                  onClick={() => navigate('/lms/my-courses')}
                >
                  View All
                </Button>
              </Box>

              {isLoading ? (
                <Typography>Loading courses...</Typography>
              ) : enrollments && enrollments.length > 0 ? (
                <Grid container spacing={2}>
                  {enrollments.slice(0, 2).map((enrollment, index) => (
                    <Grid item xs={12} key={enrollment.id}>
                      <Card variant="outlined">
                        <CardContent>
                          <Box sx={{ display: 'flex', gap: 2 }}>
                            <Avatar
                              sx={{
                                width: 60,
                                height: 60,
                                bgcolor: index === 0 ? 'primary.main' : 'secondary.main',
                              }}
                            >
                              <School />
                            </Avatar>
                            <Box sx={{ flex: 1 }}>
                              <Typography variant="h6" gutterBottom>
                                Course {index + 1}
                              </Typography>
                              <Typography variant="body2" color="text.secondary" gutterBottom>
                                Instructor: John Doe
                              </Typography>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2 }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={enrollment.progressPercentage || 0}
                                  sx={{ flex: 1, height: 8, borderRadius: 4 }}
                                />
                                <Typography variant="body2" fontWeight="bold">
                                  {enrollment.progressPercentage || 0}%
                                </Typography>
                              </Box>
                            </Box>
                          </Box>
                        </CardContent>
                        <CardActions>
                          <Button
                            startIcon={<PlayCircleOutline />}
                            onClick={() => navigate(`/lms/course/${enrollment.id}`)}
                          >
                            Continue Learning
                          </Button>
                        </CardActions>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary" gutterBottom>
                    You're not enrolled in any courses yet.
                  </Typography>
                  <Button
                    variant="contained"
                    sx={{ mt: 2 }}
                    onClick={() => navigate('/lms/courses')}
                  >
                    Browse Courses
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Recent Activity
              </Typography>
              <List>
                {recentActivity.map((activity) => (
                  <ListItem key={activity.id} sx={{ px: 0 }}>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.light' }}>
                        {activity.icon}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={activity.title}
                      secondary={
                        <>
                          {activity.course} • {activity.time}
                        </>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton edge="end">
                        <ArrowForward />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Upcoming Deadlines */}
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Upcoming Deadlines
              </Typography>
              <List>
                {upcomingDeadlines.map((deadline) => (
                  <ListItem key={deadline.id} sx={{ px: 0 }}>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: deadline.daysLeft <= 3 ? 'error.main' : 'warning.main' }}>
                        <Assignment />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={deadline.title}
                      secondary={
                        <>
                          {deadline.course}
                          <br />
                          <Chip
                            label={`${deadline.daysLeft} days left`}
                            size="small"
                            color={deadline.daysLeft <= 3 ? 'error' : 'default'}
                            sx={{ mt: 0.5 }}
                          />
                        </>
                      }
                    />
                  </ListItem>
                ))}
              </List>
              <Button fullWidth sx={{ mt: 2 }}>
                View Calendar
              </Button>
            </CardContent>
          </Card>

          {/* Achievements */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Achievements
              </Typography>
              <List>
                {achievements.map((achievement) => (
                  <ListItem key={achievement.id} sx={{ px: 0 }}>
                    <ListItemAvatar>
                      <Avatar
                        sx={{
                          bgcolor: achievement.earned ? 'success.main' : 'grey.400',
                        }}
                      >
                        <EmojiEvents />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={achievement.title}
                      secondary={achievement.description}
                      sx={{
                        '& .MuiListItemText-primary': {
                          color: achievement.earned ? 'text.primary' : 'text.disabled',
                        },
                        '& .MuiListItemText-secondary': {
                          color: achievement.earned ? 'text.secondary' : 'text.disabled',
                        },
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default StudentDashboard;