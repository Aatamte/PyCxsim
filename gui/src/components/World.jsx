// World.jsx
import React, { useState, useRef, useEffect } from 'react';
import { Box, IconButton, VStack, HStack } from '@chakra-ui/react';
import { Text, Stage, Layer, Rect, Circle } from 'react-konva';
import { MdZoomIn, MdZoomOut, MdArrowBack, MdArrowForward, MdArrowUpward, MdArrowDownward } from 'react-icons/md';
import {useData} from "./DataProvider";
import { useNavigate } from 'react-router-dom';
import { MdPanTool } from 'react-icons/md'; // Or any other appropriate icon


const DEFAULT_GRID_SIZE = 10;


const World = () => {
    const { state, handleReconnect } = useData();
    const containerRef = useRef(null);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    const [scale, setScale] = useState(1);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isPanning, setIsPanning] = useState(false);
    const navigate = useNavigate();
    const gridSize = state.environment.x_size || DEFAULT_GRID_SIZE;

    const indexBoxSize = 20; // Size of the boxes for indices

    const handleWheel = (e) => {
        if (isPanning) {
            e.preventDefault();
            const scaleBy = 1.1;
            const newScale = e.deltaY < 0 ? scale * scaleBy : scale / scaleBy;
            setScale(newScale);
        }
    };

useEffect(() => {
    if (containerRef.current) {
        // Get the width of the sidebar, if it's dynamic you might need to manage this with state
        const sidebarWidth = 400 // Replace with the actual or state-managed width of your sidebar

        const containerWidth = containerRef.current.offsetWidth - sidebarWidth; // Adjust for sidebar
        const containerHeight = containerRef.current.offsetHeight;
        setDimensions({
            width: containerWidth,
            height: containerHeight,
        });

        const cellSize = Math.min(containerWidth / gridSize, containerHeight / gridSize);
        const gridWidth = gridSize * cellSize;
        const gridHeight = gridSize * cellSize;

        // Calculate the position to center the grid horizontally and vertically
        setPosition({
            x: (containerWidth / 2) - (gridWidth / 2),
            y: (containerHeight / 2) - (gridHeight / 2),
        });
    }
}, []); // The empty array means this effect will only run once when the component mounts




    const cellSize = dimensions.width / gridSize; // Cell size based on container width


    // Zoom and Pan functions
    const zoomIn = () => setScale(scale => scale * 1.2);
    const zoomOut = () => setScale(scale => scale / 1.2);
    const pan = (dx, dy) => setPosition(pos => ({ x: pos.x + dx, y: pos.y + dy }));

const renderGrid = () => {
    const grid = [];

    // Render the grid squares
    for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < gridSize; j++) {
            grid.push(
                <Rect
                    key={`grid-${i}-${j}`}
                    x={i * cellSize + indexBoxSize} // Adjust position to accommodate index boxes
                    y={j * cellSize + indexBoxSize}
                    width={cellSize}
                    height={cellSize}
                    fill="white"
                    stroke="black"
                />
            );
        }
    }

    // Render horizontal indices
    for (let i = 0; i < gridSize; i++) {
        grid.push(
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
        grid.push(
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

    return grid;
};

const renderAgents = () => {
    return Object.values(state.environment.agents).map((agent, index) => {
        const fontSize = 17; // Adjust font size as needed
        const textWidth = agent.name.length * fontSize * 0.6; // Rough estimate for text width
        const textHeight = fontSize; // Rough estimate for text height

        return (
            <React.Fragment key={`agent-${agent.name}`}>
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
                    offsetX={textWidth / 2} // Center the text horizontally based on its estimated width
                    offsetY={textHeight / 2} // Center the text vertically based on its estimated height
                />
            </React.Fragment>
        );
    });
};

    return (
        <Box
            bg="black"
            w="100%"
            h="100%"
            color="white"
            ref={containerRef}
            position="relative"
            cursor={isPanning ? 'grab' : 'default'}
              onWheel={handleWheel}
      //     onMouseDown={isPanning ? () => document.body.style.cursor = 'grabbing' : null}
       //     onMouseUp={isPanning ? () => document.body.style.cursor = 'grab' : null}
        >
            <Stage
                width={dimensions.width}
                height={dimensions.height}
                scaleX={scale}
                scaleY={scale}
                x={position.x}
                y={position.y}
                draggable={isPanning}
            >
                <Layer>
                    {renderGrid()}
                    {renderAgents()}
                </Layer>
            </Stage>
                       <VStack position="absolute" top="20px" left="20px" spacing="10px">
                <IconButton
                    icon={<MdPanTool />}
                    onClick={() => setIsPanning(!isPanning)}
                    colorScheme={isPanning ? "red" : "blue"}
                    aria-label="Pan Mode"
                    isActive={isPanning}
                    variant={isPanning ? 'solid' : 'outline'}
                />
            </VStack>
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




