import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  FormControl,
  FormControlLabel,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  RadioGroup,
  Radio,
  Checkbox,
  Stack,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
  FormLabel,
  FormGroup,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  DragIndicator as DragIcon,
  ArrowBack,
  ArrowForward,
} from '@mui/icons-material';
import { useCreateQuizMutation, useUpdateQuizMutation, useGetQuizQuery } from '../../../store/api/quizApi';
import type { QuizCreate, QuizQuestion, QuizOption } from '../../../store/api/quizApi';
import toast from 'react-hot-toast';

interface QuizBuilderProps {
  contentItemId: string;
  quizId?: string;
  onClose: () => void;
  onSave: (quizId: string) => void;
}

const QuizBuilder: React.FC<QuizBuilderProps> = ({ contentItemId, quizId, onClose, onSave }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [quiz, setQuiz] = useState<QuizCreate>({
    content_item_id: contentItemId,
    title: '',
    instructions: '',
    time_limit_minutes: 60,
    attempts_allowed: 1,
    passing_score: 70,
    shuffle_questions: false,
    shuffle_answers: false,
    show_correct_answers: true,
    show_feedback: true,
    allow_review: true,
    questions: [],
  });

  const [editingQuestionIndex, setEditingQuestionIndex] = useState<number | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<QuizQuestion>({
    question_type: 'multiple_choice',
    question_text: '',
    options: [
      { id: 'a', text: '' },
      { id: 'b', text: '' },
      { id: 'c', text: '' },
      { id: 'd', text: '' },
    ],
    correct_answers: [],
    explanation: '',
    points: 1,
    sequence_order: 1,
    difficulty_level: 1,
  });

  const [createQuiz, { isLoading: isCreating }] = useCreateQuizMutation();
  const [updateQuiz, { isLoading: isUpdating }] = useUpdateQuizMutation();
  const { data: existingQuiz, isLoading: isLoadingQuiz } = useGetQuizQuery(quizId || '', {
    skip: !quizId,
  });

  useEffect(() => {
    if (existingQuiz && quizId) {
      setQuiz({
        ...existingQuiz,
        content_item_id: contentItemId,
        questions: [], // Questions will be loaded separately
      });
    }
  }, [existingQuiz, quizId, contentItemId]);

  const steps = ['Quiz Settings', 'Add Questions', 'Review & Save'];

  const handleNext = () => {
    if (activeStep === 0) {
      // Validate settings
      if (!quiz.title || !quiz.instructions) {
        toast.error('Please fill in all required fields');
        return;
      }
    } else if (activeStep === 1) {
      // Validate questions
      if (quiz.questions.length === 0) {
        toast.error('Please add at least one question');
        return;
      }
    }
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleAddQuestion = () => {
    if (!currentQuestion.question_text) {
      toast.error('Please enter a question');
      return;
    }

    if (currentQuestion.question_type === 'multiple_choice' || currentQuestion.question_type === 'true_false') {
      if (currentQuestion.correct_answers?.length === 0) {
        toast.error('Please select at least one correct answer');
        return;
      }
    } else if (currentQuestion.question_type === 'short_answer') {
      if (!currentQuestion.correct_answers || currentQuestion.correct_answers.length === 0) {
        toast.error('Please provide at least one correct answer');
        return;
      }
    }

    const newQuestion = {
      ...currentQuestion,
      sequence_order: editingQuestionIndex !== null ? currentQuestion.sequence_order : quiz.questions.length + 1,
    };

    if (editingQuestionIndex !== null) {
      // Update existing question
      const updatedQuestions = [...quiz.questions];
      updatedQuestions[editingQuestionIndex] = newQuestion;
      setQuiz({ ...quiz, questions: updatedQuestions });
      setEditingQuestionIndex(null);
    } else {
      // Add new question
      setQuiz({ ...quiz, questions: [...quiz.questions, newQuestion] });
    }

    // Reset current question
    setCurrentQuestion({
      question_type: 'multiple_choice',
      question_text: '',
      options: [
        { id: 'a', text: '' },
        { id: 'b', text: '' },
        { id: 'c', text: '' },
        { id: 'd', text: '' },
      ],
      correct_answers: [],
      explanation: '',
      points: 1,
      sequence_order: quiz.questions.length + 2,
      difficulty_level: 1,
    });
  };

  const handleEditQuestion = (index: number) => {
    setEditingQuestionIndex(index);
    setCurrentQuestion(quiz.questions[index]);
  };

  const handleDeleteQuestion = (index: number) => {
    const updatedQuestions = quiz.questions.filter((_, i) => i !== index);
    // Update sequence orders
    updatedQuestions.forEach((q, i) => {
      q.sequence_order = i + 1;
    });
    setQuiz({ ...quiz, questions: updatedQuestions });
  };

  const handleSaveQuiz = async () => {
    try {
      let result;
      if (quizId) {
        result = await updateQuiz({ quizId, data: quiz }).unwrap();
      } else {
        result = await createQuiz(quiz).unwrap();
      }
      toast.success(`Quiz ${quizId ? 'updated' : 'created'} successfully!`);
      onSave(result.id);
    } catch (error) {
      toast.error(`Failed to ${quizId ? 'update' : 'create'} quiz`);
      console.error('Error saving quiz:', error);
    }
  };

  const handleQuestionTypeChange = (type: QuizQuestion['question_type']) => {
    if (type === 'true_false') {
      setCurrentQuestion({
        ...currentQuestion,
        question_type: type,
        options: [
          { id: 'true', text: 'True' },
          { id: 'false', text: 'False' },
        ],
        correct_answers: [],
      });
    } else if (type === 'multiple_choice') {
      setCurrentQuestion({
        ...currentQuestion,
        question_type: type,
        options: [
          { id: 'a', text: '' },
          { id: 'b', text: '' },
          { id: 'c', text: '' },
          { id: 'd', text: '' },
        ],
        correct_answers: [],
      });
    } else {
      setCurrentQuestion({
        ...currentQuestion,
        question_type: type,
        options: undefined,
        correct_answers: [],
      });
    }
  };

  const renderSettingsStep = () => (
    <Stack spacing={3}>
      <TextField
        fullWidth
        label="Quiz Title"
        value={quiz.title}
        onChange={(e) => setQuiz({ ...quiz, title: e.target.value })}
        required
      />
      <TextField
        fullWidth
        multiline
        rows={3}
        label="Instructions"
        value={quiz.instructions}
        onChange={(e) => setQuiz({ ...quiz, instructions: e.target.value })}
        required
      />
      <Stack direction="row" spacing={2}>
        <TextField
          type="number"
          label="Time Limit (minutes)"
          value={quiz.time_limit_minutes}
          onChange={(e) => setQuiz({ ...quiz, time_limit_minutes: parseInt(e.target.value) || undefined })}
          InputProps={{ inputProps: { min: 0 } }}
        />
        <TextField
          type="number"
          label="Attempts Allowed"
          value={quiz.attempts_allowed}
          onChange={(e) => setQuiz({ ...quiz, attempts_allowed: parseInt(e.target.value) || undefined })}
          InputProps={{ inputProps: { min: 1 } }}
        />
      </Stack>
      <Box>
        <Typography gutterBottom>Passing Score: {quiz.passing_score}%</Typography>
        <Slider
          value={quiz.passing_score}
          onChange={(_, value) => setQuiz({ ...quiz, passing_score: value as number })}
          min={0}
          max={100}
          step={5}
          marks
          valueLabelDisplay="auto"
        />
      </Box>
      <FormGroup>
        <FormControlLabel
          control={
            <Switch
              checked={quiz.shuffle_questions}
              onChange={(e) => setQuiz({ ...quiz, shuffle_questions: e.target.checked })}
            />
          }
          label="Shuffle Questions"
        />
        <FormControlLabel
          control={
            <Switch
              checked={quiz.shuffle_answers}
              onChange={(e) => setQuiz({ ...quiz, shuffle_answers: e.target.checked })}
            />
          }
          label="Shuffle Answer Options"
        />
        <FormControlLabel
          control={
            <Switch
              checked={quiz.show_correct_answers}
              onChange={(e) => setQuiz({ ...quiz, show_correct_answers: e.target.checked })}
            />
          }
          label="Show Correct Answers After Submission"
        />
        <FormControlLabel
          control={
            <Switch
              checked={quiz.show_feedback}
              onChange={(e) => setQuiz({ ...quiz, show_feedback: e.target.checked })}
            />
          }
          label="Show Feedback/Explanations"
        />
        <FormControlLabel
          control={
            <Switch
              checked={quiz.allow_review}
              onChange={(e) => setQuiz({ ...quiz, allow_review: e.target.checked })}
            />
          }
          label="Allow Students to Review Attempts"
        />
      </FormGroup>
    </Stack>
  );

  const renderQuestionsStep = () => (
    <Stack spacing={3}>
      <Paper elevation={2} sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          {editingQuestionIndex !== null ? 'Edit Question' : 'Add New Question'}
        </Typography>
        <Stack spacing={2}>
          <FormControl fullWidth>
            <InputLabel>Question Type</InputLabel>
            <Select
              value={currentQuestion.question_type}
              onChange={(e) => handleQuestionTypeChange(e.target.value as QuizQuestion['question_type'])}
              label="Question Type"
            >
              <MenuItem value="multiple_choice">Multiple Choice</MenuItem>
              <MenuItem value="true_false">True/False</MenuItem>
              <MenuItem value="short_answer">Short Answer</MenuItem>
              <MenuItem value="essay">Essay</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            multiline
            rows={2}
            label="Question"
            value={currentQuestion.question_text}
            onChange={(e) => setCurrentQuestion({ ...currentQuestion, question_text: e.target.value })}
            required
          />

          {(currentQuestion.question_type === 'multiple_choice' || currentQuestion.question_type === 'true_false') && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Answer Options
              </Typography>
              {currentQuestion.options?.map((option, index) => (
                <Stack key={option.id} direction="row" spacing={1} sx={{ mb: 1 }}>
                  <Checkbox
                    checked={currentQuestion.correct_answers?.includes(option.id) || false}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setCurrentQuestion({
                          ...currentQuestion,
                          correct_answers: [...(currentQuestion.correct_answers || []), option.id],
                        });
                      } else {
                        setCurrentQuestion({
                          ...currentQuestion,
                          correct_answers: currentQuestion.correct_answers?.filter((id) => id !== option.id) || [],
                        });
                      }
                    }}
                  />
                  <TextField
                    fullWidth
                    size="small"
                    value={option.text}
                    onChange={(e) => {
                      const newOptions = [...(currentQuestion.options || [])];
                      newOptions[index] = { ...option, text: e.target.value };
                      setCurrentQuestion({ ...currentQuestion, options: newOptions });
                    }}
                    disabled={currentQuestion.question_type === 'true_false'}
                  />
                </Stack>
              ))}
            </Box>
          )}

          {currentQuestion.question_type === 'short_answer' && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Acceptable Answers (one per line)
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={3}
                value={currentQuestion.correct_answers?.join('\n') || ''}
                onChange={(e) =>
                  setCurrentQuestion({
                    ...currentQuestion,
                    correct_answers: e.target.value.split('\n').filter((a) => a.trim()),
                  })
                }
                placeholder="Enter acceptable answers, one per line"
              />
            </Box>
          )}

          <TextField
            fullWidth
            multiline
            rows={2}
            label="Explanation (shown after submission)"
            value={currentQuestion.explanation}
            onChange={(e) => setCurrentQuestion({ ...currentQuestion, explanation: e.target.value })}
          />

          <Stack direction="row" spacing={2}>
            <TextField
              type="number"
              label="Points"
              value={currentQuestion.points}
              onChange={(e) => setCurrentQuestion({ ...currentQuestion, points: parseFloat(e.target.value) || 1 })}
              InputProps={{ inputProps: { min: 0, step: 0.5 } }}
            />
            <FormControl>
              <InputLabel>Difficulty</InputLabel>
              <Select
                value={currentQuestion.difficulty_level || 1}
                onChange={(e) => setCurrentQuestion({ ...currentQuestion, difficulty_level: e.target.value as number })}
                label="Difficulty"
              >
                <MenuItem value={1}>Easy</MenuItem>
                <MenuItem value={2}>Medium</MenuItem>
                <MenuItem value={3}>Hard</MenuItem>
              </Select>
            </FormControl>
          </Stack>

          <Button
            variant="contained"
            onClick={handleAddQuestion}
            startIcon={editingQuestionIndex !== null ? <SaveIcon /> : <AddIcon />}
          >
            {editingQuestionIndex !== null ? 'Update Question' : 'Add Question'}
          </Button>
          {editingQuestionIndex !== null && (
            <Button
              variant="outlined"
              onClick={() => {
                setEditingQuestionIndex(null);
                setCurrentQuestion({
                  question_type: 'multiple_choice',
                  question_text: '',
                  options: [
                    { id: 'a', text: '' },
                    { id: 'b', text: '' },
                    { id: 'c', text: '' },
                    { id: 'd', text: '' },
                  ],
                  correct_answers: [],
                  explanation: '',
                  points: 1,
                  sequence_order: quiz.questions.length + 1,
                  difficulty_level: 1,
                });
              }}
            >
              Cancel Edit
            </Button>
          )}
        </Stack>
      </Paper>

      <Typography variant="h6">Questions ({quiz.questions.length})</Typography>
      {quiz.questions.length === 0 ? (
        <Alert severity="info">No questions added yet</Alert>
      ) : (
        quiz.questions.map((question, index) => (
          <Card key={index}>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                <Box flex={1}>
                  <Typography variant="subtitle1" gutterBottom>
                    Q{index + 1}: {question.question_text}
                  </Typography>
                  <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
                    <Chip label={question.question_type.replace('_', ' ')} size="small" />
                    <Chip label={`${question.points} pts`} size="small" color="primary" />
                    {question.difficulty_level && (
                      <Chip
                        label={question.difficulty_level === 1 ? 'Easy' : question.difficulty_level === 2 ? 'Medium' : 'Hard'}
                        size="small"
                        color={question.difficulty_level === 1 ? 'success' : question.difficulty_level === 2 ? 'warning' : 'error'}
                      />
                    )}
                  </Stack>
                  {question.options && (
                    <Box sx={{ ml: 2 }}>
                      {question.options.map((opt) => (
                        <Typography
                          key={opt.id}
                          variant="body2"
                          sx={{
                            color: question.correct_answers?.includes(opt.id) ? 'success.main' : 'text.secondary',
                          }}
                        >
                          {opt.id}. {opt.text}
                          {question.correct_answers?.includes(opt.id) && ' ✓'}
                        </Typography>
                      ))}
                    </Box>
                  )}
                </Box>
                <Stack direction="row">
                  <IconButton onClick={() => handleEditQuestion(index)} size="small">
                    <EditIcon />
                  </IconButton>
                  <IconButton onClick={() => handleDeleteQuestion(index)} size="small" color="error">
                    <DeleteIcon />
                  </IconButton>
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        ))
      )}
    </Stack>
  );

  const renderReviewStep = () => {
    const totalPoints = quiz.questions.reduce((sum, q) => sum + q.points, 0);

    return (
      <Stack spacing={3}>
        <Alert severity="info">
          Please review your quiz before saving. You can go back to make changes if needed.
        </Alert>

        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Quiz Summary</Typography>
          <Stack spacing={1}>
            <Typography><strong>Title:</strong> {quiz.title}</Typography>
            <Typography><strong>Instructions:</strong> {quiz.instructions}</Typography>
            <Typography><strong>Questions:</strong> {quiz.questions.length}</Typography>
            <Typography><strong>Total Points:</strong> {totalPoints}</Typography>
            <Typography><strong>Time Limit:</strong> {quiz.time_limit_minutes ? `${quiz.time_limit_minutes} minutes` : 'No limit'}</Typography>
            <Typography><strong>Attempts Allowed:</strong> {quiz.attempts_allowed || 'Unlimited'}</Typography>
            <Typography><strong>Passing Score:</strong> {quiz.passing_score}%</Typography>
          </Stack>
        </Paper>

        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Settings</Typography>
          <Stack spacing={1}>
            <Typography>Shuffle Questions: {quiz.shuffle_questions ? 'Yes' : 'No'}</Typography>
            <Typography>Shuffle Answers: {quiz.shuffle_answers ? 'Yes' : 'No'}</Typography>
            <Typography>Show Correct Answers: {quiz.show_correct_answers ? 'Yes' : 'No'}</Typography>
            <Typography>Show Feedback: {quiz.show_feedback ? 'Yes' : 'No'}</Typography>
            <Typography>Allow Review: {quiz.allow_review ? 'Yes' : 'No'}</Typography>
          </Stack>
        </Paper>

        <Button
          variant="contained"
          size="large"
          onClick={handleSaveQuiz}
          disabled={isCreating || isUpdating}
          startIcon={<SaveIcon />}
        >
          {quizId ? 'Update Quiz' : 'Create Quiz'}
        </Button>
      </Stack>
    );
  };

  return (
    <Dialog open fullScreen>
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h5">{quizId ? 'Edit Quiz' : 'Create New Quiz'}</Typography>
          <IconButton onClick={onClose}>
            <DeleteIcon />
          </IconButton>
        </Stack>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ width: '100%', maxWidth: 900, mx: 'auto', py: 2 }}>
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {activeStep === 0 && renderSettingsStep()}
          {activeStep === 1 && renderQuestionsStep()}
          {activeStep === 2 && renderReviewStep()}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        {activeStep > 0 && (
          <Button onClick={handleBack} startIcon={<ArrowBack />}>
            Back
          </Button>
        )}
        {activeStep < steps.length - 1 && (
          <Button variant="contained" onClick={handleNext} endIcon={<ArrowForward />}>
            Next
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default QuizBuilder;