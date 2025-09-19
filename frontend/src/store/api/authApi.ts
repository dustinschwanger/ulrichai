import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { setCredentials, logout } from '../slices/authSlice';
import type { RootState } from '../store';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  organizationId: string;
  role?: string;
  department?: string;
  jobTitle?: string;
}

interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
    organization_id: string;
    avatar_url?: string;
    company_name?: string;
    job_title?: string;
    department?: string;
  };
}

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${BASE_URL}/api/lms/auth`,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.accessToken;
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['User'],
  endpoints: (builder) => ({
    login: builder.mutation<AuthResponse, LoginRequest>({
      query: (credentials) => ({
        url: '/login-json',
        method: 'POST',
        body: credentials,
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          dispatch(
            setCredentials({
              user: {
                id: data.user.id,
                email: data.user.email,
                firstName: data.user.first_name,
                lastName: data.user.last_name,
                role: data.user.role as any,
                organizationId: data.user.organization_id,
                avatarUrl: data.user.avatar_url,
                companyName: data.user.company_name,
                jobTitle: data.user.job_title,
                department: data.user.department,
              },
              accessToken: data.access_token,
              refreshToken: data.refresh_token,
            })
          );
        } catch (err) {
          // Error handling
        }
      },
    }),
    register: builder.mutation<AuthResponse, RegisterRequest>({
      query: (userData) => ({
        url: '/register',
        method: 'POST',
        body: {
          email: userData.email,
          password: userData.password,
          first_name: userData.firstName,
          last_name: userData.lastName,
          organization_id: userData.organizationId,
          role: userData.role,
          department: userData.department,
          job_title: userData.jobTitle,
        },
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          dispatch(
            setCredentials({
              user: {
                id: data.user.id,
                email: data.user.email,
                firstName: data.user.first_name,
                lastName: data.user.last_name,
                role: data.user.role as any,
                organizationId: data.user.organization_id,
                avatarUrl: data.user.avatar_url,
                companyName: data.user.company_name,
                jobTitle: data.user.job_title,
                department: data.user.department,
              },
              accessToken: data.access_token,
              refreshToken: data.refresh_token,
            })
          );
        } catch (err) {
          // Error handling
        }
      },
    }),
    refreshToken: builder.mutation<
      { access_token: string },
      { refresh_token: string }
    >({
      query: (data) => ({
        url: '/refresh',
        method: 'POST',
        body: data,
      }),
    }),
    getProfile: builder.query<AuthResponse['user'], void>({
      query: () => '/me',
      providesTags: ['User'],
    }),
    updateProfile: builder.mutation<AuthResponse['user'], Partial<AuthResponse['user']>>({
      query: (updates) => ({
        url: '/profile',
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: ['User'],
    }),
    changePassword: builder.mutation<
      { message: string },
      { current_password: string; new_password: string }
    >({
      query: (passwords) => ({
        url: '/change-password',
        method: 'POST',
        body: passwords,
      }),
    }),
    logoutUser: builder.mutation<void, void>({
      query: () => ({
        url: '/logout',
        method: 'POST',
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled;
          dispatch(logout());
        } catch (err) {
          dispatch(logout()); // Logout even if API call fails
        }
      },
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useRefreshTokenMutation,
  useGetProfileQuery,
  useUpdateProfileMutation,
  useChangePasswordMutation,
  useLogoutUserMutation,
} = authApi;