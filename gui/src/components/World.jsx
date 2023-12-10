// World.jsx
import React, { useState, useRef, useEffect } from 'react';
import { Box, IconButton, VStack, HStack } from '@chakra-ui/react';
import { Stage, Layer, Rect } from 'react-konva';
import { MdZoomIn, MdZoomOut, MdArrowBack, MdArrowForward, MdArrowUpward, MdArrowDownward } from 'react-icons/md';

const World = () => {
    const containerRef = useRef(null);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    const [scale, setScale] = useState(1);
    const [position, setPosition] = useState({ x: 0, y: 0 });

    useEffect(() => {
        if (containerRef.current) {
            const containerWidth = containerRef.current.offsetWidth;
            const containerHeight = containerRef.current.offsetHeight;
            setDimensions({
                width: containerWidth,
                height: containerHeight,
            });

            // Calculate initial position to center the grid both horizontally and vertically
            const gridSize = 10;
            const cellSize = containerWidth / gridSize;
            const gridWidth = gridSize * cellSize;
            const gridHeight = gridSize * cellSize;
            setPosition({
                x: (containerWidth - gridWidth) / 2,
                y: (containerHeight - gridHeight) / 2
            });
        }
    }, []);

    const gridSize = 10; // Size of the grid (10x10)
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
                </Layer>
            </Stage>
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




