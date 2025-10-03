import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Stack,
  Alert,
  CircularProgress,
  IconButton,
} from '@mui/material';
import {
  Quiz as QuizIcon,
  Edit as EditIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import QuizBuilder from './QuizBuilder';
import QuizTaker from './QuizTaker';
import { useGetQuizByContentItemQuery } from '../../../store/api/quizApi';
import { useAppSelector } from '../../../store/hooks';

interface LessonQuizProps {
  contentItemId: string;
  lessonId: string;
  courseId: string;
  lessonTitle: string;
  isInstructor?: boolean;
}

const LessonQuiz: React.FC<LessonQuizProps> = ({
  contentItemId,
  lessonId,
  courseId,
  lessonTitle,
  isInstructor = false,
}) => {
  const [showBuilder, setShowBuilder] = useState(false);
  const user = useAppSelector((state) => state.auth.user);

  // Fetch quiz for this content item
  const { data: quiz, isLoading, refetch } = useGetQuizByContentItemQuery(contentItemId, {
    skip: !contentItemId,
  });

  const handleQuizSaved = (newQuizId: string) => {
    setShowBuilder(false);
    refetch();
  };

  const handleBuilderClose = () => {
    setShowBuilder(false);
  };

  // Show loading state
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  // Instructor view
  if (isInstructor || user?.role === 'INSTRUCTOR') {
    if (showBuilder) {
      return (
        <QuizBuilder
          contentItemId={contentItemId}
          quizId={quiz?.id}
          onClose={handleBuilderClose}
          onSave={handleQuizSaved}
        />
      );
    }

    return (
      <Paper sx={{ p: 3 }}>
        <Stack spacing={3}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h5">
              <QuizIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Quiz Management
            </Typography>
            {quiz ? (
              <Button
                variant="contained"
                startIcon={<EditIcon />}
                onClick={() => setShowBuilder(true)}
              >
                Edit Quiz
              </Button>
            ) : (
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowBuilder(true)}
                color="primary"
              >
                Create Quiz
              </Button>
            )}
          </Stack>

          {quiz ? (
            <Box>
              <Alert severity="success" sx={{ mb: 2 }}>
                Quiz is configured and ready for students!
              </Alert>
              <Stack spacing={1}>
                <Typography variant="h6">{quiz.title}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {quiz.instructions}
                </Typography>
                <Stack direction="row" spacing={2}>
                  <Typography variant="body2">
                    <strong>Questions:</strong> {quiz.question_count}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Total Points:</strong> {quiz.total_points}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Time Limit:</strong> {quiz.time_limit_minutes ? `${quiz.time_limit_minutes} minutes` : 'No limit'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Passing Score:</strong> {quiz.passing_score}%
                  </Typography>
                </Stack>
              </Stack>

              <Box sx={{ mt: 3 }}>
                <Button
                  variant="outlined"
                  onClick={() => {
                    // Preview quiz as student
                    window.open(`/quiz-preview/${quiz.id}`, '_blank');
                  }}
                >
                  Preview as Student
                </Button>
              </Box>
            </Box>
          ) : (
            <Alert severity="info">
              No quiz has been created for this lesson yet. Click "Create Quiz" to get started.
            </Alert>
          )}
        </Stack>
      </Paper>
    );
  }

  // Student view
  if (!quiz) {
    return (
      <Paper sx={{ p: 3 }}>
        <Alert severity="info">
          No quiz is available for this lesson yet. Please check back later.
        </Alert>
      </Paper>
    );
  }

  return <QuizTaker quizId={quiz.id} />;
};

export default LessonQuiz;