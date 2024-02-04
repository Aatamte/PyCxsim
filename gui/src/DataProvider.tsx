import React, {createContext, useReducer, useContext, useEffect, ReactNode, useState} from 'react';
import Environment from './data_structures/Environment';
import SocketClient from "./websocket_client"; // Adjust the import path as necessary
import SocketParams from "./data_structures/SocketParams";
import Agent from "./data_structures/agent";
import Artifact from "./data_structures/artifact";
import KVStorage from "./data_structures/kv_storage";

// Define the shape of your application's state
interface AppState {
  environment: Environment;
  socketParams: SocketParams;
  kv_storage: KVStorage<any>;
}

// Define the shape of actions
type Action =
  | { type: 'UPDATE_ENVIRONMENT', payload: Environment }
  | {type: 'UPDATE_SOCKET', payload: SocketParams}
  | { type: 'UPDATE_KV', payload: KVStorage<any>}



// Initial state
const initialState: AppState = {
    environment: new Environment(),
    socketParams: new SocketParams(),
    kv_storage: new KVStorage<any>()
};

// Create context with the extended type
// Create context
const DataContext = createContext({
  state: initialState,
  dispatch: (() => {}) as React.Dispatch<Action>,
  handleReconnect: async () => false, // handleReconnect is now an async function returning a boolean
  sendData: (() => {}) as (ev: any, data: any) => void,
});

// Reducer function
const reducer = (state: AppState, action: Action): AppState => {
  switch (action.type) {
    case 'UPDATE_ENVIRONMENT':
      return { ...state, environment: action.payload };
    case 'UPDATE_SOCKET': // Ensure this case matches your actual action type
      return { ...state, socketParams: action.payload };
    case 'UPDATE_KV': // Handle KV storage updates if applicable
      return { ...state, kv_storage: action.payload };
    default:
      return state;
  }
};

export const DataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [state, dispatch] = useReducer(reducer, initialState);
    const [socket, setSocket] = useState(new SocketClient())

      // Define the update function
      const update = (_state: any) => {
        dispatch({ type: 'UPDATE_ENVIRONMENT', payload: _state.environment });
        dispatch({ type: 'UPDATE_KV', payload: _state.kv_storage });
        dispatch({ type: 'UPDATE_SOCKET', payload: _state.socketParams });
      };

    const onConnect = () => {
        console.log("onOpen");
        sendData("server", "kv_storage")
        update(state)
    };

    const onClose = () => {
        state.kv_storage.set("server_connection", "closed")
        state.environment.clear()
        update(state)
    }

    useEffect(() => {
        // Define the callback functions
        const callbacks = {
            onConnect: onConnect,
            onDisconnect: onClose,
            onData: onData,
            onError: (error: any) => console.error("WebSocket error", error)
        };

        socket.connect(
            state.socketParams.host,
            state.socketParams.port,
            callbacks
        );

    }, []);

    // Function to manually trigger a reconnect
    const handleReconnect = async () => {
        try {
            const success = true
            if (success) {
                console.debug("Reconnect successful");
                onConnect(); // Assuming onOpen is a callback that handles the 'open' event.
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

    const forEnvironment = (header : string, content: any) => {
        Object.entries(content).forEach(([key, value]) => {
            state.environment.set(key, value)
        })
    }

    const forAgents = (header : string, content: Record<string, any>) => {
        Object.entries(content).forEach(([key, value]) => {
            var agent = new Agent()
            Object.entries(value).forEach(([key, value]) => {
                agent.set(key, value)
            })
            state.environment.addAgent(agent)
        })
    }

    const forArtifacts = (header : string, content: Record<string, any>) => {
        Object.entries(content).forEach(([key, value]) => {
            let artifact = new Artifact()
            Object.entries(value).forEach(([key, value]) => {
                artifact.set(key, value)
            })
            state.environment.addArtifact(artifact)
        })
    }

    const onData = (msg: any) => {
        const header = msg["header"]
        const content = msg["content"]
        console.log("onData: ", msg)
        console.log(header)
        if (header === "logs") {
            state.environment.addLog(content.level, content.msg)
        } else if (header === "kv_storage") {
            // Use Object.entries to iterate over [key, value] pairs
            Object.entries(content).forEach(([key, value]) => {
                state.kv_storage.set(key, value); // Set key-value pair in kv_storage
            });
        } else if (header === "full_refresh") {
            forEnvironment(header, content)
        } else if (header === "forAgents") {
            forAgents(header, content)
        } else if (header === "forArtifacts") {
            forArtifacts(header, content)
        }

        update(state)
    };

    const sendData = (header: string, content: any) => {
        const msg = {
            "header": header,
            "content": content,
            "source": "GUI"
        }
        socket.send("data", msg);
    };

  return (
    <DataContext.Provider value={{ state, dispatch, handleReconnect, sendData}}>
      {children}
    </DataContext.Provider>
  );
};

// Custom hook to use the data context
export const useData = () => useContext(DataContext);
