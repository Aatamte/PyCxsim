// app/store.js
import { configureStore } from '@reduxjs/toolkit';
import environmentReducer from './reducers/environmentSlice';
import kvstorageReducer from './reducers/kv_storageSlice'

export const store = configureStore({
  reducer: {
    environment: environmentReducer,
    kv_storage: kvstorageReducer
  },
});

// Define the RootState type based on the store's reducers
export type RootState = ReturnType<typeof store.getState>;

// Define the AppDispatch type based on the store's dispatch function
export type AppDispatch = typeof store.dispatch;