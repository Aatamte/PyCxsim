// World.jsx
import React, { useState, useRef, useEffect, RefObject, useLayoutEffect } from 'react';
import {
    Box,
    IconButton,
    VStack,
    HStack,
    Text as CText,
    Flex,
    CircularProgress,
    CircularProgressLabel, Divider
} from '@chakra-ui/react';
import { Text, Stage, Layer, Rect, Circle } from 'react-konva';
import {
    MdZoomIn,
    MdZoomOut,
    MdArrowBack,
    MdArrowForward,
    MdArrowUpward,
    MdArrowDownward,
    MdLockOpen, MdSkipPrevious, MdPause, MdPlayArrow, MdSkipNext
} from 'react-icons/md';
import {useData} from "./DataProvider";
import { useNavigate } from 'react-router-dom';
import { MdPanTool } from 'react-icons/md'; // Or any other appropriate icon
import {MdVisibility} from "react-icons/md";
import {MdVisibilityOff} from "react-icons/md";
import {MdLock} from "react-icons/md";

const DEFAULT_GRID_SIZE = 10;


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



type agentProps = {
    agents: Record<any, any>,
    cellSize: number,
    navigate: any
};

const Agents: React.FC<agentProps> = ({ agents, cellSize, navigate }) => {
    const indexBoxSize = 20;

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
            {Object.values(agents).map((agent) => {
                const maxFontSize = cellSize / 2; // Maximum font size is half the cell size
                const fontSize = calculateFontSize(agent.name, maxFontSize);
                const textWidth = agent.name.length * fontSize * 0.6;

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
                            offsetX={textWidth / 2} // Center the text horizontally
                            offsetY={fontSize / 2} // Center the text vertically
                        />
                    </React.Fragment>
                );
            })}
        </>
    );
};


type InfoPanelProps = {
    sidebarWidth: number;
};

const InfoPanel: React.FC<InfoPanelProps> = ({ sidebarWidth }) => {
    const { state, sendData } = useData();

    const sendButtonAction = (action: string) => {
        sendData("action", action);
    };

    return (
        <Flex bg="gray" h="10vh" justifyContent="space-around" alignItems="center" px={4} boxShadow="0px 2px 4px rgba(0, 0, 0, 0.1)">
            <HStack spacing={4} align="center">
                {/* Episode Progress */}
                <VStack spacing={0}>
                    <CText fontSize="lg" fontWeight="bold">Episode</CText>
                    <CircularProgress value={(state.environment.currentEpisode / state.environment.maxEpisodes) * 100} color="green.400" thickness="12px">
                        <CircularProgressLabel>{`${state.environment.currentEpisode}/${state.environment.maxEpisodes}`}</CircularProgressLabel>
                    </CircularProgress>
                </VStack>

                {/* Step Progress */}
                <VStack spacing={0}>
                    <CText fontSize="lg" fontWeight="bold">Step</CText>
                    <CircularProgress value={((state.environment.currentStep + 1) / state.environment.maxSteps) * 100} color="blue.400" thickness="12px">
                        <CircularProgressLabel>{`${state.environment.currentStep + 1}/${state.environment.maxSteps}`}</CircularProgressLabel>
                    </CircularProgress>
                </VStack>
            </HStack>

            <Divider orientation="vertical" height="5vh" />

            {/* Control Buttons */}
            <HStack spacing={2}>
                <IconButton icon={<MdSkipPrevious />} size="lg" aria-label="Last Step" onClick={() => sendButtonAction('back')} isDisabled={true}/>
                <IconButton icon={<MdPause />} size="lg" aria-label="Pause" onClick={() => sendButtonAction('pause')} />
                <IconButton icon={<MdPlayArrow />} size="lg" aria-label="Play" onClick={() => sendButtonAction('play')} isDisabled={true}/>
                <IconButton icon={<MdSkipNext />} size="lg" aria-label="Next Step" onClick={() => sendButtonAction('next')} />
            </HStack>

            <Divider orientation="vertical" height="5vh" />

            {/* Status Placeholder */}
            <VStack spacing={0} align="center">
                <CText fontSize="md">{state.environment.status}</CText>
                <CText fontSize="md">Next Agent: {state.environment.agentQueue?.at(0)}</CText>

            </VStack>
        </Flex>
    );
};

type worldProps = {
    sidebarWidth: number;
};


