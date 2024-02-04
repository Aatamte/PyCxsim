import React, { createContext, useContext, useState, useEffect, ReactNode, useMemo } from 'react';
import Environment from './data_structures/Environment';
import SocketClient from "./websocket_client";
import SocketParams from "./data_structures/SocketParams";
import KVStorage from "./data_structures/kv_storage";
import Artifact from "./data_structures/artifact";
import Agent from "./data_structures/agent";

// Define the context shape
interface DataContextType {
  environment: Environment;
  socketParams: SocketParams;
  kv_storage: KVStorage<any>;
  sendData: (header: string, content: any) => void;
}

// Create the context with an initial default value
const DataContext = createContext<DataContextType>({
  environment: new Environment(),
  socketParams: new SocketParams(),
  kv_storage: new KVStorage<any>(),
  sendData: () => {}
});


export const DataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [environment, setEnvironment] = useState(new Environment());
  const [socketParams, setSocketParams] = useState(new SocketParams());
  const [kv_storage, setKVStorage] = useState(new KVStorage<any>());
  const [socket] = useState(new SocketClient());

    const onConnect = () => {
        sendData("server", "kv_storage");
    };

    const onClose = () => {
        setKVStorage(kv_storage.set("server_connection", "closed"));
        setEnvironment(environment.clear());
    };

    const updateAgent = (env: Environment, agentPairs: Record<string, any>) => {
        let updatedEnv = new Environment({ ...env });

        Object.entries(agentPairs).forEach(([agentName, agentObject]) => {
            let agent = new Agent();

            Object.entries(agentObject).forEach(([key, value]) => {
                agent.set(key, value);
            });
            updatedEnv = updatedEnv.addAgent(agent);
        });

        return updatedEnv; // Return the updated environment
    };

    const updateArtifact = (env: Environment, artifactPairs: Record<string, any>) => {
        let updatedEnv = new Environment({ ...env });

        Object.entries(artifactPairs).forEach(([artifactName, artifactObject]) => {
            let artifact = new Artifact(); // Assuming Artifact has a default constructor

            Object.entries(artifactObject).forEach(([key, value]) => {
                artifact.set(key, value); // Assuming Artifact has a 'set' method to update properties
            });

            updatedEnv = updatedEnv.addArtifact(artifact); // Update the environment with the new artifact
        });

        return updatedEnv; // Return the updated environment
    };

    const updateEnvironment = (env: Environment, environmentPairs: Record<string, any>) => {
        let updatedEnv = new Environment({ ...env });

        Object.entries(environmentPairs).forEach(([key, value]) => {
            updatedEnv = updatedEnv.set(key, value); // Update the environment with the new values
        });

        return updatedEnv; // Return the updated environment
    };

    // Method to handle kv_storage updates
    const handleKVStorage = (kvPairs: Record<string, any>) => {
        Object.entries(kvPairs).forEach(([key, value]) => {
            // Assuming kv_storage.set() updates the instance and returns it for chaining
            setKVStorage(kv_storage.set(key, value));
        });
    };

const onData = (msg: any) => {
    const { header, content } = msg;

    switch (header) {
        case "logs":
            // Handle logs if necessary
            break;
        case "kv_storage":
            handleKVStorage(content);
            break;
        case "agents":
            setEnvironment((prevEnv) => updateAgent(prevEnv, content));
            break;
        case "artifacts":
            setEnvironment((prevEnv) => updateArtifact(prevEnv, content));
            break;
        case "environment":
            setEnvironment((prevEnv) => updateEnvironment(prevEnv, content));
            break;
        default:
            console.log("Unhandled message type:", header);
            break;
    }
};

    useEffect(() => {
        // Define the callback functions
        const callbacks = {
            onConnect: onConnect,
            onDisconnect: onClose,
            onData: onData,
            onError: (error: any) => console.error("WebSocket error", error)
        };

        socket.connect(
            socketParams.host,
            socketParams.port,
            callbacks
        );

    }, []);

  const sendData = (header: string, content: any) => {
    const msg = { header, content, source: "GUI" };
    socket.send("data", msg);
  };

  return (
    <DataContext.Provider value={{ environment, kv_storage, socketParams, sendData }}>
      {children}
    </DataContext.Provider>
  );
};

export const useData = () => useContext(DataContext);
