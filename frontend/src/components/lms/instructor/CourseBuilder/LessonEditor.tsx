import React, { useState, useRef, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Chip,
  Stack,
  Alert,
  CircularProgress,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Paper,
  Switch,
  FormControlLabel,
  Divider,
  Radio,
  RadioGroup,
  Checkbox,
  FormGroup,
  Card,
  CardContent,
} from '@mui/material';
import {
  CloudUpload,
  VideoLibrary,
  Article,
  Quiz,
  TouchApp,
  Delete,
  AttachFile,
  Close,
  Add,
  DragIndicator,
  Forum,
  Code,
} from '@mui/icons-material';
import {
  useCreateLessonMutation,
  useUpdateLessonMutation,
  useUploadLessonMediaMutation,
  useDeleteLessonMediaMutation,
  useLinkExistingMediaMutation,
  useGetCourseMediaQuery,
} from '../../../../features/lms/courseBuilderSlice';
import RichTextEditor from '../../../common/RichTextEditor';

interface LessonEditorProps {
  open: boolean;
  onClose: () => void;
  courseId: string;
  moduleId: string;
  lesson?: any;
  isEdit?: boolean;
  sequenceOrder?: number;
}

const LessonEditor: React.FC<LessonEditorProps> = ({
  open,
  onClose,
  courseId,
  moduleId,
  lesson,
  isEdit = false,
  sequenceOrder = 1,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const resourceInputRef = useRef<HTMLInputElement>(null);

  const [createLesson, { isLoading: isCreating }] = useCreateLessonMutation();
  const [updateLesson, { isLoading: isUpdating }] = useUpdateLessonMutation();
  const [uploadMedia, { isLoading: isUploading }] = useUploadLessonMediaMutation();
  const [deleteMedia] = useDeleteLessonMediaMutation();
  const [linkMedia, { isLoading: isLinking }] = useLinkExistingMediaMutation();

  // Fetch existing course videos for reuse
  const { data: courseVideos = [], isLoading: isLoadingVideos } = useGetCourseMediaQuery(
    { courseId, mediaType: 'video' },
    { skip: !courseId }
  );

  const [formData, setFormData] = useState({
    title: lesson?.title || '',
    description: lesson?.description || '',
    lesson_type: lesson?.lesson_type || 'standard',
    estimated_duration_minutes: lesson?.estimated_duration_minutes || 15,
    is_required: lesson?.is_required ?? true,
    sequence_order: lesson?.sequence_order || sequenceOrder,
    content_data: lesson?.content_data || {},
  });

  const [uploadedFiles, setUploadedFiles] = useState<any[]>(
    lesson?.content_data?.media_files || []
  );
  const [uploadError, setUploadError] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // RAG metadata state
  const [showMetadataForm, setShowMetadataForm] = useState(false);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [pendingMediaType, setPendingMediaType] = useState<string>('');
  const [metadata, setMetadata] = useState({
    display_name: '',
    document_source: 'Dave Ulrich HR Academy',
    document_type: 'Video',
    capability_domain: '',
    author: '',
    publication_date: '',
    description: '',
  });

  // Video upload mode state
  const [videoUploadMode, setVideoUploadMode] = useState<'new' | 'existing'>('new');
  const [selectedExistingVideo, setSelectedExistingVideo] = useState<any>(null);

  // Quiz-specific state
  const [quizQuestions, setQuizQuestions] = useState<any[]>([]);
  const [passingScore, setPassingScore] = useState(70);
  const [currentQuestion, setCurrentQuestion] = useState({
    question: '',
    type: 'multiple_choice',
    options: ['', '', '', ''],
    correct_answer: 0,
    explanation: '',
    points: 1,
  });

  // Reset form data when the dialog opens with different props
  useEffect(() => {
    if (open) {
      console.log('LessonEditor opened with lesson:', lesson);
      console.log('Media files in lesson.content_data:', lesson?.content_data?.media_files);

      setFormData({
        title: lesson?.title || '',
        description: lesson?.description || '',
        lesson_type: lesson?.lesson_type || 'standard',
        estimated_duration_minutes: lesson?.estimated_duration_minutes || 15,
        is_required: lesson?.is_required ?? true,
        sequence_order: lesson?.sequence_order || sequenceOrder,
        content_data: lesson?.content_data || {},
      });
      setUploadedFiles(lesson?.content_data?.media_files || []);
      // Load existing quiz questions when editing
      setQuizQuestions(lesson?.content_data?.quiz_questions || []);
      setPassingScore(lesson?.content_data?.passing_score || 70);
      setCurrentQuestion({
        question: '',
        type: 'multiple_choice',
        options: ['', '', '', ''],
        correct_answer: 0,
        explanation: '',
        points: 1,
      });
      setUploadError('');
      setIsSubmitting(false);
    }
  }, [open, lesson, sequenceOrder]);

  const handleLessonTypeChange = (event: any) => {
    setFormData({ ...formData, lesson_type: event.target.value });
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>, mediaType: string) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    // Must have a saved lesson to upload to
    if (!lesson?.id) {
      setUploadError('Please save the activity first before uploading files');
      return;
    }

    // For now, only handle single file at a time with metadata
    const file = files[0];

    // Show metadata form for video uploads
    if (mediaType === 'video') {
      setPendingFile(file);
      setPendingMediaType(mediaType);
      setMetadata({
        display_name: file.name,
        document_source: 'Dave Ulrich HR Academy',
        document_type: 'Video',
        capability_domain: '',
        author: '',
        publication_date: '',
        description: '',
      });
      setShowMetadataForm(true);
    } else {
      // For non-video files, upload directly without metadata
      await performUpload(file, mediaType, {});
    }
  };

  const performUpload = async (file: File, mediaType: string, metadataFields: any) => {
    const formDataToSend = new FormData();
    formDataToSend.append('file', file);
    formDataToSend.append('media_type', mediaType);
    formDataToSend.append('title', file.name);

    // Add RAG metadata fields if provided
    if (metadataFields.display_name) {
      formDataToSend.append('display_name', metadataFields.display_name);
    }
    if (metadataFields.document_source) {
      formDataToSend.append('document_source', metadataFields.document_source);
    }
    if (metadataFields.document_type) {
      formDataToSend.append('document_type', metadataFields.document_type);
    }
    if (metadataFields.capability_domain) {
      formDataToSend.append('capability_domain', metadataFields.capability_domain);
    }
    if (metadataFields.author) {
      formDataToSend.append('author', metadataFields.author);
    }
    if (metadataFields.publication_date) {
      formDataToSend.append('publication_date', metadataFields.publication_date);
    }
    if (metadataFields.description) {
      formDataToSend.append('description', metadataFields.description);
    }

    try {
      const result = await uploadMedia({
        lessonId: lesson!.id,
        formData: formDataToSend,
      }).unwrap();

      setUploadedFiles(prevFiles => [...prevFiles, result.media]);
      setUploadError('');
    } catch (error: any) {
      setUploadError(`Failed to upload ${file.name}: ${error?.data?.detail || 'Unknown error'}`);
    }
  };

  const handleMetadataSubmit = async () => {
    if (!pendingFile) return;

    await performUpload(pendingFile, pendingMediaType, metadata);

    // Reset state
    setShowMetadataForm(false);
    setPendingFile(null);
    setPendingMediaType('');
    setMetadata({
      display_name: '',
      document_source: 'Dave Ulrich HR Academy',
      document_type: 'Video',
      capability_domain: '',
      author: '',
      publication_date: '',
      description: '',
    });
  };

  const handleDeleteMedia = async (mediaId: string) => {
    if (!lesson?.id) return;

    try {
      await deleteMedia({
        lessonId: lesson.id,
        mediaId,
      }).unwrap();

      setUploadedFiles(uploadedFiles.filter(f => f.id !== mediaId));
    } catch (error) {
      console.error('Failed to delete media:', error);
    }
  };

  const handleSubmit = async () => {
    // Prevent double submission
    if (isSubmitting || isCreating || isUpdating) {
      console.log('[LessonEditor] Submission already in progress, skipping...');
      return;
    }

    console.log('[LessonEditor] handleSubmit called', { isEdit, lessonId: lesson?.id, moduleId });

    try {
      setIsSubmitting(true);

      // Prepare lesson data
      const lessonData: any = { ...formData };

      // IMPORTANT: Don't send media_files - they're managed separately in LessonMedia table
      const { media_files, ...contentDataWithoutMedia } = lessonData.content_data || {};

      // Build content_data based on lesson type
      if (formData.lesson_type === 'quiz' && quizQuestions.length > 0) {
        lessonData.content_data = {
          ...contentDataWithoutMedia,
          quiz_questions: quizQuestions,
          passing_score: passingScore,
          total_points: quizQuestions.reduce((sum: number, q: any) => sum + q.points, 0),
        };
      } else if (formData.lesson_type === 'video') {
        lessonData.content_data = {
          ...contentDataWithoutMedia,
          video_url: formData.content_data?.video_url || '',
        };
      } else {
        lessonData.content_data = contentDataWithoutMedia;
      }

      // Create or update lesson
      let lessonId: string;
      if (isEdit && lesson) {
        console.log('[LessonEditor] Updating existing lesson:', lesson.id);
        await updateLesson({
          id: lesson.id,
          updates: lessonData,
        }).unwrap();
        lessonId = lesson.id;
      } else {
        console.log('[LessonEditor] Creating new lesson in module:', moduleId);
        const result = await createLesson({
          moduleId,
          lesson: lessonData,
        }).unwrap();
        console.log('[LessonEditor] Lesson created successfully:', result);
        lessonId = result.id;
      }

      // If using existing video and one is selected, link it to the lesson
      if (formData.lesson_type === 'video' && videoUploadMode === 'existing' && selectedExistingVideo) {
        console.log('[LessonEditor] Linking existing video:', selectedExistingVideo.id, 'to lesson:', lessonId);
        await linkMedia({
          lessonId,
          mediaId: selectedExistingVideo.id,
        }).unwrap();
        console.log('[LessonEditor] Video linked successfully');
      }

      console.log('[LessonEditor] Closing dialog after successful save');
      onClose();
    } catch (error: any) {
      console.error('[LessonEditor] Failed to save activity:', error);
      setUploadError(`Failed to save activity: ${error?.data?.detail || 'Unknown error'}`);
      setIsSubmitting(false);
    }
  };

  const renderTypeSpecificFields = () => {
    switch (formData.lesson_type) {
      case 'video':
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              <VideoLibrary sx={{ mr: 1, verticalAlign: 'middle' }} />
              Video Content
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Video Introduction Text
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
                    This text will be displayed below the video to provide context or instructions
                  </Typography>
                  <RichTextEditor
                    value={formData.description}
                    onChange={(value) => setFormData({ ...formData, description: value })}
                    placeholder="Enter introductory text that will appear below the video..."
                    minHeight={150}
                  />
                </Box>

                <TextField
                  label="Video URL (YouTube, Vimeo, or Cloud Link)"
                  fullWidth
                  placeholder="https://youtube.com/watch?v=... or https://..."
                  value={formData.content_data?.video_url || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    content_data: { ...formData.content_data, video_url: e.target.value }
                  })}
                  helperText="Paste a YouTube, Vimeo, or direct video URL"
                />

                <Typography variant="body2" color="text.secondary" align="center">
                  - OR -
                </Typography>

                <Divider />

                {/* Toggle between upload new and use existing */}
                <RadioGroup
                  row
                  value={videoUploadMode}
                  onChange={(e) => setVideoUploadMode(e.target.value as 'new' | 'existing')}
                >
                  <FormControlLabel value="new" control={<Radio />} label="Upload New Video" />
                  <FormControlLabel value="existing" control={<Radio />} label="Use Existing Video" />
                </RadioGroup>

                {videoUploadMode === 'new' ? (
                  <>
                    <Box>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".mp4,.webm,.mov,.avi,.mkv"
                        onChange={(e) => handleFileUpload(e, 'video')}
                        style={{ display: 'none' }}
                        multiple
                      />
                      <Button
                        variant="outlined"
                        startIcon={<CloudUpload />}
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading || !lesson?.id}
                        fullWidth
                      >
                        {lesson?.id ? 'Upload Video File' : 'Save activity first to upload files'}
                      </Button>
                    </Box>

                    {isUploading && (
                      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                        <CircularProgress size={24} />
                      </Box>
                    )}

                    {uploadedFiles.filter(f => f.type === 'video').length > 0 && (
                      <List>
                        {uploadedFiles.filter(f => f.type === 'video').map((file) => (
                          <ListItem key={file.id}>
                            <ListItemText
                              primary={file.title}
                              secondary={`Size: ${(file.size / 1024 / 1024).toFixed(2)} MB`}
                            />
                            <ListItemSecondaryAction>
                              <IconButton edge="end" onClick={() => handleDeleteMedia(file.id)}>
                                <Delete />
                              </IconButton>
                            </ListItemSecondaryAction>
                          </ListItem>
                        ))}
                      </List>
                    )}
                  </>
                ) : (
                  <Box>
                    {isLoadingVideos ? (
                      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                        <CircularProgress />
                      </Box>
                    ) : courseVideos.length === 0 ? (
                      <Alert severity="info">
                        No existing videos found in this course. Upload a new video instead.
                      </Alert>
                    ) : (
                      <>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Select a video from the course library:
                        </Typography>
                        <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
                          {courseVideos.map((video: any) => (
                            <Card
                              key={video.id}
                              sx={{
                                mb: 2,
                                cursor: 'pointer',
                                border: selectedExistingVideo?.id === video.id ? 2 : 1,
                                borderColor: selectedExistingVideo?.id === video.id ? 'primary.main' : 'divider',
                              }}
                              onClick={() => setSelectedExistingVideo(video)}
                            >
                              <CardContent>
                                <Stack direction="row" spacing={2} alignItems="center">
                                  <VideoLibrary sx={{ fontSize: 40, color: 'primary.main' }} />
                                  <Box sx={{ flexGrow: 1 }}>
                                    <Typography variant="subtitle1" fontWeight="bold">
                                      {video.title}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                      {video.description || 'No description'}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                      From: {video.lesson?.module?.section?.title} › {video.lesson?.module?.title} › {video.lesson?.title}
                                    </Typography>
                                    <Typography variant="caption" display="block">
                                      Size: {(video.size / 1024 / 1024).toFixed(2)} MB
                                    </Typography>
                                  </Box>
                                  {selectedExistingVideo?.id === video.id && (
                                    <Chip label="Selected" color="primary" size="small" />
                                  )}
                                </Stack>
                              </CardContent>
                            </Card>
                          ))}
                        </Box>
                        {selectedExistingVideo && (
                          <Alert severity="success" sx={{ mt: 2 }}>
                            Selected: {selectedExistingVideo.title}
                          </Alert>
                        )}
                      </>
                    )}
                  </Box>
                )}
              </Stack>
            </Paper>
          </Box>
        );

      case 'reading':
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              <Article sx={{ mr: 1, verticalAlign: 'middle' }} />
              Reading Material
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Reading Content
                  </Typography>
                  <RichTextEditor
                    value={formData.description}
                    onChange={(value) => setFormData({ ...formData, description: value })}
                    placeholder="Enter the reading content or instructions..."
                    minHeight={200}
                  />
                </Box>
                <Box>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.doc,.docx,.txt,.ppt,.pptx"
                    onChange={(e) => handleFileUpload(e, 'document')}
                    style={{ display: 'none' }}
                    multiple
                  />
                  <Button
                    variant="outlined"
                    startIcon={<CloudUpload />}
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploading || !lesson?.id}
                    fullWidth
                  >
                    {lesson?.id ? 'Upload Documents' : 'Save activity first to upload files'}
                  </Button>
                </Box>

                {uploadedFiles.filter(f => f.type === 'document').length > 0 && (
                  <List>
                    {uploadedFiles.filter(f => f.type === 'document').map((file) => (
                      <ListItem key={file.id}>
                        <ListItemText
                          primary={file.title}
                          secondary={file.description}
                        />
                        <ListItemSecondaryAction>
                          <IconButton edge="end" onClick={() => handleDeleteMedia(file.id)}>
                            <Delete />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                )}
              </Stack>
            </Paper>
          </Box>
        );

      case 'interactive':
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              <TouchApp sx={{ mr: 1, verticalAlign: 'middle' }} />
              Interactive Content
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Interactive Instructions
                  </Typography>
                  <RichTextEditor
                    value={formData.description}
                    onChange={(value) => setFormData({ ...formData, description: value })}
                    placeholder="Describe the interactive activity..."
                    minHeight={150}
                  />
                </Box>
                <Alert severity="info">
                  Interactive activities can include simulations, hands-on exercises, or collaborative exercises.
                </Alert>
              </Stack>
            </Paper>
          </Box>
        );

      case 'quiz':
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              <Quiz sx={{ mr: 1, verticalAlign: 'middle' }} />
              Quiz
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
              <Stack spacing={2}>
                <TextField
                  label="Quiz Title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  fullWidth
                  required
                />
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Quiz Instructions
                  </Typography>
                  <RichTextEditor
                    value={formData.description}
                    onChange={(value) => setFormData({ ...formData, description: value })}
                    placeholder="Provide instructions for the quiz..."
                    minHeight={120}
                  />
                </Box>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <TextField
                    label="Time Limit (minutes)"
                    type="number"
                    value={formData.estimated_duration_minutes}
                    onChange={(e) => setFormData({
                      ...formData,
                      estimated_duration_minutes: parseInt(e.target.value)
                    })}
                    sx={{ flexGrow: 1 }}
                    helperText="Leave empty for no time limit"
                  />
                  <TextField
                    label="Passing Score (%)"
                    type="number"
                    value={passingScore}
                    onChange={(e) => setPassingScore(parseInt(e.target.value))}
                    sx={{ flexGrow: 1 }}
                    helperText="Minimum score to pass"
                  />
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Quiz Questions Section */}
                <Typography variant="subtitle1" fontWeight="medium">
                  Quiz Questions
                </Typography>

                {/* Add Question Form */}
                <Card variant="outlined">
                  <CardContent>
                    <Stack spacing={2}>
                      <TextField
                        label="Question"
                        value={currentQuestion.question}
                        onChange={(e) => setCurrentQuestion({ ...currentQuestion, question: e.target.value })}
                        fullWidth
                        multiline
                        rows={2}
                      />

                      <FormControl fullWidth size="small">
                        <InputLabel>Question Type</InputLabel>
                        <Select
                          value={currentQuestion.type}
                          onChange={(e) => setCurrentQuestion({ ...currentQuestion, type: e.target.value })}
                          label="Question Type"
                        >
                          <MenuItem value="multiple_choice">Multiple Choice</MenuItem>
                          <MenuItem value="true_false">True/False</MenuItem>
                          <MenuItem value="short_answer">Short Answer</MenuItem>
                        </Select>
                      </FormControl>

                      {currentQuestion.type === 'multiple_choice' && (
                        <>
                          <Typography variant="body2" color="text.secondary">
                            Options (select the correct answer):
                          </Typography>
                          <RadioGroup
                            value={currentQuestion.correct_answer}
                            onChange={(e) => setCurrentQuestion({ ...currentQuestion, correct_answer: parseInt(e.target.value) })}
                          >
                            {currentQuestion.options.map((option: string, index: number) => (
                              <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Radio value={index} size="small" />
                                <TextField
                                  value={option}
                                  onChange={(e) => {
                                    const newOptions = [...currentQuestion.options];
                                    newOptions[index] = e.target.value;
                                    setCurrentQuestion({ ...currentQuestion, options: newOptions });
                                  }}
                                  placeholder={`Option ${index + 1}`}
                                  size="small"
                                  fullWidth
                                />
                              </Box>
                            ))}
                          </RadioGroup>
                        </>
                      )}

                      {currentQuestion.type === 'true_false' && (
                        <RadioGroup
                          value={currentQuestion.correct_answer}
                          onChange={(e) => setCurrentQuestion({ ...currentQuestion, correct_answer: e.target.value })}
                        >
                          <FormControlLabel value="true" control={<Radio />} label="True" />
                          <FormControlLabel value="false" control={<Radio />} label="False" />
                        </RadioGroup>
                      )}

                      {currentQuestion.type === 'short_answer' && (
                        <TextField
                          label="Correct Answer"
                          value={currentQuestion.correct_answer}
                          onChange={(e) => setCurrentQuestion({ ...currentQuestion, correct_answer: e.target.value })}
                          fullWidth
                          helperText="Enter the expected answer for short answer questions"
                        />
                      )}

                      <TextField
                        label="Explanation (optional)"
                        value={currentQuestion.explanation}
                        onChange={(e) => setCurrentQuestion({ ...currentQuestion, explanation: e.target.value })}
                        fullWidth
                        multiline
                        rows={2}
                        helperText="Shown after the student answers"
                      />

                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <TextField
                          label="Points"
                          type="number"
                          value={currentQuestion.points}
                          onChange={(e) => setCurrentQuestion({ ...currentQuestion, points: parseInt(e.target.value) })}
                          sx={{ width: 120 }}
                        />
                        <Button
                          variant="contained"
                          startIcon={<Add />}
                          onClick={() => {
                            if (currentQuestion.question) {
                              setQuizQuestions([...quizQuestions, { ...currentQuestion, id: Date.now() }]);
                              setCurrentQuestion({
                                question: '',
                                type: 'multiple_choice',
                                options: ['', '', '', ''],
                                correct_answer: 0,
                                explanation: '',
                                points: 1,
                              });
                            }
                          }}
                          disabled={!currentQuestion.question}
                        >
                          Add Question
                        </Button>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>

                {/* Questions List */}
                {quizQuestions.length > 0 && (
                  <>
                    <Typography variant="subtitle2" color="text.secondary">
                      {quizQuestions.length} question(s) • Total points: {quizQuestions.reduce((sum, q) => sum + q.points, 0)}
                    </Typography>
                    <List>
                      {quizQuestions.map((q, index) => (
                        <ListItem key={q.id}>
                          <ListItemText
                            primary={`${index + 1}. ${q.question}`}
                            secondary={`${q.type.replace('_', ' ')} • ${q.points} point(s)`}
                          />
                          <ListItemSecondaryAction>
                            <IconButton
                              edge="end"
                              onClick={() => setQuizQuestions(quizQuestions.filter(question => question.id !== q.id))}
                            >
                              <Delete />
                            </IconButton>
                          </ListItemSecondaryAction>
                        </ListItem>
                      ))}
                    </List>
                  </>
                )}
              </Stack>
            </Paper>
          </Box>
        );

      case 'discussion':
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              <Forum sx={{ mr: 1, verticalAlign: 'middle' }} />
              Discussion Forum
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
              <Stack spacing={2}>
                <TextField
                  label="Discussion Topic"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  fullWidth
                  required
                  placeholder="What topic should students discuss?"
                />
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Discussion Prompt *
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
                    This will be the initial prompt students see when they enter the discussion
                  </Typography>
                  <RichTextEditor
                    value={formData.description}
                    onChange={(value) => setFormData({ ...formData, description: value })}
                    placeholder="Provide a thought-provoking prompt or question to start the discussion..."
                    minHeight={150}
                  />
                </Box>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.content_data?.allow_anonymous || false}
                      onChange={(e) => setFormData({
                        ...formData,
                        content_data: {
                          ...formData.content_data,
                          allow_anonymous: e.target.checked
                        }
                      })}
                    />
                  }
                  label="Allow anonymous posts"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.content_data?.require_initial_post || false}
                      onChange={(e) => setFormData({
                        ...formData,
                        content_data: {
                          ...formData.content_data,
                          require_initial_post: e.target.checked
                        }
                      })}
                    />
                  }
                  label="Require initial post before viewing others' posts"
                />
                <TextField
                  label="Minimum Posts Required"
                  type="number"
                  value={formData.content_data?.min_posts || 1}
                  onChange={(e) => setFormData({
                    ...formData,
                    content_data: {
                      ...formData.content_data,
                      min_posts: parseInt(e.target.value) || 1
                    }
                  })}
                  helperText="Minimum number of posts required for completion"
                  sx={{ maxWidth: 200 }}
                />
                <Alert severity="info">
                  Students will be able to create threads, reply to posts, and engage in meaningful discussions about this topic.
                </Alert>
              </Stack>
            </Paper>
          </Box>
        );

      case 'embed':
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              <Code sx={{ mr: 1, verticalAlign: 'middle' }} />
              Embedded Content (iframe)
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
              <Stack spacing={2}>
                <TextField
                  label="Embed URL"
                  fullWidth
                  required
                  placeholder="https://example.com/embed/..."
                  value={formData.content_data?.embed_url || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    content_data: { ...formData.content_data, embed_url: e.target.value }
                  })}
                  helperText="Enter the URL to embed (e.g., Google Slides, Forms, external tools, etc.)"
                />

                <TextField
                  label="iframe Height (pixels)"
                  type="number"
                  placeholder="600"
                  value={formData.content_data?.iframe_height || 600}
                  onChange={(e) => setFormData({
                    ...formData,
                    content_data: { ...formData.content_data, iframe_height: parseInt(e.target.value) || 600 }
                  })}
                  helperText="Height of the embedded content in pixels"
                />

                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.content_data?.allow_fullscreen ?? true}
                      onChange={(e) => setFormData({
                        ...formData,
                        content_data: { ...formData.content_data, allow_fullscreen: e.target.checked }
                      })}
                    />
                  }
                  label="Allow fullscreen"
                />

                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Description/Instructions
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
                    Optional description that appears above the embedded content
                  </Typography>
                  <RichTextEditor
                    value={formData.description}
                    onChange={(value) => setFormData({ ...formData, description: value })}
                    placeholder="Add instructions or context for students..."
                    minHeight={120}
                  />
                </Box>
              </Stack>
            </Paper>
          </Box>
        );

      default:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Standard Activity Content
            </Typography>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Activity Content
                </Typography>
                <RichTextEditor
                  value={formData.description}
                  onChange={(value) => setFormData({ ...formData, description: value })}
                  placeholder="Enter the activity content..."
                  minHeight={150}
                />
              </Box>
            </Paper>
          </Box>
        );
    }
  };

  return (
    <>
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {isEdit ? 'Edit Activity' : 'Create New Activity'}
        <IconButton
          onClick={onClose}
          sx={{ position: 'absolute', right: 8, top: 8 }}
        >
          <Close />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <Stack spacing={3} sx={{ mt: 2 }}>
          <TextField
            label="Activity Title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            fullWidth
            required
          />

          <FormControl fullWidth>
            <InputLabel>Activity Type</InputLabel>
            <Select
              value={formData.lesson_type}
              onChange={handleLessonTypeChange}
              label="Activity Type"
            >
              <MenuItem value="standard">Standard Activity</MenuItem>
              <MenuItem value="video">Video Activity</MenuItem>
              <MenuItem value="reading">Reading Material</MenuItem>
              <MenuItem value="interactive">Interactive Activity</MenuItem>
              <MenuItem value="quiz">Quiz</MenuItem>
              <MenuItem value="discussion">Discussion</MenuItem>
              <MenuItem value="embed">Embedded Content (iframe)</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="Estimated Duration (minutes)"
            type="number"
            value={formData.estimated_duration_minutes}
            onChange={(e) => setFormData({
              ...formData,
              estimated_duration_minutes: parseInt(e.target.value)
            })}
            fullWidth
          />

          <FormControlLabel
            control={
              <Switch
                checked={formData.is_required}
                onChange={(e) => setFormData({ ...formData, is_required: e.target.checked })}
              />
            }
            label="Required Activity"
          />

          {renderTypeSpecificFields()}

          {/* Resource Upload Section - Available for all activity types */}
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              <AttachFile sx={{ mr: 1, verticalAlign: 'middle' }} />
              Additional Resources
            </Typography>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Stack spacing={2}>
                <Box>
                  <input
                    ref={resourceInputRef}
                    type="file"
                    accept=".pdf,.doc,.docx,.txt,.zip,.ppt,.pptx,.xls,.xlsx"
                    onChange={(e) => handleFileUpload(e, 'resource')}
                    style={{ display: 'none' }}
                    multiple
                  />
                  <Button
                    variant="outlined"
                    startIcon={<AttachFile />}
                    onClick={() => resourceInputRef.current?.click()}
                    disabled={isUploading || !lesson?.id}
                    fullWidth
                  >
                    {lesson?.id ? 'Upload Resources' : 'Save activity first to upload files'}
                  </Button>
                </Box>

                {uploadedFiles.filter(f => f.type === 'resource').length > 0 && (
                  <List>
                    {uploadedFiles.filter(f => f.type === 'resource').map((file) => (
                      <ListItem key={file.id}>
                        <ListItemText
                          primary={file.title}
                          secondary={`Resource • ${(file.size / 1024).toFixed(1)} KB`}
                        />
                        <ListItemSecondaryAction>
                          <IconButton edge="end" onClick={() => handleDeleteMedia(file.id)}>
                            <Delete />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                )}
              </Stack>
            </Paper>
          </Box>

          {uploadError && (
            <Alert severity="error" onClose={() => setUploadError('')}>
              {uploadError}
            </Alert>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isSubmitting || isCreating || isUpdating || !formData.title}
        >
          {isEdit ? 'Update' : 'Create'} Activity
        </Button>
      </DialogActions>
    </Dialog>

    {/* Metadata Form Dialog */}
    <Dialog open={showMetadataForm} onClose={() => setShowMetadataForm(false)} maxWidth="sm" fullWidth>
      <DialogTitle>
        Video Metadata
        <IconButton
          onClick={() => setShowMetadataForm(false)}
          sx={{ position: 'absolute', right: 8, top: 8 }}
        >
          <Close />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 2 }}>
          <Alert severity="info">
            This metadata helps our AI assistant understand and reference this video accurately.
          </Alert>

          <TextField
            label="Display Name"
            value={metadata.display_name}
            onChange={(e) => setMetadata({ ...metadata, display_name: e.target.value })}
            fullWidth
            required
            helperText="User-friendly name for this video"
          />

          <TextField
            label="Document Source"
            value={metadata.document_source}
            onChange={(e) => setMetadata({ ...metadata, document_source: e.target.value })}
            fullWidth
            helperText="e.g., Dave Ulrich HR Academy, Institute Name"
          />

          <FormControl fullWidth>
            <InputLabel>Document Type</InputLabel>
            <Select
              value={metadata.document_type}
              onChange={(e) => setMetadata({ ...metadata, document_type: e.target.value })}
              label="Document Type"
            >
              <MenuItem value="Video">Video</MenuItem>
              <MenuItem value="Lecture">Lecture</MenuItem>
              <MenuItem value="Tutorial">Tutorial</MenuItem>
              <MenuItem value="Case Study">Case Study</MenuItem>
              <MenuItem value="Interview">Interview</MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth>
            <InputLabel>Human Capability Domain</InputLabel>
            <Select
              value={metadata.capability_domain}
              onChange={(e) => setMetadata({ ...metadata, capability_domain: e.target.value })}
              label="Human Capability Domain"
            >
              <MenuItem value="">None</MenuItem>
              <MenuItem value="Talent">Talent</MenuItem>
              <MenuItem value="Leadership">Leadership</MenuItem>
              <MenuItem value="Organization">Organization</MenuItem>
              <MenuItem value="HR">HR</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="Author"
            value={metadata.author}
            onChange={(e) => setMetadata({ ...metadata, author: e.target.value })}
            fullWidth
            helperText="Name of the content creator or instructor"
          />

          <TextField
            label="Publication Date"
            type="date"
            value={metadata.publication_date}
            onChange={(e) => setMetadata({ ...metadata, publication_date: e.target.value })}
            fullWidth
            InputLabelProps={{ shrink: true }}
          />

          <TextField
            label="Description"
            value={metadata.description}
            onChange={(e) => setMetadata({ ...metadata, description: e.target.value })}
            fullWidth
            multiline
            rows={3}
            helperText="Brief description of the video content"
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowMetadataForm(false)}>Cancel</Button>
        <Button
          onClick={handleMetadataSubmit}
          variant="contained"
          disabled={!metadata.display_name || isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload Video'}
        </Button>
      </DialogActions>
    </Dialog>
    </>
  );
};

export default LessonEditor;