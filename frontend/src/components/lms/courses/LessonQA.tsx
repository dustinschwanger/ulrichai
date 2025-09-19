import React, { useState, useEffect } from 'react';
import {
  Box,
  Stack,
  Paper,
  Typography,
  Button,
  TextField,
  IconButton,
  Card,
  CardContent,
  Avatar,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
} from '@mui/material';
import {
  QuestionAnswer,
  ThumbUp,
  ThumbDown,
  Reply,
  Close,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { config } from '../../../config';
import toast from 'react-hot-toast';

interface Question {
  id: string;
  lessonId: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  question: string;
  details?: string;
  timestamp: Date;
  upvotes: number;
  hasUpvoted: boolean;
  answers: Answer[];
}

interface Answer {
  id: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  answer: string;
  timestamp: Date;
  upvotes: number;
  hasUpvoted: boolean;
  isInstructor?: boolean;
}

interface LessonQAProps {
  lessonId: string;
  lessonTitle: string;
  courseId: string;
}

const LessonQA: React.FC<LessonQAProps> = ({ lessonId, lessonTitle, courseId }) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [newQuestion, setNewQuestion] = useState('');
  const [questionDetails, setQuestionDetails] = useState('');
  const [isAskingQuestion, setIsAskingQuestion] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [newAnswer, setNewAnswer] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock current user
  const currentUser = {
    id: 'user123',
    name: 'Current User',
    avatar: 'CU',
  };

  // Load questions for this lesson
  useEffect(() => {
    fetchQuestions();
  }, [lessonId]);

  const fetchQuestions = async () => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/lessons/${lessonId}/questions`);
      if (response.ok) {
        const data = await response.json();
        // Convert timestamp strings to Date objects
        const questions = data.map((q: any) => ({
          ...q,
          timestamp: new Date(q.timestamp),
          answers: q.answers.map((a: any) => ({
            ...a,
            timestamp: new Date(a.timestamp)
          }))
        }));
        setQuestions(questions);
      }
    } catch (error) {
      console.error('Error fetching questions:', error);
      toast.error('Failed to load questions');
    }
  };

  const handleAskQuestion = async () => {
    if (!newQuestion.trim()) return;

    try {
      const response = await fetch(`${config.API_BASE_URL}/lessons/${lessonId}/questions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lessonId,
          courseId,
          question: newQuestion,
          details: questionDetails || null,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const question = {
          ...data,
          timestamp: new Date(data.timestamp)
        };
        setQuestions([question, ...questions]);
        setNewQuestion('');
        setQuestionDetails('');
        setIsAskingQuestion(false);
        toast.success('Question posted successfully');
      }
    } catch (error) {
      console.error('Error posting question:', error);
      toast.error('Failed to post question');
    }
  };

  const handleAnswerQuestion = async () => {
    if (!selectedQuestion || !newAnswer.trim()) return;

    try {
      const response = await fetch(`${config.API_BASE_URL}/questions/${selectedQuestion.id}/answers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          questionId: selectedQuestion.id,
          answer: newAnswer,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const answer = {
          ...data,
          timestamp: new Date(data.timestamp)
        };

        setQuestions(questions.map(q =>
          q.id === selectedQuestion.id
            ? { ...q, answers: [...q.answers, answer] }
            : q
        ));

        setNewAnswer('');
        setSelectedQuestion(null);
        toast.success('Answer posted successfully');
      }
    } catch (error) {
      console.error('Error posting answer:', error);
      toast.error('Failed to post answer');
    }
  };

  const handleUpvoteQuestion = async (questionId: string) => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/questions/${questionId}/upvote`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        setQuestions(questions.map(q =>
          q.id === questionId
            ? {
                ...q,
                upvotes: data.upvotes,
                hasUpvoted: data.action === 'added',
              }
            : q
        ));
      }
    } catch (error) {
      console.error('Error upvoting question:', error);
      toast.error('Failed to upvote question');
    }
  };

  const handleUpvoteAnswer = async (questionId: string, answerId: string) => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/answers/${answerId}/upvote`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        setQuestions(questions.map(q =>
          q.id === questionId
            ? {
                ...q,
                answers: q.answers.map(a =>
                  a.id === answerId
                    ? {
                        ...a,
                        upvotes: data.upvotes,
                        hasUpvoted: data.action === 'added',
                      }
                    : a
                ),
              }
            : q
        ));
      }
    } catch (error) {
      console.error('Error upvoting answer:', error);
      toast.error('Failed to upvote answer');
    }
  };

  const filteredQuestions = questions.filter(q =>
    q.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (q.details && q.details.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <Box>
      {/* Header with Ask Question button */}
      <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search questions..."
          size="small"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <Button
          variant="contained"
          startIcon={<QuestionAnswer />}
          onClick={() => setIsAskingQuestion(true)}
        >
          Ask Question
        </Button>
      </Stack>

      {/* Questions List */}
      <Stack spacing={2}>
        {filteredQuestions.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <QuestionAnswer sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No questions yet
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Be the first to ask a question about this lesson!
            </Typography>
          </Paper>
        ) : (
          filteredQuestions.map((question) => (
            <Card key={question.id} variant="outlined">
              <CardContent>
                {/* Question Header */}
                <Stack direction="row" spacing={2} alignItems="flex-start">
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    {question.userAvatar}
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                      <Typography variant="subtitle2">
                        {question.userName}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        • {formatDistanceToNow(question.timestamp, { addSuffix: true })}
                      </Typography>
                    </Stack>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                      {question.question}
                    </Typography>
                    {question.details && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {question.details}
                      </Typography>
                    )}

                    {/* Question Actions */}
                    <Stack direction="row" spacing={2} alignItems="center">
                      <Button
                        size="small"
                        startIcon={
                          <ThumbUp
                            fontSize="small"
                            color={question.hasUpvoted ? 'primary' : 'inherit'}
                          />
                        }
                        onClick={() => handleUpvoteQuestion(question.id)}
                      >
                        {question.upvotes}
                      </Button>
                      <Button
                        size="small"
                        startIcon={<Reply />}
                        onClick={() => setSelectedQuestion(question)}
                      >
                        Answer ({question.answers.length})
                      </Button>
                    </Stack>

                    {/* Answers */}
                    {question.answers.length > 0 && (
                      <Box sx={{ mt: 3, pl: 2, borderLeft: '2px solid', borderColor: 'divider' }}>
                        <Stack spacing={2}>
                          {question.answers.map((answer) => (
                            <Box key={answer.id}>
                              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                                <Avatar sx={{ width: 24, height: 24, fontSize: 12 }}>
                                  {answer.userAvatar}
                                </Avatar>
                                <Typography variant="subtitle2">
                                  {answer.userName}
                                </Typography>
                                {answer.isInstructor && (
                                  <Chip label="Instructor" size="small" color="primary" />
                                )}
                                <Typography variant="caption" color="text.secondary">
                                  • {formatDistanceToNow(answer.timestamp, { addSuffix: true })}
                                </Typography>
                              </Stack>
                              <Typography variant="body2" sx={{ mb: 1 }}>
                                {answer.answer}
                              </Typography>
                              <Button
                                size="small"
                                startIcon={
                                  <ThumbUp
                                    fontSize="small"
                                    color={answer.hasUpvoted ? 'primary' : 'inherit'}
                                  />
                                }
                                onClick={() => handleUpvoteAnswer(question.id, answer.id)}
                              >
                                {answer.upvotes}
                              </Button>
                            </Box>
                          ))}
                        </Stack>
                      </Box>
                    )}
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          ))
        )}
      </Stack>

      {/* Ask Question Dialog */}
      <Dialog
        open={isAskingQuestion}
        onClose={() => setIsAskingQuestion(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Ask a Question
          <IconButton
            sx={{ position: 'absolute', right: 8, top: 8 }}
            onClick={() => setIsAskingQuestion(false)}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              fullWidth
              label="Question"
              placeholder="What would you like to know?"
              value={newQuestion}
              onChange={(e) => setNewQuestion(e.target.value)}
              required
            />
            <TextField
              fullWidth
              label="Additional Details (optional)"
              placeholder="Add any context or specifics that might help get better answers"
              multiline
              rows={4}
              value={questionDetails}
              onChange={(e) => setQuestionDetails(e.target.value)}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsAskingQuestion(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleAskQuestion} disabled={!newQuestion.trim()}>
            Post Question
          </Button>
        </DialogActions>
      </Dialog>

      {/* Answer Question Dialog */}
      <Dialog
        open={!!selectedQuestion}
        onClose={() => setSelectedQuestion(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Answer Question
          <IconButton
            sx={{ position: 'absolute', right: 8, top: 8 }}
            onClick={() => setSelectedQuestion(null)}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {selectedQuestion && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {selectedQuestion.question}
                </Typography>
                {selectedQuestion.details && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {selectedQuestion.details}
                  </Typography>
                )}
              </Box>
              <Divider />
              <TextField
                fullWidth
                label="Your Answer"
                placeholder="Share your knowledge..."
                multiline
                rows={6}
                value={newAnswer}
                onChange={(e) => setNewAnswer(e.target.value)}
              />
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedQuestion(null)}>Cancel</Button>
          <Button variant="contained" onClick={handleAnswerQuestion} disabled={!newAnswer.trim()}>
            Post Answer
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LessonQA;