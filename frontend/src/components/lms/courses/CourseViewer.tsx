import React, { useState, useEffect } from 'react';
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
  RadioGroup,
  FormControlLabel,
  Radio,
  Alert,
  CircularProgress,
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
  Visibility,
  Group,
} from '@mui/icons-material';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { useGetCourseQuery, useGetCourseStructureQuery } from '../../../features/lms/courseBuilderSlice';
import { useAppSelector } from '../../../store/hooks';
import { selectCurrentUser, selectIsAdmin, selectIsInstructor } from '../../../store/slices/authSlice';
import LessonChat from './LessonChat';
import LessonQA from './LessonQA';
import LessonNotes from './LessonNotes';
import HtmlContent from '../../common/HtmlContent';

interface Section {
  id: string;
  title: string;
  description: string;
  modules: Module[];
  isOptional: boolean;
  isLocked: boolean;
  order: number;
}

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
  content_data?: any;
  order: number;
}

const CourseViewer = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const versionId = searchParams.get('versionId'); // Get versionId from URL query params
  const currentUser = useAppSelector(selectCurrentUser);
  const isAdmin = useAppSelector(selectIsAdmin);
  const isInstructor = useAppSelector(selectIsInstructor);
  const [selectedLesson, setSelectedLesson] = useState<string>('');
  const [expandedSections, setExpandedSections] = useState<string[]>([]);
  const [expandedModules, setExpandedModules] = useState<string[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [quizStarted, setQuizStarted] = useState(false);
  const [quizAnswers, setQuizAnswers] = useState<Record<string, any>>({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);

  // Reset quiz state when lesson changes
  useEffect(() => {
    setQuizStarted(false);
    setQuizAnswers({});
    setQuizSubmitted(false);
  }, [selectedLesson]);

  // Fetch course structure with modules and lessons
  const { data: courseStructure, isLoading, error } = useGetCourseStructureQuery(courseId!, {
    skip: !courseId,
  });

  // Use real course data from API
  const course = courseStructure?.course;
  const courseData = {
    id: courseId,
    title: course?.title || 'Loading...',
    description: course?.description || '',
    instructor: {
      name: course?.instructor ? `${course.instructor.first_name} ${course.instructor.last_name}` : 'Unknown',
      avatar: null,
      title: course?.instructor?.email || '',
    },
    progress: {
      percentage: 0,
      completedLessons: 0,
      totalLessons: course?.lesson_count || 0,
    },
    // Map real sections from the course structure
    sections: (courseStructure?.sections || []).map((section: any) => ({
      id: section.id,
      title: section.title,
      description: section.description || '',
      isOptional: section.is_optional || false,
      isLocked: section.is_locked || false,
      order: section.sequence_order || 0,
      modules: (section.modules || []).map((module: any) => ({
        id: module.id,
        title: module.title,
        description: module.description || '',
        duration: module.estimated_duration_minutes || 0,
        isCompleted: false,
        order: module.sequence_order || 0,
        lessons: (module.lessons || []).map((lesson: any) => ({
          id: lesson.id,
          title: lesson.title,
          type: lesson.lesson_type || 'video',
          duration: lesson.estimated_duration_minutes || 0,
          isCompleted: false,
          isLocked: false,
          order: lesson.sequence_order || 0,
          content: lesson,
          content_data: lesson.content_data,
        })),
      })),
    })) as Section[],
  };

  const currentLesson = courseData.sections
    .flatMap(s => s.modules)
    .flatMap(m => m.lessons)
    .find(l => l.id === selectedLesson);

  // Find the current module containing the selected lesson
  const currentModule = courseData.sections
    .flatMap(s => s.modules)
    .find(m => m.lessons.some(l => l.id === selectedLesson));

  // Auto-expand current module when a lesson is selected
  useEffect(() => {
    if (selectedLesson && currentModule && !expandedModules.includes(currentModule.id)) {
      setExpandedModules(prev => [...prev, currentModule.id]);
    }
  }, [selectedLesson, currentModule, expandedModules]);

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

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev =>
      prev.includes(sectionId)
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
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
    const allLessons = courseData.sections.flatMap(s => s.modules).flatMap(m => m.lessons);
    const currentIndex = allLessons.findIndex(l => l.id === selectedLesson);
    if (currentIndex < allLessons.length - 1) {
      setSelectedLesson(allLessons[currentIndex + 1].id);
    }
  };

  const navigateToPrevLesson = () => {
    const allLessons = courseData.sections.flatMap(s => s.modules).flatMap(m => m.lessons);
    const currentIndex = allLessons.findIndex(l => l.id === selectedLesson);
    if (currentIndex > 0) {
      setSelectedLesson(allLessons[currentIndex - 1].id);
    }
  };

  const VideoContent = () => {
    const [signedVideoUrl, setSignedVideoUrl] = React.useState<string | null>(null);
    const [isLoadingUrl, setIsLoadingUrl] = React.useState(false);
    const [urlError, setUrlError] = React.useState<string | null>(null);

    // Debug logging to see the data structure
    console.log('Current Lesson:', currentLesson);
    console.log('Content Data:', currentLesson?.content_data);

    // Get video data from lesson's content_data
    const youtubeUrl = currentLesson?.content_data?.video_url;
    const primaryVideo = currentLesson?.content_data?.primary_video;
    const firstMediaFile = currentLesson?.content_data?.media_files?.[0];

    // Determine video source
    const videoMedia = primaryVideo || firstMediaFile;

    // Check if it's a YouTube URL
    const isYouTubeUrl = youtubeUrl && (youtubeUrl.includes('youtube.com') || youtubeUrl.includes('youtu.be'));

    // Extract YouTube video ID
    const getYouTubeId = (url: string) => {
      const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/);
      return match ? match[1] : null;
    };

    const youtubeId = isYouTubeUrl ? getYouTubeId(youtubeUrl!) : null;

    // Fetch signed URL for Supabase-stored videos
    React.useEffect(() => {
      const fetchSignedUrl = async () => {
        if (!currentLesson?.id || !videoMedia?.id) {
          return;
        }

        // Skip if YouTube URL or local storage
        if (isYouTubeUrl || videoMedia.storage === 'local') {
          return;
        }

        // Only fetch for Supabase storage
        if (videoMedia.storage === 'supabase') {
          setIsLoadingUrl(true);
          setUrlError(null);

          try {
            const token = localStorage.getItem('accessToken');
            const apiUrl = process.env.REACT_APP_API_URL || '';

            const response = await fetch(
              `${apiUrl}/api/lms/course-builder/lessons/${currentLesson.id}/media/${videoMedia.id}/signed-url`,
              {
                headers: {
                  'Authorization': `Bearer ${token}`,
                },
              }
            );

            if (!response.ok) {
              if (response.status === 403) {
                setUrlError('You must be enrolled in this course to view this video.');
              } else {
                setUrlError('Failed to load video. Please try again.');
              }
              setIsLoadingUrl(false);
              return;
            }

            const data = await response.json();
            setSignedVideoUrl(data.url);
            setIsLoadingUrl(false);

            // Refresh URL before expiration (50 minutes = 3000 seconds)
            if (data.expires_in) {
              setTimeout(() => {
                fetchSignedUrl();
              }, (data.expires_in - 600) * 1000); // Refresh 10 minutes before expiry
            }
          } catch (error) {
            console.error('Error fetching signed URL:', error);
            setUrlError('Failed to load video. Please check your connection.');
            setIsLoadingUrl(false);
          }
        }
      };

      fetchSignedUrl();
    }, [currentLesson?.id, videoMedia?.id, isYouTubeUrl]);

    // Determine the video URL to use
    const videoUrl = isYouTubeUrl
      ? null  // Use YouTube embed instead
      : videoMedia?.storage === 'supabase'
        ? signedVideoUrl
        : videoMedia?.url || null;

    return (
      <Box>
        <Box
          sx={{
            aspectRatio: '16/9',
            bgcolor: 'black',
            borderRadius: 2,
            overflow: 'hidden',
            mb: 3,
            position: 'relative',
          }}
        >
          {isLoadingUrl ? (
            // Loading state
            <Box
              sx={{
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Stack alignItems="center" spacing={2}>
                <CircularProgress />
                <Typography variant="body1" color="text.secondary">
                  Loading video...
                </Typography>
              </Stack>
            </Box>
          ) : urlError ? (
            // Error state
            <Box
              sx={{
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Stack alignItems="center" spacing={2}>
                <VideoLibrary sx={{ fontSize: 60, color: 'error.main' }} />
                <Typography variant="body1" color="error">
                  {urlError}
                </Typography>
              </Stack>
            </Box>
          ) : youtubeId ? (
            // YouTube embed
            <iframe
              width="100%"
              height="100%"
              src={`https://www.youtube.com/embed/${youtubeId}`}
              title={currentLesson?.title}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              style={{ position: 'absolute', top: 0, left: 0 }}
            />
          ) : videoUrl ? (
            // HTML5 video for uploaded files or direct URLs
            <video
              key={videoUrl}
              controls
              width="100%"
              height="100%"
              style={{ position: 'absolute', top: 0, left: 0 }}
            >
              <source src={videoUrl} type="video/mp4" />
              <source src={videoUrl} type="video/webm" />
              Your browser does not support the video tag.
            </video>
          ) : (
            // Placeholder when no video
            <Box
              sx={{
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Stack alignItems="center" spacing={2}>
                <VideoLibrary sx={{ fontSize: 60, color: 'grey.500' }} />
                <Typography variant="body1" color="text.secondary">
                  No video available for this lesson
                </Typography>
              </Stack>
            </Box>
          )}
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
        {currentLesson?.content?.description ? (
          <HtmlContent content={currentLesson.content.description} sx={{ my: 2 }} />
        ) : (
          <Typography variant="body1" paragraph color="text.secondary">
            No description available for this lesson.
          </Typography>
        )}

        <Divider sx={{ my: 3 }} />

        {/* Display uploaded resources */}
        {currentLesson?.content_data?.media_files && currentLesson.content_data.media_files.length > 0 && (
          <>
            <Typography variant="h6" gutterBottom>
              Resources
            </Typography>
            <Stack spacing={1}>
              {currentLesson.content_data.media_files
                .filter((file: any) => file.type !== 'video')
                .map((file: any) => (
                  <Button
                    key={file.id}
                    startIcon={file.type === 'document' ? <Description /> : <Download />}
                    variant="outlined"
                    href={file.url || file.path}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {file.title || file.filename}
                  </Button>
                ))}
            </Stack>
          </>
        )}
      </Paper>
    </Box>
  );
  };

  const QuizContent = () => {
    const handleStartQuiz = () => {
      setQuizStarted(true);
      setQuizAnswers({});
      setQuizSubmitted(false);
    };

    const handleSubmitQuiz = () => {
      setQuizSubmitted(true);
      console.log('Quiz submitted with answers:', quizAnswers);
    };

    const handleAnswerChange = (questionId: string, answer: any) => {
      setQuizAnswers(prev => ({
        ...prev,
        [questionId]: answer
      }));
    };

    // Get quiz questions from the actual lesson content
    // Get quiz questions from lesson's content_data
    const quizQuestions = currentLesson?.content_data?.quiz_questions || [];

    // Also get passing score if available
    const passingScore = currentLesson?.content_data?.passing_score || 70;

    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          {currentLesson?.title}
        </Typography>
        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <Chip
            icon={<Quiz />}
            label="Quiz"
            size="small"
            color="primary"
          />
          <Chip
            icon={<AccessTime />}
            label={`${currentLesson?.duration} min`}
            size="small"
          />
        </Stack>

        <Box sx={{ my: 3 }}>
          {currentLesson?.content?.description ? (
            <HtmlContent content={currentLesson.content.description} sx={{ my: 2 }} />
          ) : (
            <Typography variant="body1" paragraph color="text.secondary">
              Complete this quiz to test your understanding.
            </Typography>
          )}

          <Divider sx={{ my: 3 }} />

          {!quizStarted ? (
            <>
              <Typography variant="h6" gutterBottom>
                Quiz Questions
              </Typography>
              <Box sx={{ bgcolor: 'background.default', p: 3, borderRadius: 2 }}>
                <Typography variant="body1" color="text.secondary" paragraph>
                  {quizQuestions.length > 0
                    ? `This quiz contains ${quizQuestions.length} questions. You have ${currentLesson?.duration} minutes to complete it.`
                    : 'No quiz questions available for this lesson.'}
                </Typography>
                {quizQuestions.length > 0 && (
                  <Button variant="contained" sx={{ mt: 2 }} onClick={handleStartQuiz}>
                    Start Quiz
                  </Button>
                )}
              </Box>
            </>
          ) : (
            <>
              <Typography variant="h6" gutterBottom>
                Quiz Questions
              </Typography>
              <Stack spacing={3}>
                {quizQuestions.map((q: any, index: number) => (
                  <Box key={q.id || index} sx={{ bgcolor: 'background.default', p: 3, borderRadius: 2 }}>
                    <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                      Question {index + 1}: {q.question}
                    </Typography>
                    {q.type === 'multiple_choice' && (
                      <RadioGroup
                        value={quizAnswers[q.id || index] || ''}
                        onChange={(e) => handleAnswerChange(q.id || index.toString(), parseInt(e.target.value))}
                        disabled={quizSubmitted}
                      >
                        {q.options.map((option: string, optIndex: number) => (
                          <FormControlLabel
                            key={optIndex}
                            value={optIndex}
                            control={<Radio />}
                            label={option}
                            sx={{
                              color: quizSubmitted && optIndex === q.correct_answer ? 'success.main' :
                                     quizSubmitted && quizAnswers[q.id || index] === optIndex && optIndex !== q.correct_answer ? 'error.main' :
                                     'inherit'
                            }}
                          />
                        ))}
                      </RadioGroup>
                    )}
                    {q.type === 'true_false' && (
                      <RadioGroup
                        value={quizAnswers[q.id || index] || ''}
                        onChange={(e) => handleAnswerChange(q.id || index.toString(), e.target.value === 'true')}
                        disabled={quizSubmitted}
                      >
                        <FormControlLabel
                          value="true"
                          control={<Radio />}
                          label="True"
                          sx={{
                            color: quizSubmitted && q.correct_answer === true ? 'success.main' :
                                   quizSubmitted && quizAnswers[q.id || index] === true && q.correct_answer !== true ? 'error.main' :
                                   'inherit'
                          }}
                        />
                        <FormControlLabel
                          value="false"
                          control={<Radio />}
                          label="False"
                          sx={{
                            color: quizSubmitted && q.correct_answer === false ? 'success.main' :
                                   quizSubmitted && quizAnswers[q.id || index] === false && q.correct_answer !== false ? 'error.main' :
                                   'inherit'
                          }}
                        />
                      </RadioGroup>
                    )}
                    {quizSubmitted && q.explanation && (
                      <Alert severity="info" sx={{ mt: 2 }}>
                        <Typography variant="body2">{q.explanation}</Typography>
                      </Alert>
                    )}
                  </Box>
                ))}

                {quizQuestions.length > 0 && !quizSubmitted ? (
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleSubmitQuiz}
                    disabled={Object.keys(quizAnswers).length < quizQuestions.length}
                  >
                    Submit Quiz
                  </Button>
                ) : quizSubmitted ? (
                  <Alert severity="success">
                    Quiz submitted! You can review your answers above.
                  </Alert>
                ) : null}
              </Stack>
            </>
          )}
        </Box>
      </Paper>
    );
  };

  const ReadingContent = () => (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        {currentLesson?.title}
      </Typography>
      <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
        <Chip
          icon={<Description />}
          label="Reading"
          size="small"
          color="secondary"
        />
        <Chip
          icon={<AccessTime />}
          label={`${currentLesson?.duration} min`}
          size="small"
        />
      </Stack>

      {currentLesson?.content?.description ? (
        <HtmlContent content={currentLesson.content.description} sx={{ my: 2 }} />
      ) : (
        <Typography variant="body1" paragraph color="text.secondary">
          Reading content will be displayed here.
        </Typography>
      )}

      <Divider sx={{ my: 3 }} />

      <Box sx={{ bgcolor: 'background.default', p: 3, borderRadius: 2 }}>
        <Typography variant="body1">
          {currentLesson?.content?.text || 'Reading material content...'}
        </Typography>
      </Box>
    </Paper>
  );

  const DiscussionContent = () => {
    const [discussionPosts, setDiscussionPosts] = useState<any[]>([]);
    const [newPost, setNewPost] = useState('');
    const [replyingTo, setReplyingTo] = useState<string | null>(null);
    const [replyText, setReplyText] = useState('');

    const handlePostSubmit = () => {
      if (newPost.trim()) {
        const post = {
          id: Date.now().toString(),
          author: currentUser?.name || 'Current User',
          avatar: currentUser?.name?.split(' ').map(n => n[0]).join('') || 'CU',
          timestamp: new Date().toISOString(),
          content: newPost,
          replies: []
        };
        setDiscussionPosts([post, ...discussionPosts]);
        setNewPost('');
      }
    };

    const handleReplySubmit = (postId: string) => {
      if (replyText.trim()) {
        const reply = {
          id: Date.now().toString(),
          author: currentUser?.name || 'Current User',
          avatar: currentUser?.name?.split(' ').map(n => n[0]).join('') || 'CU',
          timestamp: new Date().toISOString(),
          content: replyText
        };

        setDiscussionPosts(discussionPosts.map(post =>
          post.id === postId
            ? { ...post, replies: [...(post.replies || []), reply] }
            : post
        ));
        setReplyText('');
        setReplyingTo(null);
      }
    };

    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          {currentLesson?.title}
        </Typography>
        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <Chip
            icon={<Forum />}
            label="Discussion"
            size="small"
            color="secondary"
          />
          <Chip
            icon={<Group />}
            label={`${discussionPosts.length} posts`}
            size="small"
          />
        </Stack>

        {currentLesson?.content?.description ? (
          <HtmlContent content={currentLesson.content.description} sx={{ my: 2 }} />
        ) : (
          <Typography variant="body1" paragraph color="text.secondary">
            Join the discussion about this lesson topic.
          </Typography>
        )}

        <Divider sx={{ my: 3 }} />

        {/* New Post Input */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Start a Discussion
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            placeholder="Share your thoughts or ask a question..."
            value={newPost}
            onChange={(e) => setNewPost(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button
            variant="contained"
            onClick={handlePostSubmit}
            disabled={!newPost.trim()}
          >
            Post
          </Button>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Discussion Posts */}
        <Typography variant="h6" gutterBottom>
          Discussion Thread
        </Typography>

        {discussionPosts.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No discussions yet. Be the first to start a conversation!
          </Typography>
        ) : (
          <Stack spacing={3}>
            {discussionPosts.map((post) => (
              <Box key={post.id}>
                <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                  <Stack direction="row" spacing={2}>
                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                      {post.avatar}
                    </Avatar>
                    <Box flex={1}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {post.author}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formatDistanceToNow(new Date(post.timestamp), { addSuffix: true })}
                        </Typography>
                      </Stack>
                      <Typography variant="body1" paragraph>
                        {post.content}
                      </Typography>

                      {/* Reply Button */}
                      <Button
                        size="small"
                        onClick={() => setReplyingTo(replyingTo === post.id ? null : post.id)}
                      >
                        Reply
                      </Button>

                      {/* Reply Input */}
                      {replyingTo === post.id && (
                        <Box sx={{ mt: 2 }}>
                          <TextField
                            fullWidth
                            size="small"
                            placeholder="Write a reply..."
                            value={replyText}
                            onChange={(e) => setReplyText(e.target.value)}
                            sx={{ mb: 1 }}
                          />
                          <Stack direction="row" spacing={1}>
                            <Button
                              size="small"
                              variant="contained"
                              onClick={() => handleReplySubmit(post.id)}
                              disabled={!replyText.trim()}
                            >
                              Post Reply
                            </Button>
                            <Button
                              size="small"
                              onClick={() => {
                                setReplyingTo(null);
                                setReplyText('');
                              }}
                            >
                              Cancel
                            </Button>
                          </Stack>
                        </Box>
                      )}

                      {/* Replies */}
                      {post.replies && post.replies.length > 0 && (
                        <Box sx={{ mt: 2, ml: 4 }}>
                          {post.replies.map((reply: any) => (
                            <Box key={reply.id} sx={{ mb: 2 }}>
                              <Stack direction="row" spacing={1}>
                                <Avatar sx={{ width: 28, height: 28, fontSize: 12, bgcolor: 'secondary.main' }}>
                                  {reply.avatar}
                                </Avatar>
                                <Box>
                                  <Typography variant="caption" fontWeight="bold">
                                    {reply.author}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                    {formatDistanceToNow(new Date(reply.timestamp), { addSuffix: true })}
                                  </Typography>
                                  <Typography variant="body2">
                                    {reply.content}
                                  </Typography>
                                </Box>
                              </Stack>
                            </Box>
                          ))}
                        </Box>
                      )}
                    </Box>
                  </Stack>
                </Paper>
              </Box>
            ))}
          </Stack>
        )}
      </Paper>
    );
  };

  const AssignmentContent = () => (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        {currentLesson?.title}
      </Typography>
      <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
        <Chip
          icon={<Assignment />}
          label="Assignment"
          size="small"
          color="warning"
        />
        <Chip
          icon={<AccessTime />}
          label={`${currentLesson?.duration} min`}
          size="small"
        />
      </Stack>

      {currentLesson?.content?.description ? (
        <HtmlContent content={currentLesson.content.description} sx={{ my: 2 }} />
      ) : (
        <Typography variant="body1" paragraph color="text.secondary">
          Complete this assignment to apply what you have learned.
        </Typography>
      )}

      <Divider sx={{ my: 3 }} />

      <Typography variant="h6" gutterBottom>
        Assignment Instructions
      </Typography>

      <Box sx={{ bgcolor: 'background.default', p: 3, borderRadius: 2 }}>
        <Typography variant="body1">
          {currentLesson?.content?.instructions || 'Assignment instructions...'}
        </Typography>
        <Button variant="contained" sx={{ mt: 2 }}>
          Submit Assignment
        </Button>
      </Box>
    </Paper>
  );

  const EmbedContent = () => {
    const embedUrl = currentLesson?.content_data?.embed_url;
    const iframeHeight = currentLesson?.content_data?.iframe_height || 600;
    const allowFullscreen = currentLesson?.content_data?.allow_fullscreen ?? true;

    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          {currentLesson?.title}
        </Typography>
        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <Chip
            icon={<Code />}
            label="Embedded Content"
            size="small"
            color="info"
          />
          <Chip
            icon={<AccessTime />}
            label={`${currentLesson?.duration} min`}
            size="small"
          />
        </Stack>

        {currentLesson?.content?.description && (
          <>
            <HtmlContent content={currentLesson.content.description} sx={{ my: 2 }} />
            <Divider sx={{ my: 3 }} />
          </>
        )}

        {embedUrl ? (
          <Box
            sx={{
              width: '100%',
              height: iframeHeight,
              borderRadius: 2,
              overflow: 'hidden',
              border: '1px solid',
              borderColor: 'divider',
            }}
          >
            <iframe
              src={embedUrl}
              width="100%"
              height="100%"
              frameBorder="0"
              allowFullScreen={allowFullscreen}
              style={{ border: 'none' }}
              title={currentLesson?.title}
            />
          </Box>
        ) : (
          <Alert severity="warning">
            No embed URL configured for this activity.
          </Alert>
        )}
      </Paper>
    );
  };

  // Function to render content based on lesson type
  const renderLessonContent = () => {
    if (!currentLesson) {
      return (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            Select a lesson to begin learning
          </Typography>
        </Paper>
      );
    }

    switch (currentLesson.type) {
      case 'video':
        return <VideoContent />;
      case 'quiz':
        return <QuizContent />;
      case 'reading':
        return <ReadingContent />;
      case 'assignment':
        return <AssignmentContent />;
      case 'code':
        return (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              {currentLesson?.title}
            </Typography>
            <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
              <Chip icon={<Code />} label="Code Exercise" size="small" color="info" />
              <Chip icon={<AccessTime />} label={`${currentLesson?.duration} min`} size="small" />
            </Stack>
            {currentLesson?.content?.description ? (
              <HtmlContent content={currentLesson.content.description} sx={{ my: 2 }} />
            ) : (
              <Typography variant="body1" paragraph color="text.secondary">
                Complete this coding exercise.
              </Typography>
            )}
          </Paper>
        );
      case 'discussion':
      case 'forum':
        return <DiscussionContent />;
      case 'embed':
        return <EmbedContent />;
      default:
        return (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              {currentLesson?.title}
            </Typography>
            <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
              <Chip icon={<Description />} label="Activity" size="small" color="primary" />
              <Chip icon={<AccessTime />} label={`${currentLesson?.duration} min`} size="small" />
            </Stack>
            {currentLesson?.content?.description ? (
              <HtmlContent content={currentLesson.content.description} sx={{ my: 2 }} />
            ) : (
              <Typography variant="body1" paragraph color="text.secondary">
                Activity content will be displayed here.
              </Typography>
            )}

            <Divider sx={{ my: 3 }} />

            {/* Display uploaded resources */}
            {currentLesson?.content_data?.media_files && currentLesson.content_data.media_files.length > 0 && (
              <>
                <Typography variant="h6" gutterBottom>
                  Resources
                </Typography>
                <Stack spacing={1}>
                  {currentLesson.content_data.media_files.map((file: any) => (
                    <Button
                      key={file.id}
                      startIcon={file.type === 'document' ? <Description /> : <Download />}
                      variant="outlined"
                      href={file.url || file.path}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {file.title || file.filename}
                    </Button>
                  ))}
                </Stack>
              </>
            )}
          </Paper>
        );
    }
  };

  const TabContent = () => (
    <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
      <Tab label="Ulrich AI" />
      <Tab label="Q&A" />
      <Tab label="Notes" />
    </Tabs>
  );

  const CourseContent = () => {
    // If a lesson is selected, only show that lesson's module
    if (selectedLesson && currentModule) {
      return (
        <List sx={{ p: 0 }}>
          <Box key={currentModule.id}>
            <ListItemButton
              onClick={() => toggleModule(currentModule.id)}
              sx={{
                bgcolor: 'background.paper',
                '&:hover': { bgcolor: 'action.hover' },
              }}
            >
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle2">{currentModule.title}</Typography>
                    {currentModule.isCompleted && (
                      <CheckCircle color="success" fontSize="small" />
                    )}
                  </Box>
                }
                secondary={
                  <Typography variant="caption" color="text.secondary">
                    {currentModule.lessons.length} lessons • {currentModule.duration} min
                  </Typography>
                }
              />
              {expandedModules.includes(currentModule.id) ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>

            <Collapse in={expandedModules.includes(currentModule.id)}>
              <List disablePadding>
                {currentModule.lessons.map((lesson) => (
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
        </List>
      );
    }

    // Otherwise, show all sections with modules and lessons
    return (
      <List sx={{ p: 0 }}>
        {courseData.sections.map((section) => (
          <Box key={section.id}>
            <ListItemButton
              onClick={() => toggleSection(section.id)}
              sx={{
                bgcolor: 'background.default',
                '&:hover': { bgcolor: 'action.hover' },
                fontWeight: 'bold',
              }}
            >
              <ListItemText
                primary={<Typography variant="subtitle1" fontWeight="bold">{section.title}</Typography>}
                secondary={section.description}
              />
              {expandedSections.includes(section.id) ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>

            <Collapse in={expandedSections.includes(section.id)}>
              <List disablePadding>
                {section.modules.map((module) => (
                  <Box key={module.id}>
                    <ListItemButton
                      onClick={() => toggleModule(module.id)}
                      sx={{
                        pl: 2,
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
                              pl: 6,
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
            </Collapse>
            <Divider />
          </Box>
        ))}
      </List>
    );
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: 'background.default' }}>
      {/* Version Preview Banner - only shown when previewing a specific version */}
      {versionId && (isAdmin || isInstructor) && (
        <Paper
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            zIndex: 1300,
            bgcolor: 'warning.main',
            color: 'warning.contrastText',
            p: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 2,
          }}
        >
          <Visibility />
          <Typography variant="body1" fontWeight="bold">
            Preview Mode: Viewing Version {versionId}
          </Typography>
          <Button
            variant="contained"
            size="small"
            sx={{ bgcolor: 'white', color: 'warning.main' }}
            onClick={() => navigate(-1)}
          >
            Exit Preview
          </Button>
        </Paper>
      )}

      {/* Header */}
      <AppBar position="fixed" elevation={1} sx={{ top: versionId && (isAdmin || isInstructor) ? 48 : 0 }}>
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
            top: versionId && (isAdmin || isInstructor) ? 112 : 64, // Adjust for preview banner
            height: versionId && (isAdmin || isInstructor) ? 'calc(100% - 112px)' : 'calc(100% - 64px)',
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
          mt: versionId && (isAdmin || isInstructor) ? 14 : 8, // Adjust for preview banner
          ml: sidebarOpen ? 0 : 0,
          transition: 'margin-left 0.3s',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={3}>
            <Grid item xs={12}>
              {renderLessonContent()}

              <Box sx={{ mt: 3 }}>
                <TabContent />

                {tabValue === 0 && (
                  <Paper sx={{ p: 0, height: '650px', overflow: 'hidden' }}>
                    <LessonChat
                      courseTitle={courseData.title}
                      lessonTitle={currentLesson?.title || 'Select a lesson'}
                      lessonType={currentLesson?.type}
                      moduleTitle={courseData.sections.flatMap(s => s.modules).find(m =>
                        m.lessons.some(l => l.id === selectedLesson)
                      )?.title}
                      learningObjectives={[]}
                      currentContent={currentLesson?.content?.description || `Select a lesson to begin learning.`}
                      courseId={courseData.id}
                      lessonId={selectedLesson}
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