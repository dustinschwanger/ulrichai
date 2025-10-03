import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import authReducer from './slices/authSlice';
import { authApi } from './api/authApi';
import { courseApi } from './api/courseApi';
import { organizationApi } from './api/organizationApi';
import { quizApi } from './api/quizApi';
import { courseBuilderApi } from '../features/lms/courseBuilderSlice';
import { discussionsApi } from '../features/lms/discussionsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    [authApi.reducerPath]: authApi.reducer,
    [courseApi.reducerPath]: courseApi.reducer,
    [organizationApi.reducerPath]: organizationApi.reducer,
    [quizApi.reducerPath]: quizApi.reducer,
    [courseBuilderApi.reducerPath]: courseBuilderApi.reducer,
    [discussionsApi.reducerPath]: discussionsApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['auth/setUser'],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['meta.arg', 'payload.timestamp'],
        // Ignore these paths in the state
        ignoredPaths: ['auth.user'],
      },
    })
      .concat(authApi.middleware)
      .concat(courseApi.middleware)
      .concat(organizationApi.middleware)
      .concat(quizApi.middleware)
      .concat(courseBuilderApi.middleware)
      .concat(discussionsApi.middleware),
});

// Enable refetchOnFocus/refetchOnReconnect behaviors
setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;