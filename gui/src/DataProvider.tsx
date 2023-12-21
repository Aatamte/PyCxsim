import React, {createContext, useReducer, useContext, useEffect, ReactNode, useState} from 'react';
import Environment from './data_structures/Environment';
import {WebSocketManager} from "./websocket_client"; // Adjust the import path as necessary
import Agent from "./data_structures/agent";
import Artifact from "./data_structures/artifact";
type WebSocketStatus = "connecting" | "open" | "closing" | "closed" | "unknown";

class SocketParams {
    public host: string = 'ws://localhost';
    public port: string = '8765';
    public status: WebSocketStatus = "closed"

    constructor() {
        this.host = 'ws://localhost';
        this.port = '8765';
        this.status = "closed"
    }

}

// Define the shape of your application's state
interface AppState {
  environment: Environment;
  socketParams: SocketParams;
}

// Define the shape of actions
type Action =
  | { type: 'ENVIRONMENT_CHANGE', payload: Environment }
  | {type: 'SOCKET_VARIABLES', payload: SocketParams}
  // ... other action types

// Initial state
const initialState: AppState = {
    environment: new Environment(),
    socketParams: new SocketParams()
};

// Create context
const DataContext = createContext({
  state: initialState,
  dispatch: (() => {}) as React.Dispatch<Action>,
  handleReconnect: async () => false, // handleReconnect is now an async function returning a boolean
  sendData: (() => {}) as (data: any) => void,
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
        socketParams: action.payload,
      };
    default:
      return state;
  }
};

export const DataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [state, dispatch] = useReducer(reducer, initialState);
    const [webSocketStatus, setWebSocketStatus] = useState<WebSocketStatus>('unknown');
    const [wsManager, setWsManager] = useState<WebSocketManager | null>(null);

    useEffect(() => {

    }, [state]);

    const updateEnvironment = () => {
        dispatch({ type: 'ENVIRONMENT_CHANGE', payload:  state.environment});
    }

    const handleEnvironmentUpdate = (message: any) => {

    }

    const handleEnvironmentVariables = (message: any) => {
      if (state.environment) {
            // Example of updating name
          Object.entries(message.content).forEach(([key, value]) => {
                state.environment.updateEnvironment(key, value);
            });
            // Dispatch an action to trigger state update
            updateEnvironment();
          }
    }

    const handleAgentUpdate = (message: any) => {
        let agent_name = message.content.name
        console.log(agent_name)
        Object.entries(message.content).forEach(([key, value]) => {
                state.environment.agents[agent_name].updateAgent(key, value)
        });

        // Dispatch an action to trigger state update
        updateEnvironment();
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
          updateEnvironment();
          }
    }


    const handleArtifactInitialization = (message: any) => {
        let agent_name = message.content.name
        console.log(agent_name)
            let artifact = new Artifact()
            Object.entries(message.content).forEach(([key, value]) => {
                    artifact.updateArtifact(key, value);
            });
            state.environment.addArtifact(artifact)
        // Dispatch an action to trigger state update
        updateEnvironment();
    }


    const onMessage = (message: any) => {
    // @ts-ignore
      console.log("message contents: ", message)
      switch (message.type) {
      case 'ENVIRONMENT_CHANGE':
          handleEnvironmentVariables(message)
          break
      case 'AGENT_VARIABLES':
          handleAgentVariables(message)
          break;
      case 'AGENT_UPDATE':
          handleAgentUpdate(message)
          break;
      case 'AGENT_INIT':
          handleAgentVariables(message)
          break;
      case 'INIT_ARTIFACTS':
          handleArtifactInitialization(message)
          break;
    }
    };

    const onOpen = () => {
      console.log("onOpen")
        state.socketParams.status = "open"
      dispatch({ type: 'SOCKET_VARIABLES', payload:  state.socketParams});
      // initialize the state
      sendData("INIT")

    }

    const onClose = () => {
      state.socketParams.status = "closed"
      dispatch({ type: 'SOCKET_VARIABLES', payload:  state.socketParams});
      state.environment.clear();
      dispatch({ type: 'ENVIRONMENT_CHANGE', payload:  state.environment});
    }

    // Set up WebSocket connection
    useEffect(() => {
        const manager = new WebSocketManager(
            state.socketParams.host, state.socketParams.port, {
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
    const handleReconnect = async () => {
        try {
            const success = await wsManager?.manualReconnect();
            if (success) {
                console.debug("Reconnect successful");
                onOpen(); // Assuming onOpen is a callback that handles the 'open' event.
                return true;
            } else {
                console.debug("Reconnect failed");
                return false;
            }
        } catch (error) {
            console.error("Reconnection attempt threw an error:", error);
            return false;
        }
    };

      // Function to send data via WebSocket
      const sendData = (data: any) => {
        if (wsManager?.client.getStatus() === 'open') {
          wsManager.client.sendMessage(data);
        } else {
          console.error("WebSocket is not open. Cannot send data.");
        }
      };


  return (
    <DataContext.Provider value={{ state, dispatch, handleReconnect, sendData }}>
      {children}
    </DataContext.Provider>
  );
};

// Custom hook to use the data context
export const useData = () => useContext(DataContext);