const World: React.FC<worldProps> = ({ sidebarWidth }) => {
    const { state, handleReconnect } = useData();

    const containerRef: RefObject<HTMLDivElement> = useRef(null);
    const mainContentRef: RefObject<HTMLDivElement> = useRef(null); // New ref for main content

    const [scale, setScale] = useState(1);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isPanning, setIsPanning] = useState(false);
    const navigate = useNavigate();
    const gridSize = state.environment.x_size || DEFAULT_GRID_SIZE;
    const [showControls, setShowControls] = useState(false);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    const [isLocked, setIsLocked] = useState(false);
    const [cellSize, setCellSize] = useState(0); // New state for cell size

    const indexBoxSize = 20; // Size of the boxes for indices
    const extraRows = 2; // Extra rows for spacing
    const effectiveGridSize = gridSize + extraRows;

    const updateCellSize = (containerWidth: number, containerHeight: number) => {
        if (!isLocked) {
            const newCellSize = Math.min(containerWidth / effectiveGridSize, containerHeight / effectiveGridSize);
            setCellSize(newCellSize);

            // Update position to center the grid with extra spacing
            setPosition({
                x: (containerWidth - newCellSize * gridSize) / 2,
                y: (containerHeight - newCellSize * gridSize) / 2,
            });
        }
    };

    const updateDimensions = () => {
        if (mainContentRef.current) {
            // Adjust the height calculation for the main content area
            const offsetWidth = mainContentRef.current.offsetWidth;
            const offsetHeight = mainContentRef.current.offsetHeight
            const newDimensions = { width: offsetWidth, height: offsetHeight };
            setDimensions(newDimensions);
            updateCellSize(offsetWidth, offsetHeight);
        }
    };

    useLayoutEffect(() => {
        updateDimensions();
        window.addEventListener('resize', updateDimensions);
        return () => window.removeEventListener('resize', updateDimensions);
    }, [sidebarWidth]); // Depend on sidebarWidth if its size impacts the component


    const handleWheel = (e: any) => {
        if (isPanning) {
            e.preventDefault();
            const scaleBy = 1.1;
            const newScale = e.deltaY < 0 ? scale * scaleBy : scale / scaleBy;
            setScale(newScale);
        }
    };

    useEffect(() => {
        if (mainContentRef.current) {
            const { offsetWidth, offsetHeight } = mainContentRef.current;
            updateCellSize(offsetWidth, offsetHeight);
        }
    }, [gridSize, sidebarWidth, isLocked, mainContentRef]); // Add isLocked as a dependency

    // Zoom and Pan functions
    const zoomIn = () => setScale(scale => scale * 1.2);
    const zoomOut = () => setScale(scale => scale / 1.2);
    const pan = (dx: number, dy: number) => setPosition(pos => ({ x: pos.x + dx, y: pos.y + dy }));

    const AgentContent = () => {
        return <Agents agents={state.environment.agents} cellSize={cellSize} navigate={navigate} />
    }

    useEffect(() => {

    }, [state]);

    const mainContent = () => {
        return (
            <Box
            bg="black"
            h="83vh"
            color="white"
            ref={mainContentRef}
            cursor={isPanning ? 'grab' : 'default'}
            onWheel={handleWheel}
            overflow={'hidden'}
            position="relative"  // Set position relative for control buttons
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
                    <Grid gridSize={gridSize} cellSize={cellSize} indexBoxSize={indexBoxSize}/>
                   {AgentContent()}
                </Layer>
            </Stage>
            <IconButton
                icon={showControls ? <MdVisibilityOff /> : <MdVisibility />}
                onClick={() => setShowControls(!showControls)}
                colorScheme="blue"
                aria-label="Toggle Controls"
                position="absolute"
                top="20px"
                right="20px"
            />
            {showControls && (
                <VStack position="absolute" top="20px" right="280px" spacing="10px">
                    <HStack
            position="absolute"
            spacing="10px"
            boxShadow="0px 0px 10px rgba(0, 0, 0, 0.1)" // Optional shadow for depth
        >
            {/* Zoom Buttons */}
            <IconButton icon={<MdZoomOut />} onClick={zoomOut} aria-label="Zoom Out" />
            <IconButton icon={<MdZoomIn />} onClick={zoomIn} aria-label="Zoom In" />

            {/* Directional Pan Buttons */}
            <IconButton icon={<MdArrowForward />} onClick={() => pan(-50, 0)} aria-label="Pan Right"  />
            <IconButton icon={<MdArrowDownward />} onClick={() => pan(0, -50)} aria-label="Pan Down" />
            <IconButton icon={<MdArrowBack />} onClick={() => pan(50, 0)} aria-label="Pan Left" />
            <IconButton icon={<MdArrowUpward />} onClick={() => pan(0, 50)} aria-label="Pan Up" />

            <IconButton
                aria-label="Lock"
            icon={isLocked ? <MdLock /> : <MdLockOpen />} // Example icons for lock state
            onClick={() => setIsLocked(!isLocked)}
        />

            {/* Pan Tool Button */}
            <IconButton
                icon={<MdPanTool />}
                onClick={() => setIsPanning(!isPanning)}
                colorScheme={isPanning ? "red" : "blue"}
                aria-label="Pan Mode"
                isActive={isPanning}
                variant={isPanning ? 'solid' : 'outline'}
            />
        </HStack>
                </VStack>
            )}
        </Box>
        );
    }

    return (
        <Box
            bg="black"
            h="93vh"
            color="white"
            ref={containerRef}
            cursor={isPanning ? 'grab' : 'default'}
            onWheel={handleWheel}
            overflow={'hidden'}
        >
            {mainContent()}
            <InfoPanel sidebarWidth={sidebarWidth} />

        </Box>
    );
};

export default World;




