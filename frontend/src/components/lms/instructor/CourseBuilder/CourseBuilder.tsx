import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  FormControl,
  InputLabel,
  Alert,
  Skeleton,
  Paper,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  MoreVert,
  Visibility,
  Settings,
  School,
  Schedule,
  ArrowBack,
  Publish,
  Unpublished,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import {
  useGetCoursesQuery,
  useCreateCourseMutation,
  useUpdateCourseMutation,
  useDeleteCourseMutation,
  Course,
} from '../../../../features/lms/courseBuilderSlice';

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

const CourseBuilder: React.FC = () => {
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editMode, setEditMode] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    description: '',
    category: '',
    subcategory: '',
    difficulty_level: 'beginner',
    duration_hours: 0,
    tags: [] as string[],
    prerequisites: [] as string[],
  });

  // API hooks
  const { data: courses, isLoading, error } = useGetCoursesQuery();
  const [createCourse, { isLoading: isCreating }] = useCreateCourseMutation();
  const [updateCourse, { isLoading: isUpdating }] = useUpdateCourseMutation();
  const [deleteCourse] = useDeleteCourseMutation();

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, course: Course) => {
    setAnchorEl(event.currentTarget);
    setSelectedCourse(course);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleCreateCourse = () => {
    setEditMode(false);
    setFormData({
      title: '',
      slug: '',
      description: '',
      category: '',
      subcategory: '',
      difficulty_level: 'beginner',
      duration_hours: 0,
      tags: [],
      prerequisites: [],
    });
    setOpenDialog(true);
  };

  const handleEditCourse = (course: Course) => {
    setEditMode(true);
    setSelectedCourse(course);
    setFormData({
      title: course.title,
      slug: course.slug,
      description: course.description || '',
      category: course.category || '',
      subcategory: course.subcategory || '',
      difficulty_level: course.difficulty_level || 'beginner',
      duration_hours: course.duration_hours || 0,
      tags: course.tags || [],
      prerequisites: course.prerequisites || [],
    });
    setOpenDialog(true);
    handleMenuClose();
  };

  const handleDeleteCourse = async (courseId: string) => {
    if (window.confirm('Are you sure you want to delete this course? This action cannot be undone.')) {
      try {
        await deleteCourse(courseId).unwrap();
      } catch (error) {
        console.error('Failed to delete course:', error);
      }
    }
    handleMenuClose();
  };

  const handleSubmit = async () => {
    try {
      console.log('Submitting course data:', formData);
      if (editMode && selectedCourse) {
        const result = await updateCourse({
          id: selectedCourse.id,
          updates: formData,
        }).unwrap();
        console.log('Course updated:', result);
      } else {
        const result = await createCourse({
          ...formData,
          is_published: false,
          is_featured: false,
        }).unwrap();
        console.log('Course created:', result);

        // Redirect to the version editor for the initial version
        if (result.initial_version) {
          navigate(`/lms/admin/courses/${result.id}/version/${result.initial_version.id}`);
        } else {
          // Fallback to course editor if no version info
          navigate(`/lms/admin/courses/${result.id}`);
        }
      }
      setOpenDialog(false);
    } catch (error: any) {
      console.error('Failed to save course:', error);
      // Show error in UI
      alert(`Failed to save course: ${error?.data?.detail || error?.message || 'Unknown error'}`);
    }
  };

  const handleTogglePublish = async (course: Course) => {
    try {
      await updateCourse({
        id: course.id,
        updates: { is_published: !course.is_published },
      }).unwrap();
    } catch (error) {
      console.error('Failed to toggle publish status:', error);
    }
  };

  const handleNavigateToCourseEditor = (courseId: string) => {
    navigate(`/lms/admin/courses/${courseId}`);
  };

  const publishedCourses = courses?.filter(c => c.is_published) || [];
  const draftCourses = courses?.filter(c => !c.is_published) || [];

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h4" gutterBottom>
              Course Builder
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Create and manage your courses
            </Typography>
          </Box>
          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              startIcon={<ArrowBack />}
              onClick={() => navigate('/lms/admin')}
            >
              Back to Dashboard
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleCreateCourse}
            >
              Create New Course
            </Button>
          </Stack>
        </Stack>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Failed to load courses. Please try again later.
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label={`Published (${publishedCourses.length})`} />
          <Tab label={`Drafts (${draftCourses.length})`} />
          <Tab label="All Courses" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        {isLoading ? (
          <Grid container spacing={3}>
            {[1, 2, 3].map((i) => (
              <Grid item xs={12} md={6} lg={4} key={i}>
                <Skeleton variant="rectangular" height={250} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Grid container spacing={3}>
            {publishedCourses.map((course) => (
              <Grid item xs={12} md={6} lg={4} key={course.id}>
                <CourseCard
                  course={course}
                  onEdit={() => handleEditCourse(course)}
                  onDelete={() => handleDeleteCourse(course.id)}
                  onTogglePublish={() => handleTogglePublish(course)}
                  onNavigate={() => handleNavigateToCourseEditor(course.id)}
                  onMenuOpen={handleMenuOpen}
                />
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {isLoading ? (
          <Grid container spacing={3}>
            {[1, 2, 3].map((i) => (
              <Grid item xs={12} md={6} lg={4} key={i}>
                <Skeleton variant="rectangular" height={250} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Grid container spacing={3}>
            {draftCourses.map((course) => (
              <Grid item xs={12} md={6} lg={4} key={course.id}>
                <CourseCard
                  course={course}
                  onEdit={() => handleEditCourse(course)}
                  onDelete={() => handleDeleteCourse(course.id)}
                  onTogglePublish={() => handleTogglePublish(course)}
                  onNavigate={() => handleNavigateToCourseEditor(course.id)}
                  onMenuOpen={handleMenuOpen}
                />
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        {isLoading ? (
          <Grid container spacing={3}>
            {[1, 2, 3].map((i) => (
              <Grid item xs={12} md={6} lg={4} key={i}>
                <Skeleton variant="rectangular" height={250} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Grid container spacing={3}>
            {courses?.map((course) => (
              <Grid item xs={12} md={6} lg={4} key={course.id}>
                <CourseCard
                  course={course}
                  onEdit={() => handleEditCourse(course)}
                  onDelete={() => handleDeleteCourse(course.id)}
                  onTogglePublish={() => handleTogglePublish(course)}
                  onNavigate={() => handleNavigateToCourseEditor(course.id)}
                  onMenuOpen={handleMenuOpen}
                />
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>

      {/* Create/Edit Course Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{editMode ? 'Edit Course' : 'Create New Course'}</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
            <TextField
              label="Course Title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Course Slug (URL)"
              value={formData.slug}
              onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
              fullWidth
              required
              helperText="Used in the course URL (e.g., python-basics)"
            />
            <TextField
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              fullWidth
              multiline
              rows={4}
            />
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Subcategory"
                  value={formData.subcategory}
                  onChange={(e) => setFormData({ ...formData, subcategory: e.target.value })}
                  fullWidth
                />
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Difficulty Level</InputLabel>
                  <Select
                    value={formData.difficulty_level}
                    onChange={(e) => setFormData({ ...formData, difficulty_level: e.target.value })}
                    label="Difficulty Level"
                  >
                    <MenuItem value="beginner">Beginner</MenuItem>
                    <MenuItem value="intermediate">Intermediate</MenuItem>
                    <MenuItem value="advanced">Advanced</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Duration (hours)"
                  type="number"
                  value={formData.duration_hours}
                  onChange={(e) => setFormData({ ...formData, duration_hours: Number(e.target.value) })}
                  fullWidth
                />
              </Grid>
            </Grid>
            <TextField
              label="Tags (comma-separated)"
              value={formData.tags.join(', ')}
              onChange={(e) => setFormData({
                ...formData,
                tags: e.target.value.split(',').map(t => t.trim()).filter(t => t)
              })}
              fullWidth
              helperText="e.g., python, programming, web development"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={isCreating || isUpdating || !formData.title || !formData.slug}
          >
            {editMode ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

// Course Card Component
interface CourseCardProps {
  course: Course;
  onEdit: () => void;
  onDelete: () => void;
  onTogglePublish: () => void;
  onNavigate: () => void;
  onMenuOpen: (event: React.MouseEvent<HTMLElement>, course: Course) => void;
}

const CourseCard: React.FC<CourseCardProps> = ({
  course,
  onEdit,
  onDelete,
  onTogglePublish,
  onNavigate,
  onMenuOpen,
}) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const menuOpen = Boolean(anchorEl);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleDelete = () => {
    handleMenuClose();
    onDelete();
  };

  const handleTogglePublish = () => {
    handleMenuClose();
    onTogglePublish();
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" gutterBottom>
              {course.title}
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
              <Chip
                label={course.is_published ? 'Published' : 'Draft'}
                size="small"
                color={course.is_published ? 'success' : 'default'}
                icon={course.is_published ? <Publish /> : <Unpublished />}
              />
              {course.difficulty_level && (
                <Chip label={course.difficulty_level} size="small" />
              )}
            </Stack>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {course.description || 'No description'}
            </Typography>
          </Box>
          <IconButton size="small" onClick={handleMenuClick}>
            <MoreVert />
          </IconButton>
        </Stack>
        <Stack direction="row" spacing={2} color="text.secondary">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <School fontSize="small" />
            <Typography variant="caption">
              {course.module_count || 0} modules
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Schedule fontSize="small" />
            <Typography variant="caption">
              {course.duration_hours || 0} hours
            </Typography>
          </Box>
        </Stack>
        {course.tags && course.tags.length > 0 && (
          <Stack direction="row" spacing={0.5} sx={{ mt: 2 }}>
            {course.tags.slice(0, 3).map((tag) => (
              <Chip key={tag} label={tag} size="small" variant="outlined" />
            ))}
          </Stack>
        )}
      </CardContent>
      <CardActions>
        <Button size="small" startIcon={<Edit />} onClick={onNavigate}>
          Edit Content
        </Button>
        <Button size="small" startIcon={<Settings />} onClick={onEdit}>
          Settings
        </Button>
      </CardActions>
      <Menu
        anchorEl={anchorEl}
        open={menuOpen}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleTogglePublish}>
          {course.is_published ? 'Unpublish' : 'Publish'}
        </MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          Delete Course
        </MenuItem>
      </Menu>
    </Card>
  );
};

export default CourseBuilder;