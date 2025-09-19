import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../store';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface Organization {
  id: string;
  name: string;
  slug: string;
  logoUrl?: string;
  primaryColor: string;
  secondaryColor: string;
  customDomain?: string;
  settings: Record<string, any>;
  features: {
    aiChat: boolean;
    aiCourseBuilder: boolean;
    discussions: boolean;
    reflections: boolean;
    whiteLabeling: boolean;
  };
  subscriptionTier: 'basic' | 'professional' | 'enterprise';
  maxUsers: number;
  maxCourses: number;
  storageLimitGb: number;
  isActive: boolean;
  isVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

// Organizations endpoint returns array directly
type OrganizationsResponse = Organization[];

export const organizationApi = createApi({
  reducerPath: 'organizationApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${BASE_URL}/api/lms/`,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.accessToken;
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Organization'],
  endpoints: (builder) => ({
    getOrganizations: builder.query<
      OrganizationsResponse,
      { page?: number; limit?: number; isActive?: boolean }
    >({
      query: (params) => ({
        url: '/organizations',
        params,
      }),
      providesTags: ['Organization'],
    }),
    getOrganization: builder.query<Organization, string>({
      query: (id) => `/organizations/${id}`,
      providesTags: (result, error, id) => [{ type: 'Organization', id }],
    }),
    getOrganizationBySlug: builder.query<Organization, string>({
      query: (slug) => `/organizations/slug/${slug}`,
      providesTags: (result, error, slug) => [{ type: 'Organization', id: slug }],
    }),
    createOrganization: builder.mutation<Organization, Partial<Organization>>({
      query: (organization) => ({
        url: '/organizations',
        method: 'POST',
        body: organization,
      }),
      invalidatesTags: ['Organization'],
    }),
    updateOrganization: builder.mutation<
      Organization,
      { id: string; updates: Partial<Organization> }
    >({
      query: ({ id, updates }) => ({
        url: `/organizations/${id}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Organization', id },
        'Organization',
      ],
    }),
    updateOrganizationBranding: builder.mutation<
      Organization,
      {
        id: string;
        branding: {
          logoUrl?: string;
          primaryColor?: string;
          secondaryColor?: string;
          customDomain?: string;
        };
      }
    >({
      query: ({ id, branding }) => ({
        url: `/organizations/${id}/branding`,
        method: 'PUT',
        body: branding,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Organization', id }],
    }),
    deleteOrganization: builder.mutation<void, string>({
      query: (id) => ({
        url: `/organizations/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Organization'],
    }),
  }),
});

export const {
  useGetOrganizationsQuery,
  useGetOrganizationQuery,
  useGetOrganizationBySlugQuery,
  useCreateOrganizationMutation,
  useUpdateOrganizationMutation,
  useUpdateOrganizationBrandingMutation,
  useDeleteOrganizationMutation,
} = organizationApi;