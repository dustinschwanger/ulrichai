import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from '../store';

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'student' | 'instructor' | 'admin' | 'super_admin';
  organizationId: string;
  avatarUrl?: string;
  companyName?: string;
  jobTitle?: string;
  department?: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const initialState: AuthState = {
  user: null,
  accessToken: localStorage.getItem('accessToken'),
  refreshToken: localStorage.getItem('refreshToken'),
  isAuthenticated: false,
  isLoading: true,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{
        user: User;
        accessToken: string;
        refreshToken: string;
      }>
    ) => {
      const { user, accessToken, refreshToken } = action.payload;
      state.user = user;
      state.accessToken = accessToken;
      state.refreshToken = refreshToken;
      state.isAuthenticated = true;
      state.isLoading = false;

      // Store tokens in localStorage
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
    },
    setUser: (state, action: PayloadAction<User | null>) => {
      state.user = action.payload;
      state.isAuthenticated = !!action.payload;
      state.isLoading = false;
    },
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.isLoading = false;

      // Clear tokens from localStorage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
});

export const { setCredentials, setUser, logout, setLoading } = authSlice.actions;

// Selectors
export const selectCurrentUser = (state: RootState) => state.auth.user;
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated;
export const selectAccessToken = (state: RootState) => state.auth.accessToken;
export const selectIsLoading = (state: RootState) => state.auth.isLoading;
export const selectUserRole = (state: RootState) => state.auth.user?.role;

// Helper selectors for role-based access
export const selectIsStudent = (state: RootState) => state.auth.user?.role === 'student';
export const selectIsInstructor = (state: RootState) =>
  state.auth.user?.role === 'instructor' ||
  state.auth.user?.role === 'admin' ||
  state.auth.user?.role === 'super_admin';
export const selectIsAdmin = (state: RootState) =>
  state.auth.user?.role === 'admin' ||
  state.auth.user?.role === 'ADMIN' ||
  state.auth.user?.role === 'super_admin' ||
  state.auth.user?.role === 'INSTRUCTOR' ||
  state.auth.user?.role === 'instructor'; // Temporarily allow instructor to see admin
export const selectIsSuperAdmin = (state: RootState) => state.auth.user?.role === 'super_admin';

export default authSlice.reducer;