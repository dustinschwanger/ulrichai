import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  RadioGroup,
  Radio,
  FormControlLabel,
  Checkbox,
  TextField,
  Card,
  CardContent,
  Stack,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  IconButton,
  CircularProgress,
} from '@mui/material';
import {
  Timer as TimerIcon,
  CheckCircle,
  Cancel,
  NavigateBefore,
  NavigateNext,
  Send,
  Refresh,
  Visibility,
} from '@mui/icons-material';
import {
  useGetQuizQuery,
  useGetQuizQuestionsQuery,
  useStartQuizAttemptMutation,
  useSubmitQuizAttemptMutation,
  useGetUserQuizAttemptsQuery,
  useGetQuizReviewQuery,
} from '../../../store/api/quizApi';
import type { QuizQuestion, QuizResponse, QuizAttempt } from '../../../store/api/quizApi';
import toast from 'react-hot-toast';

interface QuizTakerProps {
  quizId: string;
  onClose?: () => void;
}

const QuizTaker: React.FC<QuizTakerProps> = ({ quizId, onClose }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<Record<string, string[]>>({});
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [showReview, setShowReview] = useState(false);
  const [selectedAttemptId, setSelectedAttemptId] = useState<string | null>(null);
  const [confirmSubmitOpen, setConfirmSubmitOpen] = useState(false);

  // API hooks
  const { data: quiz, isLoading: isLoadingQuiz } = useGetQuizQuery(quizId);
  const { data: questions, isLoading: isLoadingQuestions } = useGetQuizQuestionsQuery(quizId, {
    skip: !attemptId,
  });
  const { data: userAttempts, refetch: refetchAttempts } = useGetUserQuizAttemptsQuery(quizId);
  const [startAttempt] = useStartQuizAttemptMutation();
  const [submitAttempt] = useSubmitQuizAttemptMutation();
  const { data: reviewData } = useGetQuizReviewQuery(selectedAttemptId || '', {
    skip: !selectedAttemptId,
  });

  // Timer effect
  useEffect(() => {
    if (!attemptId || !timeRemaining || timeRemaining <= 0) return;

    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev && prev <= 1) {
          handleSubmitQuiz(true); // Auto-submit when time runs out
          return 0;
        }
        return prev ? prev - 1 : null;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [attemptId, timeRemaining]);

  const handleStartQuiz = async () => {
    try {
      const result = await startAttempt({ quiz_id: quizId }).unwrap();
      setAttemptId(result.id);
      if (quiz?.time_limit_minutes) {
        setTimeRemaining(quiz.time_limit_minutes * 60);
      }
      toast.success('Quiz started! Good luck!');
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Failed to start quiz');
    }
  };

  const handleAnswerChange = (questionId: string, answer: string | string[], isMultiple: boolean = false) => {
    if (isMultiple) {
      setResponses({
        ...responses,
        [questionId]: Array.isArray(answer) ? answer : [answer],
      });
    } else {
      setResponses({
        ...responses,
        [questionId]: [answer as string],
      });
    }
  };

  const handleSubmitQuiz = async (autoSubmit: boolean = false) => {
    if (!autoSubmit && !confirmSubmitOpen) {
      setConfirmSubmitOpen(true);
      return;
    }

    setIsSubmitting(true);
    setConfirmSubmitOpen(false);

    try {
      if (!attemptId || !questions) {
        toast.error('Invalid quiz state');
        return;
      }

      const quizResponses: QuizResponse[] = questions.map((q) => ({
        question_id: q.id || '',
        answer: responses[q.id || ''] || [],
      }));

      const result = await submitAttempt({
        attempt_id: attemptId,
        responses: quizResponses,
      }).unwrap();

      setShowResults(true);
      refetchAttempts();

      if (autoSubmit) {
        toast.info('Time is up! Quiz has been automatically submitted.');
      } else {
        toast.success('Quiz submitted successfully!');
      }
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Failed to submit quiz');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const calculateProgress = (): number => {
    if (!questions) return 0;
    const answeredCount = Object.keys(responses).filter((key) => responses[key].length > 0).length;
    return (answeredCount / questions.length) * 100;
  };

  const handleViewReview = (attemptId: string) => {
    setSelectedAttemptId(attemptId);
    setShowReview(true);
  };

  // Render loading state
  if (isLoadingQuiz) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!quiz) {
    return <Alert severity="error">Quiz not found</Alert>;
  }

  // Show attempts history if not taking quiz
  if (!attemptId && !showReview) {
    const canStartNewAttempt = !quiz.attempts_allowed ||
      !userAttempts ||
      userAttempts.length < quiz.attempts_allowed;

    return (
      <Paper sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
        <Typography variant="h4" gutterBottom>
          {quiz.title}
        </Typography>
        <Typography variant="body1" paragraph>
          {quiz.instructions}
        </Typography>

        <Stack spacing={2} sx={{ mb: 3 }}>
          <Box>
            <Chip
              icon={<TimerIcon />}
              label={quiz.time_limit_minutes ? `${quiz.time_limit_minutes} minutes` : 'No time limit'}
            />
            <Chip
              label={`${quiz.question_count} questions`}
              sx={{ ml: 1 }}
            />
            <Chip
              label={`${quiz.total_points} points`}
              sx={{ ml: 1 }}
            />
          </Box>
          <Typography variant="body2">
            Passing score: {quiz.passing_score}%
          </Typography>
          <Typography variant="body2">
            Attempts allowed: {quiz.attempts_allowed || 'Unlimited'}
          </Typography>
        </Stack>

        {userAttempts && userAttempts.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Previous Attempts
            </Typography>
            {userAttempts.map((attempt, index) => (
              <Card key={attempt.id} sx={{ mb: 1 }}>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Box>
                      <Typography variant="subtitle1">
                        Attempt {attempt.attempt_number}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Score: {attempt.score?.toFixed(1)}%
                        {attempt.passed ? ' (Passed)' : ' (Failed)'}
                      </Typography>
                    </Box>
                    <Stack direction="row" spacing={1}>
                      {quiz.allow_review && attempt.status === 'graded' && (
                        <Button
                          size="small"
                          startIcon={<Visibility />}
                          onClick={() => handleViewReview(attempt.id)}
                        >
                          Review
                        </Button>
                      )}
                      {attempt.passed ? (
                        <CheckCircle color="success" />
                      ) : (
                        <Cancel color="error" />
                      )}
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}

        <Stack direction="row" spacing={2}>
          {canStartNewAttempt ? (
            <Button
              variant="contained"
              size="large"
              onClick={handleStartQuiz}
              startIcon={<Send />}
            >
              Start Quiz
            </Button>
          ) : (
            <Alert severity="warning">
              You have used all available attempts for this quiz.
            </Alert>
          )}
          {onClose && (
            <Button variant="outlined" onClick={onClose}>
              Cancel
            </Button>
          )}
        </Stack>
      </Paper>
    );
  }

  // Show review
  if (showReview && reviewData) {
    return (
      <Paper sx={{ p: 4, maxWidth: 900, mx: 'auto' }}>
        <Typography variant="h4" gutterBottom>
          Quiz Review: {reviewData.quiz_title}
        </Typography>

        <Alert severity={reviewData.attempt.passed ? 'success' : 'error'} sx={{ mb: 3 }}>
          Score: {reviewData.attempt.score?.toFixed(1)}%
          ({reviewData.attempt.points_earned}/{reviewData.attempt.points_possible} points)
          - {reviewData.attempt.passed ? 'PASSED' : 'FAILED'}
        </Alert>

        {reviewData.questions.map((item, index) => {
          const question = item.question;
          const isCorrect = item.is_correct;

          return (
            <Card key={question.id} sx={{ mb: 2 }}>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">
                    Question {index + 1}: {question.question_text}
                  </Typography>

                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Your Answer: {item.user_response.join(', ')}
                    </Typography>

                    {quiz.show_correct_answers && question.correct_answers && (
                      <Typography variant="subtitle2" color="success.main">
                        Correct Answer: {question.correct_answers.join(', ')}
                      </Typography>
                    )}
                  </Box>

                  <Stack direction="row" alignItems="center" spacing={1}>
                    {isCorrect ? (
                      <CheckCircle color="success" />
                    ) : (
                      <Cancel color="error" />
                    )}
                    <Typography>
                      {item.points_earned}/{question.points} points
                    </Typography>
                  </Stack>

                  {quiz.show_feedback && item.explanation && (
                    <Alert severity="info">
                      <Typography variant="body2">{item.explanation}</Typography>
                    </Alert>
                  )}
                </Stack>
              </CardContent>
            </Card>
          );
        })}

        <Button
          variant="contained"
          onClick={() => setShowReview(false)}
        >
          Back to Quiz
        </Button>
      </Paper>
    );
  }

  // Show results
  if (showResults && userAttempts) {
    const latestAttempt = userAttempts[userAttempts.length - 1];

    return (
      <Paper sx={{ p: 4, maxWidth: 600, mx: 'auto', textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom>
          Quiz Completed!
        </Typography>

        {latestAttempt && (
          <>
            <Typography variant="h2" color={latestAttempt.passed ? 'success.main' : 'error.main'} sx={{ my: 3 }}>
              {latestAttempt.score?.toFixed(1)}%
            </Typography>

            <Typography variant="h6" gutterBottom>
              {latestAttempt.passed ? 'Congratulations! You passed!' : 'Sorry, you did not pass.'}
            </Typography>

            <Typography variant="body1" paragraph>
              Points: {latestAttempt.points_earned}/{latestAttempt.points_possible}
            </Typography>

            <Stack direction="row" spacing={2} justifyContent="center" sx={{ mt: 3 }}>
              {quiz.allow_review && (
                <Button
                  variant="contained"
                  startIcon={<Visibility />}
                  onClick={() => handleViewReview(latestAttempt.id)}
                >
                  Review Answers
                </Button>
              )}
              {onClose && (
                <Button variant="outlined" onClick={onClose}>
                  Close
                </Button>
              )}
            </Stack>
          </>
        )}
      </Paper>
    );
  }

  // Quiz taking interface
  if (!questions || isLoadingQuestions) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const currentResponse = responses[currentQuestion.id || ''] || [];

  return (
    <Box sx={{ maxWidth: 900, mx: 'auto', p: 2 }}>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h5">{quiz.title}</Typography>
          {timeRemaining !== null && (
            <Chip
              icon={<TimerIcon />}
              label={formatTime(timeRemaining)}
              color={timeRemaining < 60 ? 'error' : timeRemaining < 300 ? 'warning' : 'default'}
            />
          )}
        </Stack>
        <LinearProgress variant="determinate" value={calculateProgress()} sx={{ mt: 2 }} />
        <Typography variant="body2" sx={{ mt: 1 }}>
          Question {currentQuestionIndex + 1} of {questions.length}
        </Typography>
      </Paper>

      {/* Question */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {currentQuestion.question_text}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {currentQuestion.points} point{currentQuestion.points !== 1 ? 's' : ''}
          </Typography>

          <Box sx={{ mt: 3 }}>
            {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options && (
              <RadioGroup
                value={currentResponse[0] || ''}
                onChange={(e) => handleAnswerChange(currentQuestion.id || '', e.target.value)}
              >
                {currentQuestion.options.map((option) => (
                  <FormControlLabel
                    key={option.id}
                    value={option.id}
                    control={<Radio />}
                    label={option.text}
                  />
                ))}
              </RadioGroup>
            )}

            {currentQuestion.question_type === 'true_false' && currentQuestion.options && (
              <RadioGroup
                value={currentResponse[0] || ''}
                onChange={(e) => handleAnswerChange(currentQuestion.id || '', e.target.value)}
              >
                {currentQuestion.options.map((option) => (
                  <FormControlLabel
                    key={option.id}
                    value={option.id}
                    control={<Radio />}
                    label={option.text}
                  />
                ))}
              </RadioGroup>
            )}

            {currentQuestion.question_type === 'short_answer' && (
              <TextField
                fullWidth
                multiline
                rows={2}
                value={currentResponse[0] || ''}
                onChange={(e) => handleAnswerChange(currentQuestion.id || '', e.target.value)}
                placeholder="Enter your answer..."
              />
            )}

            {currentQuestion.question_type === 'essay' && (
              <TextField
                fullWidth
                multiline
                rows={6}
                value={currentResponse[0] || ''}
                onChange={(e) => handleAnswerChange(currentQuestion.id || '', e.target.value)}
                placeholder="Write your essay answer..."
              />
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Navigation */}
      <Paper sx={{ p: 2 }}>
        <Stack direction="row" justifyContent="space-between">
          <Button
            startIcon={<NavigateBefore />}
            onClick={() => setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))}
            disabled={currentQuestionIndex === 0}
          >
            Previous
          </Button>

          <Stack direction="row" spacing={1}>
            {questions.map((_, index) => (
              <IconButton
                key={index}
                size="small"
                onClick={() => setCurrentQuestionIndex(index)}
                color={responses[questions[index].id || '']?.length > 0 ? 'primary' : 'default'}
                sx={{
                  backgroundColor: index === currentQuestionIndex ? 'action.selected' : undefined,
                }}
              >
                {index + 1}
              </IconButton>
            ))}
          </Stack>

          {currentQuestionIndex < questions.length - 1 ? (
            <Button
              endIcon={<NavigateNext />}
              onClick={() => setCurrentQuestionIndex((prev) => Math.min(questions.length - 1, prev + 1))}
            >
              Next
            </Button>
          ) : (
            <Button
              variant="contained"
              color="primary"
              endIcon={<Send />}
              onClick={() => handleSubmitQuiz(false)}
              disabled={isSubmitting}
            >
              Submit Quiz
            </Button>
          )}
        </Stack>
      </Paper>

      {/* Confirm Submit Dialog */}
      <Dialog open={confirmSubmitOpen} onClose={() => setConfirmSubmitOpen(false)}>
        <DialogTitle>Submit Quiz?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to submit your quiz? You have answered{' '}
            {Object.keys(responses).filter((key) => responses[key].length > 0).length} out of{' '}
            {questions.length} questions.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmSubmitOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => handleSubmitQuiz(false)}
            disabled={isSubmitting}
          >
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default QuizTaker;