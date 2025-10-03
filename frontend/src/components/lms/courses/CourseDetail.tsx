import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Button,
  Chip,
  Rating,
  Avatar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  Paper,
  IconButton,
  Tabs,
  Tab,
  Stack,
  LinearProgress,
  Breadcrumbs,
  Link,
  Alert,
  Skeleton,
} from '@mui/material';
import {
  PlayCircleOutline,
  Check,
  ExpandMore,
  AccessTime,
  Language,
  Assignment,
  EmojiEvents,
  Devices,
  AllInclusive,
  School,
  Person,
  Star,
  Share,
  Bookmark,
  BookmarkBorder,
  PlayArrow,
  Article,
  Quiz,
  Code,
  VideoLibrary,
  Download,
  Lock,
  CheckCircle,
  NavigateNext,
} from '@mui/icons-material';
import { useGetCourseQuery } from '../../../features/lms/courseBuilderSlice';
import { useEnrollInCourseMutation } from '../../../store/api/courseApi';
import { useAppSelector } from '../../../store/hooks';
import { selectCurrentUser, selectIsAdmin, selectIsInstructor } from '../../../store/slices/authSlice';
import toast from 'react-hot-toast';

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
      id={`course-tabpanel-${index}`}
      aria-labelledby={`course-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const CourseDetail: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const currentUser = useAppSelector(selectCurrentUser);
  const isAdmin = useAppSelector(selectIsAdmin);
  const isInstructor = useAppSelector(selectIsInstructor);
  const [tabValue, setTabValue] = useState(0);
  const [expandedModules, setExpandedModules] = useState<string[]>([]);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [enrollCourse, { isLoading: isEnrolling }] = useEnrollInCourseMutation();

  const { data: course, isLoading, error } = useGetCourseQuery(courseId!, {
    skip: !courseId,
  });

  const handleEnroll = async () => {
    if (!courseId) return;

    try {
      await enrollCourse({ courseId, cohortId: 'default' }).unwrap();
      toast.success('Successfully enrolled in course!');
      navigate('/lms/my-courses');
    } catch (error) {
      toast.error('Failed to enroll in course');
    }
  };

  const handleViewCourse = () => {
    // Navigate to course viewer directly without enrollment for admins/instructors
    navigate(`/lms/course/${courseId}/learn`);
  };

  const handleModuleToggle = (moduleId: string) => {
    setExpandedModules(prev =>
      prev.includes(moduleId)
        ? prev.filter(id => id !== moduleId)
        : [...prev, moduleId]
    );
  };

  if (isLoading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={8}>
            <Skeleton variant="rectangular" height={400} sx={{ mb: 3 }} />
            <Skeleton variant="text" height={60} />
            <Skeleton variant="text" />
            <Skeleton variant="text" />
          </Grid>
          <Grid item xs={12} md={4}>
            <Skeleton variant="rectangular" height={600} />
          </Grid>
        </Grid>
      </Container>
    );
  }

  if (error || !course) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="error">
          Course not found or an error occurred while loading the course.
        </Alert>
      </Container>
    );
  }

  // Mock curriculum data
  const curriculum = [
    {
      id: '1',
      title: 'Getting Started',
      duration: 45,
      lessons: [
        { id: '1-1', title: 'Course Introduction', type: 'video', duration: 5, isPreview: true },
        { id: '1-2', title: 'Setting Up Your Environment', type: 'video', duration: 15 },
        { id: '1-3', title: 'Course Resources', type: 'article', duration: 10 },
        { id: '1-4', title: 'Your First Project', type: 'assignment', duration: 15 },
      ]
    },
    {
      id: '2',
      title: 'Core Concepts',
      duration: 120,
      lessons: [
        { id: '2-1', title: 'Understanding the Basics', type: 'video', duration: 30 },
        { id: '2-2', title: 'Advanced Techniques', type: 'video', duration: 45 },
        { id: '2-3', title: 'Best Practices', type: 'article', duration: 20 },
        { id: '2-4', title: 'Knowledge Check', type: 'quiz', duration: 25 },
      ]
    },
    {
      id: '3',
      title: 'Practical Applications',
      duration: 180,
      lessons: [
        { id: '3-1', title: 'Real-World Examples', type: 'video', duration: 40 },
        { id: '3-2', title: 'Building Your Project', type: 'code', duration: 90 },
        { id: '3-3', title: 'Testing and Debugging', type: 'video', duration: 30 },
        { id: '3-4', title: 'Final Project', type: 'assignment', duration: 20 },
      ]
    },
  ];

  // Mock reviews data
  const reviews = [
    {
      id: '1',
      user: 'John Doe',
      avatar: null,
      rating: 5,
      date: '2 weeks ago',
      comment: 'Excellent course! Very comprehensive and well-structured. The instructor explains concepts clearly and the practical exercises really helped solidify my understanding.',
      helpful: 24,
    },
    {
      id: '2',
      user: 'Jane Smith',
      avatar: null,
      rating: 4,
      date: '1 month ago',
      comment: 'Great content and good pacing. Would have liked more advanced topics covered, but overall a solid learning experience.',
      helpful: 18,
    },
    {
      id: '3',
      user: 'Mike Johnson',
      avatar: null,
      rating: 5,
      date: '2 months ago',
      comment: 'This course transformed my career! The projects were challenging but rewarding. Highly recommend to anyone serious about learning.',
      helpful: 42,
    },
  ];

  const getLessonIcon = (type: string) => {
    switch (type) {
      case 'video': return <PlayCircleOutline />;
      case 'article': return <Article />;
      case 'quiz': return <Quiz />;
      case 'assignment': return <Assignment />;
      case 'code': return <Code />;
      default: return <VideoLibrary />;
    }
  };

  const totalDuration = curriculum.reduce((sum, module) => sum + module.duration, 0);
  const totalLessons = curriculum.reduce((sum, module) => sum + module.lessons.length, 0);

  return (
    <Box sx={{ bgcolor: 'grey.50', minHeight: '100vh' }}>
      {/* Course Hero Section */}
      <Box sx={{ bgcolor: 'grey.900', color: 'white', py: 4 }}>
        <Container maxWidth="xl">
          <Breadcrumbs
            separator={<NavigateNext fontSize="small" />}
            sx={{ mb: 2 }}
          >
            <Link
              color="inherit"
              href="#"
              onClick={(e) => {
                e.preventDefault();
                navigate('/lms/courses');
              }}
              sx={{ '&:hover': { textDecoration: 'underline' } }}
            >
              Courses
            </Link>
            <Link
              color="inherit"
              href="#"
              sx={{ '&:hover': { textDecoration: 'underline' } }}
            >
              {course.category || 'Technology'}
            </Link>
            <Typography color="text.primary" sx={{ color: 'grey.300' }}>
              {course.title}
            </Typography>
          </Breadcrumbs>

          <Grid container spacing={4}>
            <Grid item xs={12} md={8}>
              <Typography variant="h3" fontWeight="bold" gutterBottom>
                {course.title}
              </Typography>
              <Typography variant="h6" sx={{ mb: 3, opacity: 0.9 }}>
                {course.shortDescription || course.description}
              </Typography>

              <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
                <Chip
                  label={course.difficultyLevel}
                  size="small"
                  sx={{
                    bgcolor: 'primary.main',
                    color: 'white',
                    textTransform: 'capitalize'
                  }}
                />
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Rating value={course.rating || 4.5} precision={0.1} readOnly size="small" />
                  <Typography variant="body2">
                    {course.rating || 4.5} ({course.reviewCount || reviews.length} reviews)
                  </Typography>
                </Box>
                <Typography variant="body2">
                  {course.enrolledCount || 1234} students enrolled
                </Typography>
              </Stack>

              <Stack direction="row" spacing={3} sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Avatar src={course.instructor?.avatarUrl}>
                    {course.instructor?.firstName?.[0]}
                  </Avatar>
                  <Box>
                    <Typography variant="caption" sx={{ opacity: 0.7 }}>
                      Created by
                    </Typography>
                    <Typography variant="body2">
                      {course.instructor?.firstName} {course.instructor?.lastName}
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Language fontSize="small" />
                  <Typography variant="body2">{course.language || 'English'}</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <AccessTime fontSize="small" />
                  <Typography variant="body2">
                    Last updated {new Date(course.updatedAt).toLocaleDateString()}
                  </Typography>
                </Box>
              </Stack>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Grid container spacing={4}>
          {/* Main Content */}
          <Grid item xs={12} md={8}>
            {/* Preview Video */}
            <Card sx={{ mb: 4 }}>
              <CardMedia
                component="img"
                height="400"
                image={course.thumbnailUrl || `https://picsum.photos/800/400?random=${course.id}`}
                alt={course.title}
                sx={{ cursor: 'pointer', position: 'relative' }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  bgcolor: 'rgba(0,0,0,0.7)',
                  borderRadius: '50%',
                  p: 2,
                  cursor: 'pointer',
                  '&:hover': {
                    bgcolor: 'rgba(0,0,0,0.9)',
                  }
                }}
              >
                <PlayArrow sx={{ fontSize: 48, color: 'white' }} />
              </Box>
            </Card>

            {/* Course Tabs */}
            <Paper sx={{ mb: 4 }}>
              <Tabs
                value={tabValue}
                onChange={(e, newValue) => setTabValue(newValue)}
                sx={{ borderBottom: 1, borderColor: 'divider' }}
              >
                <Tab label="Overview" />
                <Tab label="Curriculum" />
                <Tab label="Instructor" />
                <Tab label="Reviews" />
              </Tabs>

              {/* Overview Tab */}
              <TabPanel value={tabValue} index={0}>
                {/* What You'll Learn */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h5" fontWeight="bold" gutterBottom>
                    What you'll learn
                  </Typography>
                  <Grid container spacing={2}>
                    {[
                      'Master fundamental concepts and best practices',
                      'Build real-world projects from scratch',
                      'Learn industry-standard tools and workflows',
                      'Develop problem-solving and debugging skills',
                      'Work with modern frameworks and libraries',
                      'Deploy and maintain production applications',
                    ].map((item, index) => (
                      <Grid item xs={12} sm={6} key={index}>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Check sx={{ color: 'success.main', flexShrink: 0 }} />
                          <Typography variant="body2">{item}</Typography>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                </Box>

                {/* Course Description */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h5" fontWeight="bold" gutterBottom>
                    Description
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    {course.description || 'This comprehensive course is designed to take you from beginner to advanced level. You\'ll learn through hands-on projects, real-world examples, and practical exercises that will prepare you for professional work.'}
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    Throughout the course, you'll work on multiple projects that demonstrate key concepts and best practices. Our structured curriculum ensures you build a solid foundation while progressively tackling more complex topics.
                  </Typography>
                </Box>

                {/* Requirements */}
                {course.prerequisites && course.prerequisites.length > 0 && (
                  <Box sx={{ mb: 4 }}>
                    <Typography variant="h5" fontWeight="bold" gutterBottom>
                      Requirements
                    </Typography>
                    <List>
                      {course.prerequisites.map((req, index) => (
                        <ListItem key={index} sx={{ py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 36 }}>
                            <Check fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary={req} />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </TabPanel>

              {/* Curriculum Tab */}
              <TabPanel value={tabValue} index={1}>
                <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="h5" fontWeight="bold">
                    Course Curriculum
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {curriculum.length} sections • {totalLessons} lessons • {Math.floor(totalDuration / 60)}h {totalDuration % 60}m total length
                  </Typography>
                </Box>

                {curriculum.map((module, moduleIndex) => (
                  <Accordion
                    key={module.id}
                    expanded={expandedModules.includes(module.id)}
                    onChange={() => handleModuleToggle(module.id)}
                    sx={{ mb: 2 }}
                  >
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', pr: 2 }}>
                        <Typography fontWeight="medium">
                          Section {moduleIndex + 1}: {module.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {module.lessons.length} lessons • {module.duration}min
                        </Typography>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <List disablePadding>
                        {module.lessons.map((lesson, lessonIndex) => (
                          <ListItem
                            key={lesson.id}
                            sx={{
                              py: 1,
                              '&:hover': { bgcolor: 'action.hover' },
                              cursor: lesson.isPreview ? 'pointer' : 'default',
                            }}
                          >
                            <ListItemIcon sx={{ minWidth: 40 }}>
                              {getLessonIcon(lesson.type)}
                            </ListItemIcon>
                            <ListItemText
                              primary={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Typography variant="body2">
                                    {lessonIndex + 1}. {lesson.title}
                                  </Typography>
                                  {lesson.isPreview && (
                                    <Chip label="Preview" size="small" color="primary" />
                                  )}
                                </Box>
                              }
                            />
                            <Typography variant="body2" color="text.secondary">
                              {lesson.duration}min
                            </Typography>
                            {!lesson.isPreview && <Lock fontSize="small" sx={{ ml: 1, color: 'text.disabled' }} />}
                          </ListItem>
                        ))}
                      </List>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </TabPanel>

              {/* Instructor Tab */}
              <TabPanel value={tabValue} index={2}>
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h5" fontWeight="bold" gutterBottom>
                    About the Instructor
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 3, mt: 3 }}>
                    <Avatar
                      sx={{ width: 120, height: 120 }}
                      src={course.instructor?.avatarUrl}
                    >
                      {course.instructor?.firstName?.[0]}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        {course.instructor?.firstName} {course.instructor?.lastName}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {course.instructor?.title || 'Senior Instructor'}
                      </Typography>
                      <Stack direction="row" spacing={3}>
                        <Box>
                          <Typography variant="h6">4.7</Typography>
                          <Typography variant="caption" color="text.secondary">
                            Instructor Rating
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="h6">12,543</Typography>
                          <Typography variant="caption" color="text.secondary">
                            Students
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="h6">15</Typography>
                          <Typography variant="caption" color="text.secondary">
                            Courses
                          </Typography>
                        </Box>
                      </Stack>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                        Passionate educator with over 10 years of industry experience.
                        Specializing in making complex topics accessible and engaging for learners at all levels.
                        Committed to helping students achieve their learning goals through practical, hands-on instruction.
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </TabPanel>

              {/* Reviews Tab */}
              <TabPanel value={tabValue} index={3}>
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h5" fontWeight="bold" gutterBottom>
                    Student Reviews
                  </Typography>

                  {/* Rating Summary */}
                  <Grid container spacing={4} sx={{ my: 3 }}>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h2" fontWeight="bold">
                          {course.rating || 4.5}
                        </Typography>
                        <Rating value={course.rating || 4.5} precision={0.1} readOnly />
                        <Typography variant="body2" color="text.secondary">
                          Course Rating
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={8}>
                      {[5, 4, 3, 2, 1].map(rating => (
                        <Box key={rating} sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 60 }}>
                            <Star fontSize="small" />
                            <Typography variant="body2">{rating}</Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={rating === 5 ? 65 : rating === 4 ? 25 : 10}
                            sx={{ flex: 1, height: 8, borderRadius: 1 }}
                          />
                        </Box>
                      ))}
                    </Grid>
                  </Grid>

                  <Divider sx={{ my: 3 }} />

                  {/* Individual Reviews */}
                  {reviews.map(review => (
                    <Box key={review.id} sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <Avatar src={review.avatar}>
                          {review.user[0]}
                        </Avatar>
                        <Box sx={{ flex: 1 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Box>
                              <Typography variant="subtitle2">{review.user}</Typography>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Rating value={review.rating} size="small" readOnly />
                                <Typography variant="caption" color="text.secondary">
                                  {review.date}
                                </Typography>
                              </Box>
                            </Box>
                          </Box>
                          <Typography variant="body2" color="text.secondary" paragraph>
                            {review.comment}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {review.helpful} people found this helpful
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                  ))}
                </Box>
              </TabPanel>
            </Paper>
          </Grid>

          {/* Sticky Enrollment Card */}
          <Grid item xs={12} md={4}>
            <Card sx={{ position: 'sticky', top: 80 }}>
              <CardMedia
                component="img"
                height="200"
                image={course.thumbnailUrl || `https://picsum.photos/400/200?random=${course.id}`}
                alt={course.title}
              />
              <CardContent>
                <Box sx={{ mb: 3 }}>
                  {course.price > 0 ? (
                    <Box>
                      <Typography variant="h3" fontWeight="bold">
                        ${course.price}
                      </Typography>
                      {course.discountPrice && (
                        <Typography variant="body2" color="text.secondary" sx={{ textDecoration: 'line-through' }}>
                          ${course.discountPrice}
                        </Typography>
                      )}
                    </Box>
                  ) : (
                    <Typography variant="h3" fontWeight="bold" color="success.main">
                      Free
                    </Typography>
                  )}
                </Box>

                {/* Show different buttons based on user role */}
                {isAdmin || isInstructor ? (
                  <>
                    <Button
                      fullWidth
                      variant="contained"
                      size="large"
                      onClick={handleViewCourse}
                      sx={{
                        py: 1.5,
                        mb: 1,
                        background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                      }}
                      startIcon={<PlayArrow />}
                    >
                      View Course (Admin Access)
                    </Button>
                    <Button
                      fullWidth
                      variant="outlined"
                      size="large"
                      onClick={handleEnroll}
                      disabled={isEnrolling}
                      sx={{ mb: 2 }}
                    >
                      {isEnrolling ? 'Enrolling...' : 'Enroll as Student'}
                    </Button>
                  </>
                ) : (
                  <Button
                    fullWidth
                    variant="contained"
                    size="large"
                    onClick={handleEnroll}
                    disabled={isEnrolling}
                    sx={{
                      py: 1.5,
                      mb: 2,
                      background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                    }}
                  >
                    {isEnrolling ? 'Enrolling...' : 'Enroll Now'}
                  </Button>
                )}

                <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={isBookmarked ? <Bookmark /> : <BookmarkBorder />}
                    onClick={() => setIsBookmarked(!isBookmarked)}
                  >
                    {isBookmarked ? 'Saved' : 'Save'}
                  </Button>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Share />}
                  >
                    Share
                  </Button>
                </Stack>

                <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
                  30-Day Money-Back Guarantee
                </Typography>

                <Divider sx={{ mb: 3 }} />

                <Typography variant="h6" gutterBottom>
                  This course includes:
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <VideoLibrary fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary={`${Math.floor(totalDuration / 60)} hours on-demand video`} />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Download fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Downloadable resources" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <AllInclusive fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Full lifetime access" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Devices fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Access on mobile and TV" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Assignment fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Assignments and projects" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <EmojiEvents fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Certificate of completion" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default CourseDetail;