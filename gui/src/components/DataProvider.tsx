import React, {createContext, useReducer, useContext, useEffect, ReactNode, useState} from 'react';
import Environment from './data_structures/Environment';
import WebSocketClient from "./websocket_client"; // Adjust the import path as necessary

// Define the shape of your application's state
interface AppState {
  environment: Environment;
  // ... other state elements
}

// Define the shape of actions
type Action =
  | { type: 'ENVIRONMENT_VARIABLES', payload: Environment }
  // ... other action types

// Initial state
const initialState: AppState = {
  environment: new Environment(),
};

// Create context
const DataContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<Action>;
}>({
  state: initialState,
  dispatch: () => null // Placeholder function
});

// Reducer function to update state
const reducer = (state: AppState, action: Action): AppState => {
  switch (action.type) {
    case 'ENVIRONMENT_VARIABLES':
        console.log("Updating environment with:", action.payload);
      return {
        ...state,
        environment: action.payload,
      };
    // ... other actions
    default:
      return state;
  }
};

type WebSocketStatus = "connecting" | "open" | "closing" | "closed" | "unknown";

export const DataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [webSocketStatus, setWebSocketStatus] = useState<WebSocketStatus>('unknown');
  const [wsClient, setWsClient] = useState<WebSocketClient | null>(null);

  const handleMessage = (message: any) => {
      console.log("handle message", message)
      console.log("message type", message.type)
    // Handle the message and dispatch actions to the reducer
    switch (message.type) {
      case 'ENVIRONMENT_VARIABLES':
          if (state.environment) {
            // Example of updating name
              Object.entries(message.content).forEach(([key, value]) => {
                  console.log("updating: ", key)
                    state.environment.updateEnvironment(key, value);
                });
            // Dispatch an action to trigger state update
            dispatch({ type: 'ENVIRONMENT_VARIABLES', payload:  state.environment});
          }
      break;
      // ... handle other message types
    }
  };

    useEffect(() => {
        const client = new WebSocketClient('ws://localhost', '8765', handleMessage);
        setWsClient(client);

        // Update the status whenever the state changes
        const interval = setInterval(() => {
            setWebSocketStatus(client.getStatus());
        }, 1000); // Update status every 1 second

        return () => {
            clearInterval(interval);
            client.close();
        };
    }, []);

    const handleReconnect = () => {
        if (wsClient) {
            wsClient.reconnect(); // Assuming reconnect method exists in WebSocketClient
        }

        // handleReconnectError('');
    };

  return (
    <DataContext.Provider value={{ state, dispatch }}>
      {children}
    </DataContext.Provider>
  );
};

// Custom hook to use the data context
export const useData = () => useContext(DataContext);
