import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  IconButton,
  Stack,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  FormControl,
  InputLabel,
  MenuItem,
  Alert,
  Skeleton,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Paper,
  Divider,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  ArrowBack,
  ExpandMore,
  Add,
  Edit,
  Delete,
  DragIndicator,
  School,
  VideoLibrary,
  Description,
  Quiz,
  Assignment,
  Poll,
  Forum,
  Visibility,
  Publish,
  Unpublished,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import {
  useGetCourseStructureQuery,
  useCreateSectionMutation,
  useUpdateSectionMutation,
  useDeleteSectionMutation,
  useCreateModuleMutation,
  useUpdateModuleMutation,
  useDeleteModuleMutation,
  useCreateLessonMutation,
  useUpdateLessonMutation,
  useDeleteLessonMutation,
  useCreateContentItemMutation,
  useUpdateContentItemMutation,
  useDeleteContentItemMutation,
  useUpdateCourseMutation,
  Section,
  Module,
  Lesson,
  ContentItem,
} from '../../../../features/lms/courseBuilderSlice';
import LessonEditor from './LessonEditor';

// Sortable Activity Item Component
interface SortableActivityProps {
  lesson: Lesson;
  lessonIndex: number;
  moduleId: string;
  onEditLesson: (lesson: Lesson, moduleId: string) => void;
  onDeleteLesson: (lessonId: string) => void;
  onCreateContent: (lessonId: string) => void;
  getContentIcon: (type: ContentItem['content_type']) => React.ReactNode;
}

