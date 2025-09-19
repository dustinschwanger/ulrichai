import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../store';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface Instructor {
  id: string;
  firstName: string;
  lastName: string;
  title?: string;
  avatarUrl?: string;
}

export interface Course {
  id: string;
  organizationId: string;
  title: string;
  slug: string;
  description?: string;
  shortDescription?: string;
  thumbnailUrl?: string;
  instructorId: string;
  instructor?: Instructor;
  durationHours?: number;
  difficultyLevel: 'beginner' | 'intermediate' | 'advanced';
  category?: string;
  subcategory?: string;
  prerequisites: string[];
  tags: string[];
  isAiEnhanced: boolean;
  isPublished: boolean;
  isFeatured: boolean;
  publishedAt?: string;
  enrollmentType: 'open' | 'approval_required' | 'invitation_only';
  price: number;
  currency: string;
  enrolledCount?: number;
  rating?: number;
  reviewCount?: number;
  features?: {
    hasVideo?: boolean;
    hasQuiz?: boolean;
    hasCertificate?: boolean;
    hasLifetimeAccess?: boolean;
  };
  isBookmarked?: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Enrollment {
  id: string;
  userId: string;
  cohortId: string;
  enrollmentStatus: 'active' | 'completed' | 'dropped' | 'paused';
  progressPercentage: number;
  completedModules: number;
  completedLessons: number;
  enrolledAt: string;
  lastAccessedAt?: string;
}

export interface EnrolledCourse extends Course {
  enrollmentId: string;
  enrollmentStatus: 'active' | 'completed' | 'dropped' | 'paused';
  progressPercentage: number;
  completedModules: number;
  totalModules: number;
  completedLessons: number;
  totalLessons: number;
  lastAccessedAt?: string;
  enrolledAt: string;
  estimatedCompletion?: string;
  nextLesson?: {
    id: string;
    title: string;
    moduleTitle: string;
    duration: number;
  };
  certificate?: {
    available: boolean;
    earnedAt?: string;
    certificateUrl?: string;
  };
}

interface CoursesResponse {
  items: Course[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export const courseApi = createApi({
  reducerPath: 'courseApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${BASE_URL}/api/lms`,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.accessToken;
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Course', 'Enrollment'],
  endpoints: (builder) => ({
    getCourses: builder.query<
      CoursesResponse,
      {
        page?: number;
        limit?: number;
        search?: string;
        category?: string;
        difficultyLevel?: string;
        isPublished?: boolean;
      }
    >({
      query: (params) => ({
        url: '/courses',
        params,
      }),
      providesTags: ['Course'],
    }),
    getCourse: builder.query<Course, string>({
      query: (id) => `/courses/${id}`,
      providesTags: (result, error, id) => [{ type: 'Course', id }],
    }),
    createCourse: builder.mutation<Course, Partial<Course>>({
      query: (course) => ({
        url: '/courses',
        method: 'POST',
        body: course,
      }),
      invalidatesTags: ['Course'],
    }),
    updateCourse: builder.mutation<Course, { id: string; updates: Partial<Course> }>({
      query: ({ id, updates }) => ({
        url: `/courses/${id}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Course', id }, 'Course'],
    }),
    deleteCourse: builder.mutation<void, string>({
      query: (id) => ({
        url: `/courses/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Course'],
    }),
    enrollInCourse: builder.mutation<Enrollment, { courseId: string; cohortId: string }>({
      query: ({ courseId, cohortId }) => ({
        url: `/courses/${courseId}/enroll`,
        method: 'POST',
        body: { cohort_id: cohortId },
      }),
      invalidatesTags: ['Enrollment', 'Course'],
    }),
    getMyEnrollments: builder.query<EnrolledCourse[], void>({
      query: () => '/courses/enrollments/my',
      providesTags: ['Enrollment'],
    }),
    getEnrollment: builder.query<Enrollment, string>({
      query: (id) => `/enrollments/${id}`,
      providesTags: (result, error, id) => [{ type: 'Enrollment', id }],
    }),
    updateProgress: builder.mutation<
      Enrollment,
      { enrollmentId: string; contentItemId: string; status: string }
    >({
      query: ({ enrollmentId, ...data }) => ({
        url: `/enrollments/${enrollmentId}/progress`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { enrollmentId }) => [
        { type: 'Enrollment', id: enrollmentId },
      ],
    }),
    bookmarkCourse: builder.mutation<void, string>({
      query: (courseId) => ({
        url: `/courses/${courseId}/bookmark`,
        method: 'POST',
      }),
      invalidatesTags: ['Course'],
    }),
    unbookmarkCourse: builder.mutation<void, string>({
      query: (courseId) => ({
        url: `/courses/${courseId}/unbookmark`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Course'],
    }),
    getCategories: builder.query<string[], void>({
      query: () => '/categories',
      providesTags: ['Course'],
    }),
  }),
});

export const {
  useGetCoursesQuery,
  useGetCourseQuery,
  useCreateCourseMutation,
  useUpdateCourseMutation,
  useDeleteCourseMutation,
  useEnrollInCourseMutation,
  useGetMyEnrollmentsQuery,
  useGetEnrollmentQuery,
  useUpdateProgressMutation,
  useBookmarkCourseMutation,
  useUnbookmarkCourseMutation,
  useGetCategoriesQuery,
} = courseApi;