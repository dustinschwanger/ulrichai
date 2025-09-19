import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Collapse,
  Divider,
  LinearProgress,
  Tabs,
  Tab,
  Chip,
  Stack,
  Avatar,
  Card,
  CardContent,
  Drawer,
  AppBar,
  Toolbar,
  TextField,
} from '@mui/material';
import {
  PlayCircle,
  CheckCircle,
  RadioButtonUnchecked,
  ExpandLess,
  ExpandMore,
  Description,
  Quiz,
  Code,
  VideoLibrary,
  NavigateNext,
  NavigateBefore,
  Menu as MenuIcon,
  Close,
  AccessTime,
  Assignment,
  Download,
  Bookmark,
  BookmarkBorder,
  Help,
  Forum,
  Notes,
  Send,
  SmartToy,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import LessonChat from './LessonChat';
import LessonQA from './LessonQA';
import LessonNotes from './LessonNotes';

interface Module {
  id: string;
  title: string;
  description: string;
  lessons: Lesson[];
  duration: number;
  isCompleted: boolean;
  order: number;
}

interface Lesson {
  id: string;
  title: string;
  type: 'video' | 'reading' | 'quiz' | 'assignment' | 'code';
  duration: number;
  isCompleted: boolean;
  isLocked: boolean;
  content?: any;
  order: number;
}

const CourseViewer = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [selectedLesson, setSelectedLesson] = useState<string>('lesson-1-1');
  const [expandedModules, setExpandedModules] = useState<string[]>(['module-1']);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [isBookmarked, setIsBookmarked] = useState(false);

  // Mock course data
  const courseData = {
    id: courseId,
    title: 'Introduction to Machine Learning',
    instructor: {
      name: 'Dr. Sarah Johnson',
      avatar: null,
      title: 'AI Research Scientist',
    },
    progress: {
      percentage: 45,
      completedLessons: 12,
      totalLessons: 28,
    },
    modules: [
      {
        id: 'module-1',
        title: 'Module 1: Introduction and Setup',
        description: 'Get started with machine learning fundamentals',
        duration: 90,
        isCompleted: true,
        order: 1,
        lessons: [
          {
            id: 'lesson-1-1',
            title: 'Welcome to Machine Learning',
            type: 'video' as const,
            duration: 15,
            isCompleted: true,
            isLocked: false,
            order: 1,
          },
          {
            id: 'lesson-1-2',
            title: 'Setting Up Your Environment',
            type: 'reading' as const,
            duration: 10,
            isCompleted: true,
            isLocked: false,
            order: 2,
          },
          {
            id: 'lesson-1-3',
            title: 'Python Basics Review',
            type: 'video' as const,
            duration: 25,
            isCompleted: true,
            isLocked: false,
            order: 3,
          },
          {
            id: 'lesson-1-4',
            title: 'Module 1 Quiz',
            type: 'quiz' as const,
            duration: 20,
            isCompleted: true,
            isLocked: false,
            order: 4,
          },
        ],
      },
      {
        id: 'module-2',
        title: 'Module 2: Supervised Learning',
        description: 'Learn about classification and regression',
        duration: 180,
        isCompleted: false,
        order: 2,
        lessons: [
          {
            id: 'lesson-2-1',
            title: 'Introduction to Supervised Learning',
            type: 'video' as const,
            duration: 30,
            isCompleted: true,
            isLocked: false,
            order: 1,
          },
          {
            id: 'lesson-2-2',
            title: 'Linear Regression Deep Dive',
            type: 'video' as const,
            duration: 45,
            isCompleted: false,
            isLocked: false,
            order: 2,
          },
          {
            id: 'lesson-2-3',
            title: 'Hands-on: Building Your First Model',
            type: 'code' as const,
            duration: 60,
            isCompleted: false,
            isLocked: false,
            order: 3,
          },
        ],
      },
      {
        id: 'module-3',
        title: 'Module 3: Unsupervised Learning',
        description: 'Explore clustering and dimensionality reduction',
        duration: 150,
        isCompleted: false,
        order: 3,
        lessons: [
          {
            id: 'lesson-3-1',
            title: 'K-Means Clustering',
            type: 'video' as const,
            duration: 35,
            isCompleted: false,
            isLocked: true,
            order: 1,
          },
        ],
      },
    ] as Module[],
  };

  const currentLesson = courseData.modules
    .flatMap(m => m.lessons)
    .find(l => l.id === selectedLesson);

  const getLessonIcon = (type: string, isCompleted: boolean) => {
    if (isCompleted) return <CheckCircle color="success" />;
    switch (type) {
      case 'video':
        return <VideoLibrary />;
      case 'reading':
        return <Description />;
      case 'quiz':
        return <Quiz />;
      case 'code':
        return <Code />;
      case 'assignment':
        return <Assignment />;
      default:
        return <RadioButtonUnchecked />;
    }
  };

  const toggleModule = (moduleId: string) => {
    setExpandedModules(prev =>
      prev.includes(moduleId)
        ? prev.filter(id => id !== moduleId)
        : [...prev, moduleId]
    );
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const navigateToNextLesson = () => {
    const allLessons = courseData.modules.flatMap(m => m.lessons);
    const currentIndex = allLessons.findIndex(l => l.id === selectedLesson);
    if (currentIndex < allLessons.length - 1) {
      setSelectedLesson(allLessons[currentIndex + 1].id);
    }
  };

  const navigateToPrevLesson = () => {
    const allLessons = courseData.modules.flatMap(m => m.lessons);
    const currentIndex = allLessons.findIndex(l => l.id === selectedLesson);
    if (currentIndex > 0) {
      setSelectedLesson(allLessons[currentIndex - 1].id);
    }
  };

  const VideoContent = () => (
    <Box>
      <Box
        sx={{
          aspectRatio: '16/9',
          bgcolor: 'black',
          borderRadius: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 3,
        }}
      >
        <IconButton size="large" sx={{ color: 'white' }}>
          <PlayCircle sx={{ fontSize: 80 }} />
        </IconButton>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          {currentLesson?.title}
        </Typography>
        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <Chip
            icon={<AccessTime />}
            label={`${currentLesson?.duration} min`}
            size="small"
          />
          <Chip
            icon={<VideoLibrary />}
            label="Video Lesson"
            size="small"
          />
        </Stack>
        <Typography variant="body1" paragraph>
          In this lesson, we'll explore the fundamental concepts of machine learning
          and understand how algorithms learn from data. We'll cover supervised vs
          unsupervised learning, training vs testing data, and key terminology.
        </Typography>

        <Divider sx={{ my: 3 }} />

        <Typography variant="h6" gutterBottom>
          Resources
        </Typography>
        <Stack spacing={1}>
          <Button startIcon={<Download />} variant="outlined">
            Download Slides (PDF)
          </Button>
          <Button startIcon={<Code />} variant="outlined">
            Download Code Examples
          </Button>
        </Stack>
      </Paper>
    </Box>
  );

  const TabContent = () => (
    <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
      <Tab label="Ulrich AI" />
      <Tab label="Q&A" />
      <Tab label="Notes" />
    </Tabs>
  );

  const CourseContent = () => (
    <List sx={{ p: 0 }}>
      {courseData.modules.map((module) => (
        <Box key={module.id}>
          <ListItemButton
            onClick={() => toggleModule(module.id)}
            sx={{
              bgcolor: 'background.paper',
              '&:hover': { bgcolor: 'action.hover' },
            }}
          >
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="subtitle2">{module.title}</Typography>
                  {module.isCompleted && (
                    <CheckCircle color="success" fontSize="small" />
                  )}
                </Box>
              }
              secondary={
                <Typography variant="caption" color="text.secondary">
                  {module.lessons.length} lessons • {module.duration} min
                </Typography>
              }
            />
            {expandedModules.includes(module.id) ? <ExpandLess /> : <ExpandMore />}
          </ListItemButton>

          <Collapse in={expandedModules.includes(module.id)}>
            <List disablePadding>
              {module.lessons.map((lesson) => (
                <ListItemButton
                  key={lesson.id}
                  selected={selectedLesson === lesson.id}
                  onClick={() => !lesson.isLocked && setSelectedLesson(lesson.id)}
                  disabled={lesson.isLocked}
                  sx={{
                    pl: 4,
                    bgcolor: selectedLesson === lesson.id ? 'action.selected' : 'transparent',
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {getLessonIcon(lesson.type, lesson.isCompleted)}
                  </ListItemIcon>
                  <ListItemText
                    primary={lesson.title}
                    secondary={`${lesson.duration} min`}
                  />
                </ListItemButton>
              ))}
            </List>
          </Collapse>
          <Divider />
        </Box>
      ))}
    </List>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: 'background.default' }}>
      {/* Header */}
      <AppBar position="fixed" elevation={1}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            sx={{ mr: 2 }}
          >
            {sidebarOpen ? <Close /> : <MenuIcon />}
          </IconButton>

          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {courseData.title}
          </Typography>

          <Stack direction="row" spacing={1} alignItems="center">
            <Typography variant="body2">
              {courseData.progress.completedLessons}/{courseData.progress.totalLessons} lessons
            </Typography>
            <LinearProgress
              variant="determinate"
              value={courseData.progress.percentage}
              sx={{ width: 120, mr: 2 }}
            />
            <IconButton onClick={() => setIsBookmarked(!isBookmarked)}>
              {isBookmarked ? <Bookmark /> : <BookmarkBorder />}
            </IconButton>
            <Button
              variant="outlined"
              onClick={() => navigate(`/lms/course/${courseId}`)}
            >
              Course Info
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Drawer
        variant="persistent"
        anchor="left"
        open={sidebarOpen}
        sx={{
          width: sidebarOpen ? 360 : 0,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 360,
            boxSizing: 'border-box',
            top: 64,
            height: 'calc(100% - 64px)',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Course Content
          </Typography>
          <LinearProgress
            variant="determinate"
            value={courseData.progress.percentage}
            sx={{ mb: 1, height: 8, borderRadius: 1 }}
          />
          <Typography variant="caption" color="text.secondary">
            {courseData.progress.percentage}% Complete
          </Typography>
        </Box>
        <Divider />
        <CourseContent />
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          ml: sidebarOpen ? 0 : 0,
          transition: 'margin-left 0.3s',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <VideoContent />

              <Box sx={{ mt: 3 }}>
                <TabContent />

                {tabValue === 0 && (
                  <Paper sx={{ p: 0, height: '650px', overflow: 'hidden' }}>
                    <LessonChat
                      courseTitle={courseData.title}
                      lessonTitle={currentLesson?.title || 'Unknown Lesson'}
                      lessonType={currentLesson?.type}
                      moduleTitle={courseData.modules.find(m =>
                        m.lessons.some(l => l.id === selectedLesson)
                      )?.title}
                      learningObjectives={[
                        'Understand what machine learning is and how it differs from traditional programming',
                        'Learn about different types of machine learning algorithms',
                        'Identify real-world applications of machine learning'
                      ]}
                      currentContent={`This lesson covers ${currentLesson?.title}. It is a ${currentLesson?.duration} minute ${currentLesson?.type} lesson that is part of the ${courseData.title} course.`}
                    />
                  </Paper>
                )}

                {tabValue === 1 && (
                  <Paper sx={{ p: 3 }}>
                    <LessonQA
                      lessonId={selectedLesson}
                      lessonTitle={currentLesson?.title || 'Unknown Lesson'}
                      courseId={courseData.id}
                    />
                  </Paper>
                )}

                {tabValue === 2 && (
                  <Paper sx={{ p: 3 }}>
                    <LessonNotes
                      lessonId={selectedLesson}
                      lessonTitle={currentLesson?.title || 'Unknown Lesson'}
                      courseId={courseData.id}
                    />
                  </Paper>
                )}

              </Box>
            </Grid>
          </Grid>

          {/* Navigation Buttons */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button
              variant="outlined"
              startIcon={<NavigateBefore />}
              onClick={navigateToPrevLesson}
            >
              Previous Lesson
            </Button>

            <Button
              variant="contained"
              endIcon={<NavigateNext />}
              onClick={navigateToNextLesson}
            >
              Next Lesson
            </Button>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default CourseViewer;