import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';

// Minimal Redux store configuration for Ulrich AI Chat
// The chat application doesn't currently use Redux state management
export const store = configureStore({
  reducer: {
    // Empty reducer - can be extended in the future if needed
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware(),
});

// Enable refetchOnFocus/refetchOnReconnect behaviors
setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;