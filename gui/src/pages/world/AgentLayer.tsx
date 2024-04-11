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
  ySize: number; // Add ySize prop
};


const AgentLayer: React.FC<AgentProps> = React.memo(({ cellSize, navigate, ySize }) => {
  const { data, error } = useWebSocketListener<AgentItem[]>('cxagents');

  const indexBoxSize = 20;

  const calculateFontSize = React.useMemo(() => (name: string, maxSize: number) => {
    const maxTextWidth = maxSize * 2;
    const fontSize = Math.min(maxSize, Math.floor(maxTextWidth / (name.length * 0.6)));
    return fontSize > 1 ? fontSize : 1;
  }, []);

  return (
    <>
      {data && data.map((agent) => {
        const maxFontSize = cellSize / 2;
        const fontSize = calculateFontSize(agent.name, maxFontSize);
        const textWidth = agent.name.length * fontSize * 0.6;

        const xPos = Number(agent.x_pos);
        const yPos = Number(agent.y_pos);

        const invertedYPos = ySize - 1 - yPos;

        return (
          <React.Fragment key={`agent-${agent.name}-${xPos}-${yPos}`}>
            <Circle
              x={(xPos * cellSize) + (cellSize / 2) + indexBoxSize}
              y={(invertedYPos * cellSize) + (cellSize / 2) + indexBoxSize}
              radius={cellSize / 2}
              fill="blue"
              onClick={() => navigate(`/?tab=agents&agent=${encodeURIComponent(agent.name)}`)}
              listening={false}
            />
            <Text
              x={(xPos * cellSize) + (cellSize / 2) + indexBoxSize - textWidth / 2}
              y={(invertedYPos * cellSize) + (cellSize / 2) + indexBoxSize - fontSize / 2}
              text={agent.name}
              fontSize={fontSize}
              fill="white"
              align="center"
              width={textWidth}
            />
          </React.Fragment>
        );
      })}
    </>
  );
});

export default AgentLayer;