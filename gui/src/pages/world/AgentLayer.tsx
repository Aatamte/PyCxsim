import React from "react";
import { Circle, Text } from "react-konva";
import useWebSocketListener from "../../sockets/useWebSocketListener";


interface MessageProps {
  role: string;
  content: string;
  timestamp?: string; // Optional timestamp property
}

interface AgentItem {
  name: string;
  x_pos: number; // Ensuring x_pos and y_pos are numbers
  y_pos: number;
  parameters: Record<string, string>;
  inventory: Record<string, number>;
  messages: MessageProps[];
}

// Adjusted AgentProps to include the agents prop
type AgentProps = {
  cellSize: number;
  navigate: (path: string) => void;
};

const AgentLayer: React.FC<AgentProps> = ({ cellSize, navigate }) => {
  const { data, error } = useWebSocketListener<AgentItem[]>('cxagents');

  const indexBoxSize = 20;

  const calculateFontSize = (name: string, maxSize: number) => {
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
      {data && data.map((agent) => {
        const maxFontSize = cellSize / 2; // Maximum font size is half the cell size
        const fontSize = calculateFontSize(agent.name, maxFontSize);
        const textWidth = agent.name.length * fontSize * 0.6;

        // Casting x_pos and y_pos as numbers
        const xPos = Number(agent.x_pos);
        const yPos = Number(agent.y_pos);

        return (
          <React.Fragment key={`agent-${agent.name}-${xPos}-${yPos}`}>
            <Circle
              x={(xPos * cellSize) + (cellSize / 2) + indexBoxSize}
              y={(yPos * cellSize) + (cellSize / 2) + indexBoxSize}
              radius={cellSize / 2}
              fill="blue"
              onClick={() => navigate(`/?tab=agents&agent=${encodeURIComponent(agent.name)}`)}
            />
            <Text
              x={(xPos * cellSize) + (cellSize / 2) + indexBoxSize - textWidth / 2} // Adjust x to center the text
              y={(yPos * cellSize) + (cellSize / 2) + indexBoxSize - fontSize / 2} // Adjust y to center the text
              text={agent.name}
              fontSize={fontSize}
              fill="white"
              align="center"
              width={textWidth} // Set width to wrap text correctly
            />
          </React.Fragment>
        );
      })}
    </>
  );
};



const AgentLayer2: React.FC<AgentProps> = ({ cellSize, navigate }) => {
  const agents = [
    { name: "Agent1", x_pos: 100, y_pos: 100 },
    { name: "Agent2", x_pos: 200, y_pos: 200 },
  ];

  return (
    <>
      {agents.map((agent, index) => (
        <React.Fragment key={index}>
          <Circle
            x={agent.x_pos}
            y={agent.y_pos}
            radius={cellSize / 2}
            fill="blue"
          />
          <Text
            x={agent.x_pos}
            y={agent.y_pos}
            text={agent.name}
            fontSize={14}
            fill="white"
            align="center"
          />
        </React.Fragment>
      ))}
    </>
  );
};

export default AgentLayer;
