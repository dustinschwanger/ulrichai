import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { RootState } from '../../app/store';

interface DiscussionThread {
  id: string;
  lesson_id: string;
  author_id: string;
  author_name?: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  is_pinned: boolean;
  is_locked: boolean;
  upvotes: number;
  replies_count: number;
  tags?: string[];
}

interface DiscussionReply {
  id: string;
  thread_id: string;
  author_id: string;
  author_name?: string;
  content: string;
  created_at: string;
  updated_at: string;
  upvotes: number;
  is_solution?: boolean;
}

interface CreateThreadData {
  lesson_id: string;
  title: string;
  content: string;
  tags?: string[];
}

interface CreateReplyData {
  thread_id: string;
  content: string;
}

interface UpdateThreadData {
  title?: string;
  content?: string;
  is_pinned?: boolean;
  is_locked?: boolean;
  tags?: string[];
}

interface UpdateReplyData {
  content?: string;
  is_solution?: boolean;
}

export const discussionsApi = createApi({
  reducerPath: 'discussionsApi',
  baseQuery: fetchBaseQuery({
    baseUrl: 'http://localhost:8000/api/lms',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Thread', 'Reply'],
  endpoints: (builder) => ({
    // Thread endpoints
    getThreadsByLesson: builder.query<DiscussionThread[], string>({
      query: (lessonId) => `/discussions/lessons/${lessonId}/threads`,
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Thread' as const, id })),
              { type: 'Thread', id: 'LIST' },
            ]
          : [{ type: 'Thread', id: 'LIST' }],
    }),

    getThread: builder.query<DiscussionThread, string>({
      query: (threadId) => `/discussions/threads/${threadId}`,
      providesTags: (result, error, id) => [{ type: 'Thread', id }],
    }),

    createThread: builder.mutation<DiscussionThread, CreateThreadData>({
      query: (data) => ({
        url: '/discussions/threads',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: [{ type: 'Thread', id: 'LIST' }],
    }),

    updateThread: builder.mutation<DiscussionThread, { id: string; data: UpdateThreadData }>({
      query: ({ id, data }) => ({
        url: `/discussions/threads/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Thread', id }],
    }),

    deleteThread: builder.mutation<void, string>({
      query: (id) => ({
        url: `/discussions/threads/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: [{ type: 'Thread', id: 'LIST' }],
    }),

    upvoteThread: builder.mutation<{ upvotes: number }, string>({
      query: (id) => ({
        url: `/discussions/threads/${id}/upvote`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [{ type: 'Thread', id }],
    }),

    // Reply endpoints
    getRepliesByThread: builder.query<DiscussionReply[], string>({
      query: (threadId) => `/discussions/threads/${threadId}/replies`,
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Reply' as const, id })),
              { type: 'Reply', id: 'LIST' },
            ]
          : [{ type: 'Reply', id: 'LIST' }],
    }),

    createReply: builder.mutation<DiscussionReply, CreateReplyData>({
      query: (data) => ({
        url: '/discussions/replies',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: [{ type: 'Reply', id: 'LIST' }],
    }),

    updateReply: builder.mutation<DiscussionReply, { id: string; data: UpdateReplyData }>({
      query: ({ id, data }) => ({
        url: `/discussions/replies/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Reply', id }],
    }),

    deleteReply: builder.mutation<void, string>({
      query: (id) => ({
        url: `/discussions/replies/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: [{ type: 'Reply', id: 'LIST' }],
    }),

    upvoteReply: builder.mutation<{ upvotes: number }, string>({
      query: (id) => ({
        url: `/discussions/replies/${id}/upvote`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [{ type: 'Reply', id }],
    }),

    markReplyAsSolution: builder.mutation<DiscussionReply, string>({
      query: (id) => ({
        url: `/discussions/replies/${id}/solution`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [{ type: 'Reply', id }],
    }),
  }),
});

export const {
  useGetThreadsByLessonQuery,
  useGetThreadQuery,
  useCreateThreadMutation,
  useUpdateThreadMutation,
  useDeleteThreadMutation,
  useUpvoteThreadMutation,
  useGetRepliesByThreadQuery,
  useCreateReplyMutation,
  useUpdateReplyMutation,
  useDeleteReplyMutation,
  useUpvoteReplyMutation,
  useMarkReplyAsSolutionMutation,
} = discussionsApi;