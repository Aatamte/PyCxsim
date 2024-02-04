import React from "react";
import {Rect, Text} from "react-konva";

type gridProps = {
    gridSize: number,
    cellSize: number,
    indexBoxSize: number
};


const Grid: React.FC<gridProps> = ({ gridSize, cellSize, indexBoxSize}) => {
    const renderGridSquares = () => {
        const gridSquares = [];
        for (let i = 0; i < gridSize; i++) {
            for (let j = 0; j < gridSize; j++) {
                gridSquares.push(
                    <Rect
                        key={`grid-${i}-${j}`}
                        x={i * cellSize + indexBoxSize}
                        y={j * cellSize + indexBoxSize}
                        width={cellSize}
                        height={cellSize}
                        fill="white"
                        stroke="black"
                    />
                );
            }
        }
        return gridSquares;
    };

    const renderIndices = () => {
        const indices = [];
        // Render horizontal indices
        for (let i = 0; i < gridSize; i++) {
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
        for (let j = 0; j < gridSize; j++) {
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
                    text={`${j}`}
                    fontSize={indexBoxSize / 2}
                    fill="black"
                    align="center"
                />
            );
        }
        return indices;
    };

    return (
        <>
            {renderGridSquares()}
            {renderIndices()}
        </>
    );
};

export default Grid;