// src/features/kvStorage/kvStorageSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import KvStorage from '../data_structures/kv_storage'; // Adjust the import path as needed

// Define the initial state type
interface KvStorageState {
  data: KvStorage<any>; // More descriptive name for the state field
}

// Define the initial state
const initialState: KvStorageState = {
  data: new KvStorage<any>(), // Ensure generics are used consistently
};

const kvStorageSlice = createSlice({
  name: 'kvStorage',
  initialState,
  reducers: {
    // Action to update a key-value pair in KVStorage
    updateKVStorage: (state, action: PayloadAction<{ key: string; value: any }>) => {
      const { key, value } = action.payload;
      // Using the class method to update the KVStorage instance
      state.data.set(key, value);
    },
    // Additional actions to handle other KVStorage operations can be added here
  },
});

// Export actions using destructuring to ensure correct naming
export const { updateKVStorage  } = kvStorageSlice.actions;

// Export the reducer
export default kvStorageSlice.reducer;
