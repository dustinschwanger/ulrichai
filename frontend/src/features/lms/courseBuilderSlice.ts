import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

// Types
export interface Course {
  id: string;
  organization_id: string;
  title: string;
  slug: string;
  description?: string;
  thumbnail_url?: string;
  instructor_id: string;
  instructor?: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
  };
  category?: string;
  subcategory?: string;
  difficulty_level?: string;
  duration_hours?: number;
  prerequisites: string[];
  tags: string[];
  is_published: boolean;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
  module_count?: number;
  lesson_count?: number;
}

export interface Section {
  id: string;
  title: string;
  description?: string;
  sequence_order: number;
  is_optional: boolean;
  is_locked: boolean;
  created_at: string;
  updated_at: string;
}

export interface Module {
  id: string;
  section_id: string;
  title: string;
  description?: string;
  sequence_order: number;
  is_optional: boolean;
  estimated_duration_minutes?: number;
  learning_objectives: string[];
  created_at: string;
  updated_at: string;
}

export interface Lesson {
  id: string;
  title: string;
  description?: string;
  sequence_order: number;
  lesson_type: 'standard' | 'video' | 'reading' | 'interactive' | 'assessment';
  estimated_duration_minutes?: number;
  is_required: boolean;
  content_data?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ContentItem {
  id: string;
  content_type: 'video' | 'document' | 'quiz' | 'discussion' | 'reflection' | 'poll' | 'assignment';
  title: string;
  description?: string;
  sequence_order: number;
  is_required: boolean;
  points_possible?: number;
  content_data?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CourseStructure {
  course: Course;
  sections: Array<Section & {
    modules: Array<Module & {
      lessons: Array<Lesson & {
        content_items: ContentItem[];
      }>;
    }>;
  }>;
}

// API Slice
export const courseBuilderApi = createApi({
  reducerPath: 'courseBuilderApi',
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.REACT_APP_API_URL ? `${process.env.REACT_APP_API_URL}/api/lms/course-builder` : '/api/lms/course-builder',
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('accessToken');
      console.log('Course Builder API - Token exists:', !!token);
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Course', 'Section', 'Module', 'Lesson', 'ContentItem'],
  endpoints: (builder) => ({
    // Course endpoints
    getCourses: builder.query<Course[], void>({
      query: () => '/courses',
      providesTags: ['Course'],
    }),
    getCourse: builder.query<Course, string>({
      query: (id) => `/courses/${id}`,
      providesTags: ['Course'],
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
      invalidatesTags: ['Course'],
    }),
    deleteCourse: builder.mutation<void, string>({
      query: (id) => ({
        url: `/courses/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Course'],
    }),
    getCourseStructure: builder.query<CourseStructure, string>({
      query: (courseId) => `/courses/${courseId}/structure`,
      providesTags: ['Course', 'Section', 'Module', 'Lesson', 'ContentItem'],
    }),

    // Section endpoints
    createSection: builder.mutation<Section, { courseId: string; section: Partial<Section> }>({
      query: ({ courseId, section }) => ({
        url: `/courses/${courseId}/sections`,
        method: 'POST',
        body: section,
      }),
      invalidatesTags: ['Section', 'Course'],
    }),
    updateSection: builder.mutation<Section, { id: string; updates: Partial<Section> }>({
      query: ({ id, updates }) => ({
        url: `/sections/${id}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: ['Section'],
    }),
    deleteSection: builder.mutation<void, string>({
      query: (id) => ({
        url: `/sections/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Section', 'Course'],
    }),

    // Module endpoints
    getModules: builder.query<Module[], string>({
      query: (courseId) => `/courses/${courseId}/modules`,
      providesTags: ['Module'],
    }),
    createModule: builder.mutation<Module, { courseId: string; module: Partial<Module> }>({
      query: ({ courseId, module }) => ({
        url: `/courses/${courseId}/modules`,
        method: 'POST',
        body: module,
      }),
      invalidatesTags: ['Module', 'Course'],
    }),
    updateModule: builder.mutation<Module, { id: string; updates: Partial<Module> }>({
      query: ({ id, updates }) => ({
        url: `/modules/${id}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: ['Module'],
    }),
    deleteModule: builder.mutation<void, string>({
      query: (id) => ({
        url: `/modules/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Module', 'Course'],
    }),

    // Lesson endpoints
    getLessons: builder.query<Lesson[], string>({
      query: (moduleId) => `/modules/${moduleId}/lessons`,
      providesTags: ['Lesson'],
    }),
    createLesson: builder.mutation<Lesson, { moduleId: string; lesson: Partial<Lesson> }>({
      query: ({ moduleId, lesson }) => ({
        url: `/modules/${moduleId}/lessons`,
        method: 'POST',
        body: lesson,
      }),
      invalidatesTags: ['Lesson', 'Module'],
    }),
    updateLesson: builder.mutation<Lesson, { id: string; updates: Partial<Lesson> }>({
      query: ({ id, updates }) => ({
        url: `/lessons/${id}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: ['Lesson'],
    }),
    deleteLesson: builder.mutation<void, string>({
      query: (id) => ({
        url: `/lessons/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Lesson', 'Module'],
    }),

    // Content Item endpoints
    getContentItems: builder.query<ContentItem[], string>({
      query: (lessonId) => `/lessons/${lessonId}/content`,
      providesTags: ['ContentItem'],
    }),
    createContentItem: builder.mutation<ContentItem, { lessonId: string; content: Partial<ContentItem> }>({
      query: ({ lessonId, content }) => ({
        url: `/lessons/${lessonId}/content`,
        method: 'POST',
        body: content,
      }),
      invalidatesTags: ['ContentItem', 'Lesson'],
    }),
    updateContentItem: builder.mutation<ContentItem, { id: string; updates: Partial<ContentItem> }>({
      query: ({ id, updates }) => ({
        url: `/content/${id}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: ['ContentItem'],
    }),
    deleteContentItem: builder.mutation<void, string>({
      query: (id) => ({
        url: `/content/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['ContentItem', 'Lesson'],
    }),

    // Media upload endpoints
    uploadLessonMedia: builder.mutation<any, { lessonId: string; formData: FormData }>({
      query: ({ lessonId, formData }) => ({
        url: `/lessons/${lessonId}/upload`,
        method: 'POST',
        body: formData,
      }),
      // Invalidate both Lesson and Course tags to ensure course structure refetches
      invalidatesTags: ['Lesson', 'Course'],
    }),
    deleteLessonMedia: builder.mutation<void, { lessonId: string; mediaId: string }>({
      query: ({ lessonId, mediaId }) => ({
        url: `/lessons/${lessonId}/media/${mediaId}`,
        method: 'DELETE',
      }),
      // Invalidate both Lesson and Course tags to ensure course structure refetches
      invalidatesTags: ['Lesson', 'Course'],
    }),
    linkExistingMedia: builder.mutation<any, { lessonId: string; mediaId: string }>({
      query: ({ lessonId, mediaId }) => {
        const formData = new FormData();
        formData.append('media_id', mediaId);
        return {
          url: `/lessons/${lessonId}/media/link`,
          method: 'POST',
          body: formData,
        };
      },
      invalidatesTags: ['Lesson', 'Course'],
    }),
    getCourseMedia: builder.query<any[], { courseId: string; mediaType?: string }>({
      query: ({ courseId, mediaType }) => ({
        url: `/courses/${courseId}/media`,
        params: mediaType ? { media_type: mediaType } : undefined,
      }),
      providesTags: ['Course'],
    }),

    // Course Version endpoints
    getCourseVersions: builder.query<any[], string>({
      query: (courseId) => `/courses/${courseId}/versions`,
      providesTags: (result, error, courseId) => [
        { type: 'Course', id: courseId },
      ],
    }),
    createCourseVersion: builder.mutation<any, { courseId: string; versionData: any }>({
      query: ({ courseId, versionData }) => ({
        url: `/courses/${courseId}/versions`,
        method: 'POST',
        body: versionData,
      }),
      invalidatesTags: (result, error, { courseId }) => [
        { type: 'Course', id: courseId },
      ],
    }),
    updateCourseVersion: builder.mutation<any, { courseId: string; versionId: string; updates: any }>({
      query: ({ courseId, versionId, updates }) => ({
        url: `/courses/${courseId}/versions/${versionId}`,
        method: 'PATCH',
        body: updates,
      }),
      invalidatesTags: (result, error, { courseId }) => [
        { type: 'Course', id: courseId },
      ],
    }),
    deleteCourseVersion: builder.mutation<any, { courseId: string; versionId: string }>({
      query: ({ courseId, versionId }) => ({
        url: `/courses/${courseId}/versions/${versionId}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, { courseId }) => [
        { type: 'Course', id: courseId },
      ],
    }),
  }),
});

// Export hooks
export const {
  useGetCoursesQuery,
  useGetCourseQuery,
  useCreateCourseMutation,
  useUpdateCourseMutation,
  useDeleteCourseMutation,
  useGetCourseStructureQuery,
  useCreateSectionMutation,
  useUpdateSectionMutation,
  useDeleteSectionMutation,
  useGetModulesQuery,
  useCreateModuleMutation,
  useUpdateModuleMutation,
  useDeleteModuleMutation,
  useGetLessonsQuery,
  useCreateLessonMutation,
  useUpdateLessonMutation,
  useDeleteLessonMutation,
  useGetContentItemsQuery,
  useCreateContentItemMutation,
  useUpdateContentItemMutation,
  useDeleteContentItemMutation,
  useUploadLessonMediaMutation,
  useDeleteLessonMediaMutation,
  useLinkExistingMediaMutation,
  useGetCourseMediaQuery,
  useGetCourseVersionsQuery,
  useCreateCourseVersionMutation,
  useUpdateCourseVersionMutation,
  useDeleteCourseVersionMutation,
} = courseBuilderApi;