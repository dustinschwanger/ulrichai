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
  Chip,
  Breadcrumbs,
  Link,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  ArrowBack,
  Add,
  MoreVert,
  Edit,
  ContentCopy,
  Delete,
  Visibility,
  Schedule,
  CheckCircle,
  School,
  Group,
  CalendarToday,
  Launch,
  PlayCircle,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import {
  useGetCourseQuery,
  useGetCourseVersionsQuery,
  useCreateCourseVersionMutation,
  useUpdateCourseVersionMutation,
  useDeleteCourseVersionMutation
} from '../../../features/lms/courseBuilderSlice';
import { formatDistanceToNow } from 'date-fns';

interface CourseVersionCardProps {
  version: any;
  course: any;
  isActive: boolean;
  onEdit: () => void;
  onDuplicate: () => void;
  onDelete: () => void;
  onToggleActive: () => void;
  onViewDetails: () => void;
  onPreviewAsStudent: () => void;
}

const CourseVersionCard: React.FC<CourseVersionCardProps> = ({
  version,
  course,
  isActive,
  onEdit,
  onDuplicate,
  onDelete,
  onToggleActive,
  onViewDetails,
  onPreviewAsStudent,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <Card sx={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      border: isActive ? '2px solid' : '1px solid',
      borderColor: isActive ? 'primary.main' : 'divider',
    }}>
      {/* Version Header Image */}
      {course.thumbnail_url ? (
        <Box
          sx={{
            height: 160,
            backgroundImage: `url(${course.thumbnail_url})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            position: 'relative',
          }}
        >
          {isActive && (
            <Chip
              label="Active Version"
              color="primary"
              sx={{
                position: 'absolute',
                top: 8,
                left: 8,
              }}
            />
          )}
        </Box>
      ) : (
        <Box
          sx={{
            height: 160,
            bgcolor: 'grey.200',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
          }}
        >
          <School sx={{ fontSize: 60, color: 'grey.400' }} />
          {isActive && (
            <Chip
              label="Active Version"
              color="primary"
              sx={{
                position: 'absolute',
                top: 8,
                left: 8,
              }}
            />
          )}
        </Box>
      )}

      <CardContent sx={{ flexGrow: 1 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box flex={1}>
            <Typography variant="h6" gutterBottom>
              {version.version_name || `Version ${version.version_number}`}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              v{version.version_number}
            </Typography>
          </Box>
          <IconButton size="small" onClick={handleMenuOpen}>
            <MoreVert />
          </IconButton>
        </Stack>

        {version.description && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mt: 1,
              mb: 2,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
            }}
          >
            {version.description}
          </Typography>
        )}

        {/* Version Stats */}
        <Stack spacing={1}>
          {version.modules && version.modules.length > 0 && (
            <Stack direction="row" alignItems="center" spacing={1}>
              <School sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="caption" color="text.secondary">
                {version.modules.length} modules
              </Typography>
            </Stack>
          )}
          <Stack direction="row" alignItems="center" spacing={1}>
            <CalendarToday sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="caption" color="text.secondary">
              Created {formatDistanceToNow(new Date(version.created_at), { addSuffix: true })}
            </Typography>
          </Stack>
        </Stack>

        <Stack direction="row" spacing={1} sx={{ mt: 2 }} flexWrap="wrap" useFlexGap>
          <Chip
            label={version.is_draft ? 'Draft' : 'Published'}
            size="small"
            color={version.is_draft ? 'default' : 'success'}
          />
          {version.is_ai_generated && (
            <Chip label="AI Generated" size="small" variant="outlined" />
          )}
        </Stack>
      </CardContent>

      <CardActions sx={{ px: 2, pb: 2 }}>
        <Button
          size="small"
          variant="contained"
          startIcon={<PlayCircle />}
          onClick={onPreviewAsStudent}
          color="primary"
        >
          Preview
        </Button>
        <Button
          size="small"
          startIcon={<Edit />}
          onClick={onEdit}
        >
          Edit
        </Button>
        <Button
          size="small"
          onClick={onToggleActive}
          color={isActive ? "default" : "primary"}
        >
          {isActive ? 'Deactivate' : 'Activate'}
        </Button>
      </CardActions>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => { onDuplicate(); handleMenuClose(); }}>
          <ContentCopy sx={{ mr: 1, fontSize: 20 }} /> Duplicate Version
        </MenuItem>
        <MenuItem onClick={() => { onDelete(); handleMenuClose(); }} sx={{ color: 'error.main' }}>
          <Delete sx={{ mr: 1, fontSize: 20 }} /> Delete Version
        </MenuItem>
      </Menu>
    </Card>
  );
};

const CourseVersions: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newVersionData, setNewVersionData] = useState({
    version_number: '',
    version_name: '',
    description: '',
    is_active: false,
  });

  const { data: course, isLoading } = useGetCourseQuery(courseId || '');
  const { data: versions = [], isLoading: versionsLoading } = useGetCourseVersionsQuery(courseId || '', {
    skip: !courseId,
  });
  const [createVersion, { isLoading: isCreating }] = useCreateCourseVersionMutation();
  const [updateVersion] = useUpdateCourseVersionMutation();
  const [deleteVersion] = useDeleteCourseVersionMutation();

  // Get active versions from the fetched data
  const activeVersions = versions.filter((v: any) => v.is_active);

  const handleCreateVersion = async () => {
    if (!courseId) return;

    try {
      await createVersion({
        courseId,
        versionData: newVersionData
      }).unwrap();

      setCreateDialogOpen(false);
      setNewVersionData({
        version_number: '',
        version_name: '',
        description: '',
        is_active: false,
      });
    } catch (error) {
      console.error('Failed to create version:', error);
      alert('Failed to create version. Please try again.');
    }
  };

  const handleEditVersion = (versionId: string) => {
    navigate(`/lms/admin/courses/${courseId}/version/${versionId}`);
  };

  const handleViewVersion = (versionId: string) => {
    navigate(`/lms/courses/${courseId}/version/${versionId}`);
  };

  const handlePreviewVersion = (versionId: string) => {
    // Navigate to the student course viewer with the specific version
    navigate(`/lms/course/${courseId}/learn?versionId=${versionId}`);
  };

  const handleDuplicateVersion = async (versionId: string) => {
    if (!courseId) return;

    try {
      await createVersion({
        courseId,
        versionData: {
          source_version_id: versionId,
          is_draft: true,
          is_active: false,
        }
      }).unwrap();
    } catch (error) {
      console.error('Failed to duplicate version:', error);
      alert('Failed to duplicate version. Please try again.');
    }
  };

  const handleDeleteVersion = async (versionId: string) => {
    if (!courseId) return;

    if (window.confirm('Are you sure you want to delete this version? This action cannot be undone.')) {
      try {
        await deleteVersion({
          courseId,
          versionId
        }).unwrap();
      } catch (error: any) {
        console.error('Failed to delete version:', error);
        alert(error?.data?.detail || 'Failed to delete version. Please try again.');
      }
    }
  };

  const handleToggleVersionActive = async (version: any) => {
    if (!courseId) return;

    try {
      await updateVersion({
        courseId,
        versionId: version.id,
        updates: { is_active: !version.is_active }
      }).unwrap();
    } catch (error) {
      console.error('Failed to toggle version active status:', error);
      alert('Failed to update version. Please try again.');
    }
  };

  if (isLoading || versionsLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography>Loading course...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link
          underline="hover"
          color="inherit"
          href="#"
          onClick={(e: any) => {
            e.preventDefault();
            navigate('/lms/admin');
          }}
        >
          Admin Dashboard
        </Link>
        <Link
          underline="hover"
          color="inherit"
          href="#"
          onClick={(e: any) => {
            e.preventDefault();
            navigate('/lms/admin/courses');
          }}
        >
          Courses
        </Link>
        <Typography color="text.primary">Versions</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Stack direction="row" alignItems="center" spacing={2}>
            <IconButton onClick={() => navigate('/lms/admin')}>
              <ArrowBack />
            </IconButton>
            <Box>
              <Typography variant="h4">
                {course?.title || 'Course'} - Versions
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Manage different versions of this course
              </Typography>
            </Box>
          </Stack>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create New Version
        </Button>
      </Stack>

      {/* Active Versions Highlight */}
      {activeVersions.length > 0 && (
        <Paper sx={{ p: 3, mb: 4, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
          <Stack spacing={2}>
            <Stack direction="row" alignItems="center" spacing={1}>
              <CheckCircle />
              <Typography variant="h6">
                Active Versions ({activeVersions.length})
              </Typography>
            </Stack>
            <Typography variant="body2" sx={{ mb: 2 }}>
              These versions are currently available to students based on their enrollment preferences.
            </Typography>
            <Stack direction="row" spacing={2} flexWrap="wrap">
              {activeVersions.map(version => (
                <Chip
                  key={version.id}
                  label={version.version_name}
                  color="secondary"
                  onClick={() => handleViewVersion(version.id)}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Stack>
          </Stack>
        </Paper>
      )}

      {/* Versions Grid */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        All Versions ({versions.length})
      </Typography>
      
      <Grid container spacing={3}>
        {versions.map((version) => (
          <Grid item xs={12} md={6} lg={4} key={version.id}>
            <CourseVersionCard
              version={version}
              course={course || {}}
              isActive={version.is_active}
              onEdit={() => handleEditVersion(version.id)}
              onDuplicate={() => handleDuplicateVersion(version.id)}
              onDelete={() => handleDeleteVersion(version.id)}
              onToggleActive={() => handleToggleVersionActive(version)}
              onViewDetails={() => handleViewVersion(version.id)}
              onPreviewAsStudent={() => handlePreviewVersion(version.id)}
            />
          </Grid>
        ))}
      </Grid>

      {/* Create Version Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Course Version</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Version Number"
              value={newVersionData.version_number}
              onChange={(e) => setNewVersionData({ ...newVersionData, version_number: e.target.value })}
              fullWidth
              helperText="e.g., 2.1, 3.0-draft"
            />
            <TextField
              label="Version Name"
              value={newVersionData.version_name}
              onChange={(e) => setNewVersionData({ ...newVersionData, version_name: e.target.value })}
              fullWidth
              helperText="e.g., Spring 2025 Edition"
            />
            <TextField
              label="Description"
              value={newVersionData.description}
              onChange={(e) => setNewVersionData({ ...newVersionData, description: e.target.value })}
              fullWidth
              multiline
              rows={3}
            />
            <FormControlLabel
              control={<Switch />}
              label="Start from existing version"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={newVersionData.is_active}
                  onChange={(e) => setNewVersionData({ ...newVersionData, is_active: e.target.checked })}
                />
              }
              label="Set as active version"
            />
            <Alert severity="info">
              You can either create a blank version or duplicate an existing version as a starting point. Multiple versions can be active at the same time.
            </Alert>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateVersion} variant="contained">
            Create Version
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CourseVersions;