import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  Stack,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  IconButton,
} from '@mui/material';
import {
  ArrowBack,
  PlayCircle,
  Article,
  Quiz,
  Forum,
  Poll,
  Psychology,
  TouchApp,
  CheckCircle,
  Schedule,
  School,
} from '@mui/icons-material';
import { useGetCourseStructureQuery } from '../../features/lms/courseBuilderSlice';

const CoursePreview: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();

  const { data: courseStructure, isLoading, error } = useGetCourseStructureQuery(
    courseId || '',
    { skip: !courseId }
  );

  const getActivityIcon = (activityType: string) => {
    switch (activityType) {
      case 'video':
        return <PlayCircle />;
      case 'reading':
        return <Article />;
      case 'quiz':
        return <Quiz />;
      case 'discussion':
        return <Forum />;
      case 'poll':
        return <Poll />;
      case 'reflection':
        return <Psychology />;
      case 'interactive':
        return <TouchApp />;
      default:
        return <School />;
    }
  };

  const getActivityTypeLabel = (activityType: string) => {
    switch (activityType) {
      case 'video':
        return 'Video Activity';
      case 'reading':
        return 'Reading';
      case 'quiz':
        return 'Quiz';
      case 'discussion':
        return 'Discussion';
      case 'poll':
        return 'Poll';
      case 'reflection':
        return 'Reflection';
      case 'interactive':
        return 'Interactive';
      default:
        return 'Activity';
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography>Loading course preview...</Typography>
      </Container>
    );
  }

  if (error || !courseStructure) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          Failed to load course preview. Please try again.
        </Alert>
        <Button onClick={() => navigate(-1)} startIcon={<ArrowBack />} sx={{ mt: 2 }}>
          Go Back
        </Button>
      </Container>
    );
  }

  const totalActivities = courseStructure.modules.reduce(
    (sum, module) => sum + (module.lessons?.length || 0),
    0
  );

  const totalDuration = courseStructure.modules.reduce(
    (sum, module) => sum + (module.estimated_duration_minutes || 0),
    0
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Button
          onClick={() => navigate(`/lms/instructor/courses/${courseId}/edit`)}
          startIcon={<ArrowBack />}
          sx={{ mb: 2 }}
        >
          Back to Course Builder
        </Button>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h4" gutterBottom>
            {courseStructure.course.title}
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            {courseStructure.course.description}
          </Typography>
          <Stack direction="row" spacing={2} alignItems="center">
            <Chip
              icon={<School />}
              label={`${courseStructure.modules.length} Modules`}
              color="primary"
              variant="outlined"
            />
            <Chip
              icon={<Article />}
              label={`${totalActivities} Activities`}
              color="primary"
              variant="outlined"
            />
            {totalDuration > 0 && (
              <Chip
                icon={<Schedule />}
                label={`~${Math.ceil(totalDuration / 60)} hours`}
                color="primary"
                variant="outlined"
              />
            )}
          </Stack>
        </Paper>
      </Box>

      {/* Course Content */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Typography variant="h5" gutterBottom>
            Course Content
          </Typography>

          {courseStructure.modules.length === 0 ? (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="text.secondary">
                No modules added yet. Go back to the course builder to add content.
              </Typography>
            </Paper>
          ) : (
            courseStructure.modules.map((module, moduleIndex) => (
              <Card key={module.id} sx={{ mb: 3 }}>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                    <Box>
                      <Typography variant="h6">
                        Module {moduleIndex + 1}: {module.title}
                      </Typography>
                      {module.description && (
                        <Typography variant="body2" color="text.secondary">
                          {module.description}
                        </Typography>
                      )}
                    </Box>
                    {module.estimated_duration_minutes && (
                      <Chip
                        size="small"
                        icon={<Schedule />}
                        label={`${module.estimated_duration_minutes} min`}
                      />
                    )}
                  </Stack>

                  {module.lessons && module.lessons.length > 0 ? (
                    <List>
                      {module.lessons.map((activity, activityIndex) => (
                        <React.Fragment key={activity.id}>
                          {activityIndex > 0 && <Divider />}
                          <ListItem>
                            <ListItemIcon>
                              {getActivityIcon(activity.lesson_type)}
                            </ListItemIcon>
                            <ListItemText
                              primary={
                                <Stack direction="row" spacing={1} alignItems="center">
                                  <Typography>
                                    {activity.title}
                                  </Typography>
                                  <Chip
                                    label={getActivityTypeLabel(activity.lesson_type)}
                                    size="small"
                                    variant="outlined"
                                  />
                                  {activity.is_required && (
                                    <Chip
                                      label="Required"
                                      size="small"
                                      color="primary"
                                    />
                                  )}
                                </Stack>
                              }
                              secondary={activity.description}
                            />
                            {activity.estimated_duration_minutes && (
                              <Typography variant="caption" color="text.secondary">
                                {activity.estimated_duration_minutes} min
                              </Typography>
                            )}
                          </ListItem>
                        </React.Fragment>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                      No activities added to this module yet.
                    </Typography>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Course Information
              </Typography>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    label={courseStructure.course.is_published ? 'Published' : 'Draft'}
                    color={courseStructure.course.is_published ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Category
                  </Typography>
                  <Typography>{courseStructure.course.category || 'Not specified'}</Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Level
                  </Typography>
                  <Typography>{courseStructure.course.level || 'All Levels'}</Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Language
                  </Typography>
                  <Typography>{courseStructure.course.language || 'English'}</Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>

          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                What Students Will Learn
              </Typography>
              {courseStructure.modules.some(m => m.learning_objectives?.length > 0) ? (
                <List>
                  {courseStructure.modules.map(module =>
                    module.learning_objectives?.map((objective, index) => (
                      <ListItem key={`${module.id}-${index}`}>
                        <ListItemIcon>
                          <CheckCircle color="success" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={objective} />
                      </ListItem>
                    ))
                  )}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Learning objectives will be displayed here.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default CoursePreview;