// features/environment/environmentSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import Environment from '../data_structures/Environment'; // Adjust the import path as needed

// Define the initial state type
interface EnvironmentState {
  value: Environment;
}

// Define the initial state
const initialState: EnvironmentState = {
  value: new Environment(),
};

export const environmentSlice = createSlice({
  name: 'environment',
  initialState,
  reducers: {
    // Define a reducer and automatically generate an action
    setEnvironment: (state, action: PayloadAction<Environment>) => {
      state.value = action.payload;
    },
    // Add more reducers if needed
  },
});

// Export actions
export const { setEnvironment } = environmentSlice.actions;

// Export the reducer
export default environmentSlice.reducer;
