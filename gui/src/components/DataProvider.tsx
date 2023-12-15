import React, {createContext, useReducer, useContext, useEffect, ReactNode, useState} from 'react';
import Environment from './data_structures/Environment';
import {WebSocketManager} from "./websocket_client"; // Adjust the import path as necessary
import Agent from "./data_structures/agent";

type WebSocketStatus = "connecting" | "open" | "closing" | "closed" | "unknown";


// Define the shape of your application's state
interface AppState {
  environment: Environment;
  status: WebSocketStatus;
}

// Define the shape of actions
type Action =
  | { type: 'ENVIRONMENT_CHANGE', payload: Environment }
  | {type: 'SOCKET_VARIABLES', payload: WebSocketStatus}
  // ... other action types

// Initial state
const initialState: AppState = {
    environment: new Environment(),
    status: "closed",
};

// Create context
const DataContext = createContext<
    {
      state: AppState;
      dispatch: React.Dispatch<Action>;
      handleReconnect: () => void;
      sendData: (data: any) => void;
    }>({
      state: initialState,
      dispatch: () => null,
      handleReconnect: () => {},
    sendData: () => {},
});

// Reducer function to update state
const reducer = (state: AppState, action: Action): AppState => {
  switch (action.type) {
    case 'ENVIRONMENT_CHANGE':
      return {
        ...state,
        environment: action.payload,
      };
    case 'SOCKET_VARIABLES':
      return {
        ...state,
        status: action.payload,
      };
    default:
      return state;
  }
};

export const DataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [webSocketStatus, setWebSocketStatus] = useState<WebSocketStatus>('unknown');
  const [wsManager, setWsManager] = useState<WebSocketManager | null>(null);

  const host = 'ws://localhost';
  const port = '8765';

  const handleEnvironmentVariables = (message: any) => {
      if (state.environment) {
            // Example of updating name
              Object.entries(message.content).forEach(([key, value]) => {
                    state.environment.updateEnvironment(key, value);
                });
            // Dispatch an action to trigger state update
            dispatch({ type: 'ENVIRONMENT_CHANGE', payload:  state.environment});
          }
  }

  const handleAgentVariables = (message: any) => {
      if (state.environment) {
            // Example of updating name
            let agent = new Agent()
            Object.entries(message.content).forEach(([key, value]) => {
                    agent.updateAgent(key, value);
            });
            state.environment.addAgent(agent)
            // Dispatch an action to trigger state update
            dispatch({ type: 'ENVIRONMENT_CHANGE', payload:  state.environment});
          }
  }


  const onMessage = (message: any) => {
    // @ts-ignore
      switch (message.type) {
      case 'ENVIRONMENT_CHANGE':
          handleEnvironmentVariables(message)
          break
      case 'AGENT_VARIABLES':
          handleAgentVariables(message)
          break;
      // ... handle other message types
    }
  };

  const onOpen = () => {
      console.log("onOpen")
      state.status = "open"
      dispatch({ type: 'SOCKET_VARIABLES', payload:  state.status});
      // initialize the state
      sendData("INIT")

  }

  const onClose = () => {
      state.status = "closed"
      dispatch({ type: 'SOCKET_VARIABLES', payload:  state.status});
      let new_environment = new Environment();
      dispatch({ type: 'ENVIRONMENT_CHANGE', payload:  new_environment});
  }

  // Set up WebSocket connection
    useEffect(() => {
        const manager = new WebSocketManager(
            host, port, {
                onMessage,
             onOpen,
             onClose,
             onError: (error: any) => { console.error("WebSocket error", error); },
          }
        );

        setWsManager(manager);

        // Start the automatic reconnect scheduler
        manager.startReconnectScheduler();

        return () => {
          // Clean up WebSocket connection when component unmounts
          manager.stopReconnectScheduler();
          manager.client.close();
        };
      }, []);

      // Function to manually trigger a reconnect
      const handleReconnect = () => {

        wsManager?.manualReconnect().then(success => {
            if (success) {
                console.debug("Reconnect successful");
                onOpen();
            } else {
                console.debug("Reconnect failed");
            }
        });
      };

      // Function to send data via WebSocket
      const sendData = (data: any) => {
        if (wsManager?.client.getStatus() === 'open') {
          wsManager.client.sendMessage(data);
        } else {
          console.error("WebSocket is not open. Cannot send data.");
        }
      };

  // Update WebSocket status
  useEffect(() => {
    if (wsManager) {
      const interval = setInterval(() => {
          setWebSocketStatus(wsManager.client.getStatus());
          state.status = webSocketStatus
      }, 1000); // Update status every 1 second

      return () => clearInterval(interval);
    }
  }, [wsManager]);

  return (
    <DataContext.Provider value={{ state, dispatch, handleReconnect, sendData }}>
      {children}
    </DataContext.Provider>
  );
};

// Custom hook to use the data context
export const useData = () => useContext(DataContext);
