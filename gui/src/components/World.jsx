// World.jsx
import React, { useState, useRef, useEffect } from 'react';
import { Box, IconButton, VStack, HStack } from '@chakra-ui/react';
import { Text, Stage, Layer, Rect, Circle } from 'react-konva';
import { MdZoomIn, MdZoomOut, MdArrowBack, MdArrowForward, MdArrowUpward, MdArrowDownward } from 'react-icons/md';
import {useData} from "./DataProvider";

const DEFAULT_GRID_SIZE = 10;


const World = () => {
    const { state, handleReconnect } = useData();
    const containerRef = useRef(null);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    const [scale, setScale] = useState(0.75);
    const [position, setPosition] = useState({ x: 0, y: 0 });

    const gridSize = state.environment.x_size || DEFAULT_GRID_SIZE;

    useEffect(() => {
        if (containerRef.current) {
            // ... existing useEffect code ...
        }
    }, [containerRef, gridSize]); // Add gridSize as a dependency


    useEffect(() => {
        if (containerRef.current) {
            const containerWidth = containerRef.current.offsetWidth;
            const containerHeight = containerRef.current.offsetHeight;
            setDimensions({
                width: containerWidth,
                height: containerHeight,
            });

            const cellSize = Math.min(containerWidth, containerHeight) / gridSize; // Use the smaller dimension for square cells
            const gridWidth = gridSize * cellSize;
            const gridHeight = gridSize * cellSize;
            setPosition({
                x: (containerWidth - gridWidth) / 2,
                y: (containerHeight - gridHeight) / 2
            });
        }
    }, []);


    const cellSize = dimensions.width / gridSize; // Cell size based on container width


    // Zoom and Pan functions
    const zoomIn = () => setScale(scale => scale * 1.2);
    const zoomOut = () => setScale(scale => scale / 1.2);
    const pan = (dx, dy) => setPosition(pos => ({ x: pos.x + dx, y: pos.y + dy }));

    const renderGrid = () => {
        const grid = [];
        for (let i = 0; i < gridSize; i++) {
            for (let j = 0; j < gridSize; j++) {
                grid.push(
                    <Rect
                        key={`${i}-${j}`}
                        x={i * cellSize}
                        y={j * cellSize}
                        width={cellSize}
                        height={cellSize}
                        fill="white"
                        stroke="black"
                    />
                );
            }
        }
        return grid;
    };

    const renderAgents = () => {
        console.log(state.environment.agents)
        return Object.values(state.environment.agents).map((agent, index) => (
            <React.Fragment key={`agent-${agent.name}`}>
                <Circle
                    x={(agent.x_pos * cellSize) + (cellSize / 2)}
                    y={(agent.y_pos * cellSize) + (cellSize / 2)}
                    radius={cellSize / 2}
                    fill="blue"
                />
                <Text
                    x={(agent.x_pos * cellSize) + (cellSize / 2)}
                    y={(agent.y_pos * cellSize) + (cellSize / 2)}
                    text={agent.name}
                    fontSize={12} // Adjust font size as needed
                    fill="white" // Text color
                    align="center"
                    verticalAlign="middle"
                    offsetX={(cellSize / 2)} // Center the text horizontally
                    offsetY={(cellSize / 2)} // Center the text vertically
                />
            </React.Fragment>
        ));
    };

    return (
        <Box bg="black" w="100%" h="100%" color="white" ref={containerRef} position="relative">
            <Stage
                width={dimensions.width}
                height={dimensions.height}
                scaleX={scale}
                scaleY={scale}
                x={position.x}
                y={position.y}
            >
                <Layer>
                    {renderGrid()}
                    {renderAgents()}
                </Layer>
            </Stage>
            {/* Pan and Zoom Buttons */}
            <VStack position="absolute" bottom="20px" left="20px" spacing="10px">
                <IconButton icon={<MdArrowUpward />} onClick={() => pan(0, 50)} colorScheme="blue" aria-label="Pan Up" />
                <HStack spacing="10px">
                    <IconButton icon={<MdArrowBack />} onClick={() => pan(50, 0)} colorScheme="blue" aria-label="Pan Left" />
                    <IconButton icon={<MdArrowDownward />} onClick={() => pan(0, -50)} colorScheme="blue" aria-label="Pan Down" />
                    <IconButton icon={<MdArrowForward />} onClick={() => pan(-50, 0)} colorScheme="blue" aria-label="Pan Right" />
                </HStack>
            </VStack>
            <VStack position="absolute" bottom="20px" right="20px" spacing="10px">
                <IconButton icon={<MdZoomIn />} onClick={zoomIn} colorScheme="blue" aria-label="Zoom In" />
                <IconButton icon={<MdZoomOut />} onClick={zoomOut} colorScheme="blue" aria-label="Zoom Out" />
            </VStack>
        </Box>
    );
};

export default World;