const SortableActivity: React.FC<SortableActivityProps> = ({
  lesson,
  lessonIndex,
  moduleId,
  onEditLesson,
  onDeleteLesson,
  onCreateContent,
  getContentIcon,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: lesson.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <Card ref={setNodeRef} style={style} variant="outlined" sx={{ mb: 1 }}>
      <CardContent>
        <Stack direction="row" alignItems="center">
          <Box
            {...attributes}
            {...listeners}
            sx={{
              cursor: 'grab',
              '&:active': { cursor: 'grabbing' },
              display: 'flex',
              alignItems: 'center',
              mr: 2,
            }}
          >
            <DragIndicator color="action" />
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="subtitle1">
              Activity {lessonIndex + 1}: {lesson.title}
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
              <Chip label={lesson.lesson_type} size="small" />
              {!lesson.is_required && <Chip label="Optional" size="small" />}
              <Typography variant="caption" color="text.secondary">
                {(lesson.content_data?.media_files?.length || 0) + (lesson.content_items?.length || 0)} items •{' '}
                {lesson.estimated_duration_minutes || 0} minutes
              </Typography>
            </Stack>

            {lesson.content_items && lesson.content_items.length > 0 && (
              <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                {lesson.content_items.map((item) => (
                  <Chip
                    key={item.id}
                    icon={getContentIcon(item.content_type)}
                    label={item.title}
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Stack>
            )}
          </Box>
          <Stack direction="row" spacing={1}>
            <Button
              size="small"
              onClick={() => onCreateContent(lesson.id)}
            >
              Add Content
            </Button>
            <IconButton
              size="small"
              onClick={() => onEditLesson(lesson, moduleId)}
            >
              <Edit />
            </IconButton>
            <IconButton
              size="small"
              onClick={() => onDeleteLesson(lesson.id)}
            >
              <Delete />
            </IconButton>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
};

const CourseEditor: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();

  const [expandedModule, setExpandedModule] = useState<string | false>(false);
  const [sectionDialog, setSectionDialog] = useState(false);
  const [moduleDialog, setModuleDialog] = useState(false);
  const [lessonDialog, setLessonDialog] = useState(false);
  const [contentDialog, setContentDialog] = useState(false);
  const [courseDescDialog, setCourseDescDialog] = useState(false);
  const [editingSection, setEditingSection] = useState<any | null>(null);
  const [editingModule, setEditingModule] = useState<Module | null>(null);
  const [editingLesson, setEditingLesson] = useState<Lesson | null>(null);
  const [editingContent, setEditingContent] = useState<ContentItem | null>(null);
  const [selectedModuleId, setSelectedModuleId] = useState<string | null>(null);
  const [selectedLessonId, setSelectedLessonId] = useState<string | null>(null);
  const [courseDescription, setCourseDescription] = useState('');

  // Form states
  const [sectionForm, setSectionForm] = useState({
    title: '',
    description: '',
    sequence_order: 1,
    is_optional: false,
    is_locked: false,
  });

  const [moduleForm, setModuleForm] = useState({
    section_id: '',
    title: '',
    description: '',
    sequence_order: 1,
    is_optional: false,
    estimated_duration_minutes: 0,
    learning_objectives: [] as string[],
  });

  const [lessonForm, setLessonForm] = useState({
    title: '',
    description: '',
    sequence_order: 1,
    lesson_type: 'standard' as Lesson['lesson_type'],
    estimated_duration_minutes: 0,
    is_required: true,
  });

  const [contentForm, setContentForm] = useState({
    title: '',
    description: '',
    sequence_order: 1,
    content_type: 'video' as ContentItem['content_type'],
    is_required: true,
    points_possible: 0,
    content_data: {},
  });

  // API hooks
  const { data: courseStructure, isLoading, error, refetch } = useGetCourseStructureQuery(courseId || '');
  const [createSection] = useCreateSectionMutation();
  const [updateSection] = useUpdateSectionMutation();
  const [deleteSection] = useDeleteSectionMutation();
  const [createModule] = useCreateModuleMutation();
  const [updateModule] = useUpdateModuleMutation();
  const [deleteModule] = useDeleteModuleMutation();
  const [createLesson] = useCreateLessonMutation();
  const [updateLesson] = useUpdateLessonMutation();
  const [deleteLesson] = useDeleteLessonMutation();
  const [createContent] = useCreateContentItemMutation();
  const [updateContent] = useUpdateContentItemMutation();
  const [deleteContent] = useDeleteContentItemMutation();
  const [updateCourse, { isLoading: isPublishing }] = useUpdateCourseMutation();

  // Drag and drop sensors
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Handle drag end for activities
  const handleDragEnd = async (event: DragEndEvent, moduleId: string) => {
    const { active, over } = event;

    if (!over || active.id === over.id) {
      return;
    }

    const module = courseStructure?.sections
      ?.flatMap(s => s.modules)
      .find(m => m.id === moduleId);

    if (!module) return;

    const lessons = module.lessons || [];
    const oldIndex = lessons.findIndex(l => l.id === active.id);
    const newIndex = lessons.findIndex(l => l.id === over.id);

    if (oldIndex === -1 || newIndex === -1) return;

    // Reorder the lessons locally
    const reorderedLessons = arrayMove(lessons, oldIndex, newIndex);

    // Update sequence_order for each lesson
    const updates = reorderedLessons.map((lesson, index) => ({
      id: lesson.id,
      sequence_order: index + 1,
    }));

    // Update each lesson's sequence order in the backend
    try {
      await Promise.all(
        updates.map(update =>
          updateLesson({
            id: update.id,
            updates: { sequence_order: update.sequence_order },
          }).unwrap()
        )
      );
      // Refetch to get updated structure
      refetch();
    } catch (error) {
      console.error('Failed to reorder lessons:', error);
    }
  };

  const handleModuleExpand = (moduleId: string) => {
    setExpandedModule(expandedModule === moduleId ? false : moduleId);
  };

  // Section handlers
  const handleSaveSection = async () => {
    try {
      if (editingSection) {
        await updateSection({
          id: editingSection.id,
          updates: sectionForm,
        }).unwrap();
      } else {
        await createSection({
          courseId: courseId!,
          section: sectionForm,
        }).unwrap();
      }
      setSectionDialog(false);
    } catch (error) {
      console.error('Failed to save section:', error);
    }
  };

  const handleDeleteSection = async (sectionId: string) => {
    if (window.confirm('Are you sure you want to delete this section? All modules and content will be deleted.')) {
      try {
        await deleteSection(sectionId).unwrap();
      } catch (error) {
        console.error('Failed to delete section:', error);
      }
    }
  };

  // Module handlers
  const handleCreateModule = () => {
    const sections = courseStructure?.sections || [];

    // If no sections exist, prompt user to create a section first
    if (sections.length === 0) {
      alert('Please create a section first before adding modules.');
      return;
    }

    setEditingModule(null);
    const allModules = sections.flatMap(s => s.modules) || [];

    // Auto-select first section if only one exists
    const defaultSectionId = sections.length === 1 ? sections[0].id : '';

    setModuleForm({
      section_id: defaultSectionId,
      title: '',
      description: '',
      sequence_order: allModules.length + 1,
      is_optional: false,
      estimated_duration_minutes: 0,
      learning_objectives: [],
    });
    setModuleDialog(true);
  };

  const handleEditModule = (module: Module & { section_id?: string }) => {
    setEditingModule(module);
    setModuleForm({
      section_id: module.section_id || '',
      title: module.title,
      description: module.description || '',
      sequence_order: module.sequence_order,
      is_optional: module.is_optional,
      estimated_duration_minutes: module.estimated_duration_minutes || 0,
      learning_objectives: module.learning_objectives || [],
    });
    setModuleDialog(true);
  };

  const handleSaveModule = async () => {
    try {
      if (editingModule) {
        await updateModule({
          id: editingModule.id,
          updates: moduleForm,
        }).unwrap();
      } else {
        await createModule({
          courseId: courseId!,
          module: moduleForm,
        }).unwrap();
      }
      setModuleDialog(false);
    } catch (error) {
      console.error('Failed to save module:', error);
    }
  };

  const handleDeleteModule = async (moduleId: string) => {
    if (window.confirm('Are you sure you want to delete this module? All activities and content will be deleted.')) {
      try {
        await deleteModule(moduleId).unwrap();
      } catch (error) {
        console.error('Failed to delete module:', error);
      }
    }
  };

  // Lesson handlers
  const handleCreateLesson = (moduleId: string) => {
    setSelectedModuleId(moduleId);
    setEditingLesson(null);
    const allModules = courseStructure?.sections?.flatMap(s => s.modules) || [];
    const module = allModules.find(m => m.id === moduleId);
    setLessonForm({
      title: '',
      description: '',
      sequence_order: (module?.lessons.length || 0) + 1,
      lesson_type: 'standard',
      estimated_duration_minutes: 0,
      is_required: true,
    });
    setLessonDialog(true);
  };

  const handleEditLesson = (lesson: Lesson, moduleId: string) => {
    setSelectedModuleId(moduleId);
    setEditingLesson(lesson);
    setLessonForm({
      title: lesson.title,
      description: lesson.description || '',
      sequence_order: lesson.sequence_order,
      lesson_type: lesson.lesson_type,
      estimated_duration_minutes: lesson.estimated_duration_minutes || 0,
      is_required: lesson.is_required,
    });
    setLessonDialog(true);
  };

  const handleSaveLesson = async () => {
    try {
      if (editingLesson) {
        await updateLesson({
          id: editingLesson.id,
          updates: lessonForm,
        }).unwrap();
      } else {
        await createLesson({
          moduleId: selectedModuleId!,
          lesson: lessonForm,
        }).unwrap();
      }
      setLessonDialog(false);
    } catch (error) {
      console.error('Failed to save lesson:', error);
    }
  };

  const handleDeleteLesson = async (lessonId: string) => {
    if (window.confirm('Are you sure you want to delete this lesson? All content will be deleted.')) {
      try {
        await deleteLesson(lessonId).unwrap();
      } catch (error) {
        console.error('Failed to delete lesson:', error);
      }
    }
  };

  // Content handlers
  const handleCreateContent = (lessonId: string) => {
    setSelectedLessonId(lessonId);
    setEditingContent(null);
    setContentForm({
      title: '',
      description: '',
      sequence_order: 1,
      content_type: 'video',
      is_required: true,
      points_possible: 0,
      content_data: {},
    });
    setContentDialog(true);
  };

  const handleEditContent = (content: ContentItem, lessonId: string) => {
    setSelectedLessonId(lessonId);
    setEditingContent(content);
    setContentForm({
      title: content.title,
      description: content.description || '',
      sequence_order: content.sequence_order,
      content_type: content.content_type,
      is_required: content.is_required,
      points_possible: content.points_possible || 0,
      content_data: content.content_data || {},
    });
    setContentDialog(true);
  };

  const handleSaveContent = async () => {
    try {
      if (editingContent) {
        await updateContent({
          id: editingContent.id,
          updates: contentForm,
        }).unwrap();
      } else {
        await createContent({
          lessonId: selectedLessonId!,
          content: contentForm,
        }).unwrap();
      }
      setContentDialog(false);
    } catch (error) {
      console.error('Failed to save content:', error);
    }
  };

  // Publish/Unpublish handler
  const handlePublishToggle = async () => {
    if (!courseStructure?.course) return;

    const isPublished = courseStructure.course.is_published;
    const confirmMessage = isPublished
      ? 'Are you sure you want to unpublish this course? Students will no longer be able to access it.'
      : 'Are you sure you want to publish this course? It will become available to students.';

    if (window.confirm(confirmMessage)) {
      try {
        await updateCourse({
          id: courseId!,
          updates: { is_published: !isPublished }
        }).unwrap();
        // Optionally show success message
      } catch (error) {
        console.error('Failed to update course status:', error);
      }
    }
  };

  // Course description handler
  const handleSaveCourseDescription = async () => {
    try {
      await updateCourse({
        id: courseId!,
        updates: { description: courseDescription }
      }).unwrap();
      setCourseDescDialog(false);
    } catch (error) {
      console.error('Failed to update course description:', error);
    }
  };

  const handleDeleteContent = async (contentId: string) => {
    if (window.confirm('Are you sure you want to delete this content item?')) {
      try {
        await deleteContent(contentId).unwrap();
      } catch (error) {
        console.error('Failed to delete content:', error);
      }
    }
  };

  const getContentIcon = (type: ContentItem['content_type']) => {
    switch (type) {
      case 'video': return <VideoLibrary />;
      case 'document': return <Description />;
      case 'quiz': return <Quiz />;
      case 'assignment': return <Assignment />;
      case 'poll': return <Poll />;
      case 'discussion': return <Forum />;
      default: return <Description />;
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="xl">
        <Skeleton variant="rectangular" height={100} sx={{ mb: 3 }} />
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} variant="rectangular" height={200} sx={{ mb: 2 }} />
        ))}
      </Container>
    );
  }

  if (error || !courseStructure) {
    return (
      <Container maxWidth="xl">
        <Alert severity="error">
          Failed to load course. Please try again.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Button
              startIcon={<ArrowBack />}
              onClick={() => navigate('/lms/instructor/course-builder')}
              sx={{ mb: 2 }}
            >
              Back to Course List
            </Button>
            <Typography variant="h4" gutterBottom>
              {courseStructure.course.title}
            </Typography>
            <Box sx={{ mb: 2 }}>
              {courseStructure.course.description ? (
                <Box>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Typography variant="body1" color="text.secondary">
                      {courseStructure.course.description}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setCourseDescription(courseStructure.course.description || '');
                        setCourseDescDialog(true);
                      }}
                    >
                      <Edit fontSize="small" />
                    </IconButton>
                  </Stack>
                </Box>
              ) : (
                <Button
                  size="small"
                  startIcon={<Add />}
                  onClick={() => {
                    setCourseDescription('');
                    setCourseDescDialog(true);
                  }}
                >
                  Add Course Description
                </Button>
              )}
            </Box>
            <Stack direction="row" spacing={2}>
              <Chip
                label={courseStructure.course.is_published ? 'Published' : 'Draft'}
                color={courseStructure.course.is_published ? 'success' : 'default'}
              />
              <Typography variant="body1" color="text.secondary">
                {courseStructure.sections?.flatMap(s => s.modules).length || 0} modules •{' '}
                {courseStructure.sections?.flatMap(s => s.modules).reduce((acc, m) => acc + m.lessons.length, 0) || 0} activities
              </Typography>
            </Stack>
          </Box>
          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              startIcon={<Visibility />}
              onClick={() => navigate(`/lms/courses/${courseId}/preview`)}
            >
              Preview Course
            </Button>
            <Button
              variant={courseStructure?.course?.is_published ? "outlined" : "contained"}
              color={courseStructure?.course?.is_published ? "error" : "success"}
              startIcon={courseStructure?.course?.is_published ? <Unpublished /> : <Publish />}
              onClick={handlePublishToggle}
              disabled={isPublishing}
            >
              {courseStructure?.course?.is_published ? 'Unpublish' : 'Publish'} Course
            </Button>
            <Button variant="outlined" startIcon={<Add />} onClick={() => {
              setEditingSection(null);
              const sections = courseStructure?.sections || [];
              setSectionForm({
                title: '',
                description: '',
                sequence_order: sections.length + 1,
                is_optional: false,
                is_locked: false,
              });
              setSectionDialog(true);
            }}>
              Add Section
            </Button>
            <Button variant="contained" startIcon={<Add />} onClick={handleCreateModule}>
              Add Module
            </Button>
          </Stack>
        </Stack>
      </Box>

      {(courseStructure.sections?.length || 0) === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            No sections yet
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            Start building your course by adding a section
          </Typography>
          <Button variant="contained" startIcon={<Add />} onClick={() => {
            setEditingSection(null);
            setSectionForm({
              title: '',
              description: '',
              sequence_order: 1,
              is_optional: false,
              is_locked: false,
            });
            setSectionDialog(true);
          }}>
            Create First Section
          </Button>
        </Paper>
      ) : (
        <Stack spacing={3}>
          {courseStructure.sections?.map((section) => (
            <Paper key={section.id} sx={{ p: 2 }}>
              <Stack spacing={2}>
                {/* Section Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="h5" gutterBottom>
                      {section.title}
                    </Typography>
                    {section.description && (
                      <Typography variant="body2" color="text.secondary">
                        {section.description}
                      </Typography>
                    )}
                    <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                      {section.is_optional && <Chip label="Optional" size="small" />}
                      {section.is_locked && <Chip label="Locked" size="small" color="warning" />}
                      <Typography variant="caption" color="text.secondary">
                        {section.modules?.length || 0} modules
                      </Typography>
                    </Stack>
                  </Box>
                  <Stack direction="row" spacing={1}>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setEditingSection(section);
                        setSectionForm({
                          title: section.title,
                          description: section.description || '',
                          sequence_order: section.sequence_order,
                          is_optional: section.is_optional || false,
                          is_locked: section.is_locked || false,
                        });
                        setSectionDialog(true);
                      }}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteSection(section.id)}
                    >
                      <Delete />
                    </IconButton>
                    <Button
                      size="small"
                      startIcon={<Add />}
                      onClick={() => {
                        setEditingModule(null);
                        setModuleForm({
                          section_id: section.id,
                          title: '',
                          description: '',
                          sequence_order: (section.modules?.length || 0) + 1,
                          is_optional: false,
                          estimated_duration_minutes: 0,
                          learning_objectives: [],
                        });
                        setModuleDialog(true);
                      }}
                    >
                      Add Module
                    </Button>
                  </Stack>
                </Box>

                <Divider />

                {/* Modules within Section */}
                {section.modules && section.modules.length > 0 ? (
                  <Stack spacing={2}>
                    {section.modules.map((module) => (
                      <Accordion
                        key={module.id}
                        expanded={expandedModule === module.id}
                        onChange={() => handleModuleExpand(module.id)}
                      >
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Stack direction="row" spacing={2} alignItems="center" sx={{ width: '100%', pr: 2 }}>
                  <DragIndicator color="action" />
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6">
                      Module {module.sequence_order}: {module.title}
                    </Typography>
                    <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
                      {module.is_optional && <Chip label="Optional" size="small" />}
                      <Typography variant="caption" color="text.secondary">
                        {module.lessons?.length || 0} activities •{' '}
                        {module.estimated_duration_minutes || 0} minutes
                      </Typography>
                    </Stack>
                  </Box>
                  <Stack direction="row" spacing={1}>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditModule(module);
                      }}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteModule(module.id);
                      }}
                    >
                      <Delete />
                    </IconButton>
                  </Stack>
                </Stack>
              </AccordionSummary>
              <AccordionDetails>
                <Box>
                  {module.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {module.description}
                    </Typography>
                  )}

                  {module.learning_objectives && module.learning_objectives.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Learning Objectives:
                      </Typography>
                      <List dense>
                        {module.learning_objectives.map((obj, idx) => (
                          <ListItem key={idx}>
                            <ListItemText primary={`• ${obj}`} />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  <Divider sx={{ my: 2 }} />

                  <Box>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                      <Typography variant="subtitle1">Activities</Typography>
                      <Button
                        size="small"
                        startIcon={<Add />}
                        onClick={() => handleCreateLesson(module.id)}
                      >
                        Add Activity
                      </Button>
                    </Stack>

                    {!module.lessons || module.lessons.length === 0 ? (
                      <Typography color="text.secondary">No activities yet</Typography>
                    ) : (
                      <DndContext
                        sensors={sensors}
                        collisionDetection={closestCenter}
                        onDragEnd={(event) => handleDragEnd(event, module.id)}
                      >
                        <SortableContext
                          items={module.lessons.map(l => l.id)}
                          strategy={verticalListSortingStrategy}
                        >
                          <Stack spacing={1}>
                            {module.lessons.map((lesson, lessonIndex) => (
                              <SortableActivity
                                key={lesson.id}
                                lesson={lesson}
                                lessonIndex={lessonIndex}
                                moduleId={module.id}
                                onEditLesson={handleEditLesson}
                                onDeleteLesson={handleDeleteLesson}
                                onCreateContent={handleCreateContent}
                                getContentIcon={getContentIcon}
                              />
                            ))}
                          </Stack>
                        </SortableContext>
                      </DndContext>
                    )}
                  </Box>
                </Box>
              </AccordionDetails>
            </Accordion>
                  ))}
                </Stack>
              ) : (
                <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'background.default' }}>
                  <Typography variant="body2" color="text.secondary">
                    No modules in this section yet
                  </Typography>
                </Paper>
              )}
            </Stack>
          </Paper>
        ))}
      </Stack>
    )}

      {/* Course Description Dialog */}
      <Dialog open={courseDescDialog} onClose={() => setCourseDescDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Course Description</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <TextField
              label="Course Description"
              value={courseDescription}
              onChange={(e) => setCourseDescription(e.target.value)}
              fullWidth
              multiline
              rows={6}
              placeholder="Provide a detailed description of what students will learn in this course..."
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCourseDescDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveCourseDescription} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Section Dialog */}
      <Dialog open={sectionDialog} onClose={() => setSectionDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{editingSection ? 'Edit Section' : 'Create Section'}</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
            <TextField
              label="Section Title"
              value={sectionForm.title}
              onChange={(e) => setSectionForm({ ...sectionForm, title: e.target.value })}
              fullWidth
              required
              placeholder="e.g., Week 1, Module 1, Introduction, etc."
            />
            <TextField
              label="Description"
              value={sectionForm.description}
              onChange={(e) => setSectionForm({ ...sectionForm, description: e.target.value })}
              fullWidth
              multiline
              rows={3}
              placeholder="Describe what this section covers..."
            />
            <TextField
              label="Sequence Order"
              type="number"
              value={sectionForm.sequence_order}
              onChange={(e) => setSectionForm({ ...sectionForm, sequence_order: Number(e.target.value) })}
              fullWidth
            />
            <FormControlLabel
              control={
                <Switch
                  checked={sectionForm.is_optional}
                  onChange={(e) => setSectionForm({ ...sectionForm, is_optional: e.target.checked })}
                />
              }
              label="Optional Section"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={sectionForm.is_locked}
                  onChange={(e) => setSectionForm({ ...sectionForm, is_locked: e.target.checked })}
                />
              }
              label="Locked (requires previous sections to be completed)"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSectionDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveSection} variant="contained" disabled={!sectionForm.title}>
            {editingSection ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Module Dialog */}
      <Dialog open={moduleDialog} onClose={() => setModuleDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{editingModule ? 'Edit Module' : 'Create Module'}</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
            <FormControl fullWidth required>
              <InputLabel>Section</InputLabel>
              <Select
                value={moduleForm.section_id}
                onChange={(e) => setModuleForm({ ...moduleForm, section_id: e.target.value })}
                label="Section"
              >
                {courseStructure?.sections?.map((section) => (
                  <MenuItem key={section.id} value={section.id}>
                    {section.title}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Module Title"
              value={moduleForm.title}
              onChange={(e) => setModuleForm({ ...moduleForm, title: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Description"
              value={moduleForm.description}
              onChange={(e) => setModuleForm({ ...moduleForm, description: e.target.value })}
              fullWidth
              multiline
              rows={3}
            />
            <TextField
              label="Sequence Order"
              type="number"
              value={moduleForm.sequence_order}
              onChange={(e) => setModuleForm({ ...moduleForm, sequence_order: Number(e.target.value) })}
              fullWidth
            />
            <TextField
              label="Estimated Duration (minutes)"
              type="number"
              value={moduleForm.estimated_duration_minutes}
              onChange={(e) => setModuleForm({ ...moduleForm, estimated_duration_minutes: Number(e.target.value) })}
              fullWidth
            />
            <FormControlLabel
              control={
                <Switch
                  checked={moduleForm.is_optional}
                  onChange={(e) => setModuleForm({ ...moduleForm, is_optional: e.target.checked })}
                />
              }
              label="Optional Module"
            />
            <TextField
              label="Learning Objectives (one per line)"
              value={moduleForm.learning_objectives.join('\n')}
              onChange={(e) => setModuleForm({
                ...moduleForm,
                learning_objectives: e.target.value.split('\n').filter(o => o.trim())
              })}
              fullWidth
              multiline
              rows={3}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setModuleDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveModule} variant="contained" disabled={!moduleForm.title}>
            {editingModule ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Lesson Editor Dialog */}
      <LessonEditor
        open={lessonDialog}
        onClose={() => {
          setLessonDialog(false);
          setEditingLesson(null);
          setSelectedModuleId(null);
          // RTK Query will auto-update via cache invalidation tags
        }}
        courseId={courseId || ''}
        moduleId={selectedModuleId || ''}
        lesson={editingLesson}
        isEdit={!!editingLesson}
        sequenceOrder={lessonForm.sequence_order}
      />

      {/* Content Dialog */}
      <Dialog open={contentDialog} onClose={() => setContentDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{editingContent ? 'Edit Content' : 'Add Content'}</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
            <TextField
              label="Content Title"
              value={contentForm.title}
              onChange={(e) => setContentForm({ ...contentForm, title: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Description"
              value={contentForm.description}
              onChange={(e) => setContentForm({ ...contentForm, description: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
            <FormControl fullWidth>
              <InputLabel>Content Type</InputLabel>
              <Select
                value={contentForm.content_type}
                onChange={(e) => setContentForm({ ...contentForm, content_type: e.target.value as ContentItem['content_type'] })}
                label="Content Type"
              >
                <MenuItem value="video">Video</MenuItem>
                <MenuItem value="document">Document</MenuItem>
                <MenuItem value="quiz">Quiz</MenuItem>
                <MenuItem value="assignment">Assignment</MenuItem>
                <MenuItem value="discussion">Discussion</MenuItem>
                <MenuItem value="poll">Poll</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Sequence Order"
              type="number"
              value={contentForm.sequence_order}
              onChange={(e) => setContentForm({ ...contentForm, sequence_order: Number(e.target.value) })}
              fullWidth
            />
            {(contentForm.content_type === 'quiz' || contentForm.content_type === 'assignment') && (
              <TextField
                label="Points Possible"
                type="number"
                value={contentForm.points_possible}
                onChange={(e) => setContentForm({ ...contentForm, points_possible: Number(e.target.value) })}
                fullWidth
              />
            )}
            <FormControlLabel
              control={
                <Switch
                  checked={contentForm.is_required}
                  onChange={(e) => setContentForm({ ...contentForm, is_required: e.target.checked })}
                />
              }
              label="Required Content"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setContentDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveContent} variant="contained" disabled={!contentForm.title}>
            {editingContent ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CourseEditor;