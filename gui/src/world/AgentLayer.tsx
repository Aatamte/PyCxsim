import React, {useEffect} from "react";
import {Circle, Text} from "react-konva";
import {useData} from "../DataProvider";

type agentProps = {
    agents: Record<any, any>,
    cellSize: number,
    navigate: any
};


const AgentLayer: React.FC<agentProps> = ({ agents, cellSize, navigate }) => {
    const { environment } = useData();
    const indexBoxSize = 20;

    useEffect(() => {
        console.log("updated state!!!!")

    }, [environment]);

    const calculateFontSize = (name: any, maxSize: number) => {
        let fontSize = maxSize;
        const maxTextWidth = maxSize * 2; // Maximum text width is the diameter of the circle

        // Reduce the font size until the text fits within the circle
        while (name.length * fontSize * 0.6 > maxTextWidth && fontSize > 1) {
            fontSize -= 1; // Decrease font size
        }

        return fontSize;
    };


    return (
        <>
            {Object.values(environment.agents).map((agent) => {
                const maxFontSize = cellSize / 2; // Maximum font size is half the cell size
                const fontSize = calculateFontSize(agent.name, maxFontSize);
                const textWidth = agent.name.length * fontSize * 0.6;

                return (
                    <React.Fragment key={`agent-${agent.name}-${agent.x_pos}-${agent.y_pos}`}>
                        <Circle
                            x={(agent.x_pos * cellSize) + (cellSize / 2) + indexBoxSize}
                            y={(agent.y_pos * cellSize) + (cellSize / 2) + indexBoxSize}
                            radius={cellSize / 2}
                            fill="blue"
                            onClick={() => navigate(`/?tab=agents?agent=${encodeURIComponent(agent.name)}`)}
                        />
                        <Text
                            x={(agent.x_pos * cellSize) + (cellSize / 2) + indexBoxSize}
                            y={(agent.y_pos * cellSize) + (cellSize / 2) + indexBoxSize}
                            text={agent.name}
                            fontSize={fontSize}
                            fill="white"
                            align="center"
                            verticalAlign="middle"
                            offsetX={textWidth / 2} // Center the text horizontally
                            offsetY={fontSize / 2} // Center the text vertically
                        />
                    </React.Fragment>
                );
            })}
        </>
    );
};

export default AgentLayer;