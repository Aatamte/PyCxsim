import React, { useState } from "react";
import {Rect, Text, Group } from "react-konva";
import useWebSocketListener from "../../sockets/useWebSocketListener";

type gridProps = {
    xSize: number,
    ySize: number,
    cellSize: number,
    indexBoxSize: number
};

interface DataItem {
    position: string;
    color: string;
    content: string;
    is_passable: string;
    is_goal: string;
}

const Grid: React.FC<gridProps> = ({ xSize, ySize, cellSize, indexBoxSize}) => {
    const { data, error } = useWebSocketListener<DataItem[]>('cxgridworld');
    const [hoveredItem, setHoveredItem] = useState<DataItem | null>(null);

      const renderGridSquares = () => {
        if (!data) {
          return null;
        }

        const gridSquares = data.map((item) => {
          const [x, y] = item.position
            .replace(/[()]/g, "")
            .split(",")
            .map(Number);

          return (
            <Rect
              key={`grid-${x}-${y}`}
              x={x * cellSize + indexBoxSize}
              y={(ySize - 1 - y) * cellSize + indexBoxSize}
              width={cellSize}
              height={cellSize}
              fill={item.color}
              stroke="black"
              onMouseEnter={() => setHoveredItem(item)}
              onMouseLeave={() => setHoveredItem(null)}
            />
          );
        });

        return gridSquares;
      };

     const renderIndices = () => {
        const indices = [];
        // Render horizontal indices
        for (let i = 0; i < xSize; i++) {
          indices.push(
            <Rect
              key={`h-index-box-${i}`}
              x={i * cellSize + indexBoxSize}
              y={0}
              width={cellSize}
              height={indexBoxSize}
              fill="grey"
            />,
            <Text
              key={`h-index-text-${i}`}
              x={i * cellSize + indexBoxSize}
              y={indexBoxSize / 4}
              width={cellSize}
              text={`${i}`}
              fontSize={indexBoxSize / 2}
              fill="black"
              align="center"
            />
          );
        }
        // Render vertical indices
        for (let j = 0; j < ySize; j++) {
          indices.push(
            <Rect
              key={`v-index-box-${j}`}
              x={0}
              y={j * cellSize + indexBoxSize}
              width={indexBoxSize}
              height={cellSize}
              fill="grey"
            />,
            <Text
              key={`v-index-text-${j}`}
              x={0}
              y={j * cellSize + indexBoxSize + cellSize / 4}
              width={indexBoxSize}
              text={`${ySize - 1 - j}`}
              fontSize={indexBoxSize / 2}
              fill="black"
              align="center"
            />
          );
        }
        return indices;
      };

  const renderHoverBox = () => {
    const boxWidth = indexBoxSize * 10;
    const boxHeight = cellSize * 15;
    const boxX = -boxWidth - 10;
    const boxY = (ySize * cellSize) / 2 - boxHeight / 2;

    const contentText = hoveredItem ? hoveredItem.content : "Hover over a square";
    const fontSize = cellSize * 0.3;
    const textColor = "black";
    const textAlign = "center";
    const verticalAlign = "middle";

    const textX = boxX + boxWidth / 2;
    const textY = boxY + boxHeight / 2;

    return (
      <Group>
        <Rect
          x={boxX}
          y={boxY}
          width={boxWidth}
          height={boxHeight}
          fill="white"
          stroke="black"
          cornerRadius={5}
        />
        <Text
          x={textX}
          y={textY}
          text={contentText}
          fontSize={fontSize}
          fill={textColor}
          align={textAlign}
          verticalAlign={verticalAlign}
        />
      </Group>
    );
  };

    return (
        <>
            {renderGridSquares()}
            {renderIndices()}
            {renderHoverBox()}
        </>
    );
};

export default Grid;