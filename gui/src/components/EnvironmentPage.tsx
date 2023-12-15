
import React from 'react';
import { useData } from './DataProvider'; // Adjust the import path as necessary

const EnvironmentDisplay: React.FC = () => {
    const { state, handleReconnect } = useData();

    return (
        <div>
            <h1>Environment Information</h1>
            <div>
                <strong>Name:</strong> {state.environment.name}
            </div>
            <div>
                <strong>Status:</strong> {state.status}
            </div>
            <div>
                <strong>Current Episode:</strong> {state.environment.currentEpisode}
            </div>
            <div>
                <strong>Current Step:</strong> {state.environment.currentStep}
            </div>

            <div>
                <strong>Current Step:</strong> {state.environment.agentNames}
            </div>
            {/* Additional environment details here */}

            <button onClick={handleReconnect}>
                Reconnect WebSocket
            </button>
        </div>
    );
};

export default EnvironmentDisplay;
