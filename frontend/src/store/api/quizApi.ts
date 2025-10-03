import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../store';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Types
export interface QuizOption {
  id: string;
  text: string;
}

export interface QuizQuestion {
  id?: string;
  question_type: 'multiple_choice' | 'true_false' | 'short_answer' | 'essay';
  question_text: string;
  options?: QuizOption[];
  correct_answers?: string[];
  explanation?: string;
  points: number;
  sequence_order: number;
  difficulty_level?: number;
}

export interface QuizCreate {
  content_item_id: string;
  title: string;
  instructions: string;
  time_limit_minutes?: number;
  attempts_allowed?: number;
  passing_score: number;
  shuffle_questions?: boolean;
  shuffle_answers?: boolean;
  show_correct_answers?: boolean;
  show_feedback?: boolean;
  allow_review?: boolean;
  questions: QuizQuestion[];
}

export interface Quiz {
  id: string;
  content_item_id: string;
  title: string;
  instructions: string;
  time_limit_minutes?: number;
  attempts_allowed?: number;
  passing_score: number;
  shuffle_questions: boolean;
  shuffle_answers: boolean;
  show_correct_answers: boolean;
  show_feedback: boolean;
  allow_review: boolean;
  question_count: number;
  total_points: number;
  created_at: string;
  updated_at: string;
}

export interface QuizAttempt {
  id: string;
  user_id: string;
  quiz_id: string;
  attempt_number: number;
  started_at: string;
  submitted_at?: string;
  time_spent_seconds?: number;
  score?: number;
  points_earned?: number;
  points_possible?: number;
  passed?: boolean;
  status: 'in_progress' | 'submitted' | 'graded' | 'abandoned';
}

export interface QuizResponse {
  question_id: string;
  answer: string[];
}

export interface QuizSubmission {
  attempt_id: string;
  responses: QuizResponse[];
}

export interface QuizReview {
  quiz_title: string;
  quiz_id: string;
  attempt: QuizAttempt;
  questions: Array<{
    question: QuizQuestion & { id: string };
    user_response: string[];
    is_correct: boolean;
    points_earned: number;
    explanation?: string;
  }>;
}

export const quizApi = createApi({
  reducerPath: 'quizApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${BASE_URL}/api/lms/quiz`,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.accessToken;
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Quiz', 'QuizAttempt', 'QuizQuestion'],
  endpoints: (builder) => ({
    // Create a new quiz
    createQuiz: builder.mutation<Quiz, QuizCreate>({
      query: (quizData) => ({
        url: '/',
        method: 'POST',
        body: quizData,
      }),
      invalidatesTags: ['Quiz'],
    }),

    // Get quiz by ID
    getQuiz: builder.query<Quiz, string>({
      query: (quizId) => `/${quizId}`,
      providesTags: (result) =>
        result ? [{ type: 'Quiz', id: result.id }] : [],
    }),

    // Get quiz by content item ID
    getQuizByContentItem: builder.query<Quiz, string>({
      query: (contentItemId) => `/by-content-item/${contentItemId}`,
      providesTags: (result) =>
        result ? [{ type: 'Quiz', id: result.id }] : [],
    }),

    // Update quiz
    updateQuiz: builder.mutation<Quiz, { quizId: string; data: Partial<QuizCreate> }>({
      query: ({ quizId, data }) => ({
        url: `/${quizId}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result) =>
        result ? [{ type: 'Quiz', id: result.id }] : [],
    }),

    // Delete quiz
    deleteQuiz: builder.mutation<void, string>({
      query: (quizId) => ({
        url: `/${quizId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Quiz'],
    }),

    // Get quiz questions (for taking quiz)
    getQuizQuestions: builder.query<QuizQuestion[], string>({
      query: (quizId) => `/${quizId}/questions`,
      providesTags: ['QuizQuestion'],
    }),

    // Start quiz attempt
    startQuizAttempt: builder.mutation<QuizAttempt, { quiz_id: string }>({
      query: (data) => ({
        url: '/attempt/start',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['QuizAttempt'],
    }),

    // Submit quiz attempt
    submitQuizAttempt: builder.mutation<{
      attempt: QuizAttempt;
      questions_correct: number;
      questions_answered: number;
    }, QuizSubmission>({
      query: (submission) => ({
        url: '/attempt/submit',
        method: 'POST',
        body: submission,
      }),
      invalidatesTags: ['QuizAttempt'],
    }),

    // Get quiz attempt review
    getQuizReview: builder.query<QuizReview, string>({
      query: (attemptId) => `/attempt/${attemptId}/review`,
    }),

    // Get user's attempts for a quiz
    getUserQuizAttempts: builder.query<QuizAttempt[], string>({
      query: (quizId) => `/attempts/my?quiz_id=${quizId}`,
      providesTags: ['QuizAttempt'],
    }),

    // Get all attempts for a quiz (instructor)
    getQuizAttempts: builder.query<QuizAttempt[], string>({
      query: (quizId) => `/attempts?quiz_id=${quizId}`,
      providesTags: ['QuizAttempt'],
    }),
  }),
});

// Export hooks for use in components
export const {
  useCreateQuizMutation,
  useGetQuizQuery,
  useGetQuizByContentItemQuery,
  useUpdateQuizMutation,
  useDeleteQuizMutation,
  useGetQuizQuestionsQuery,
  useStartQuizAttemptMutation,
  useSubmitQuizAttemptMutation,
  useGetQuizReviewQuery,
  useGetUserQuizAttemptsQuery,
  useGetQuizAttemptsQuery,
} = quizApi;