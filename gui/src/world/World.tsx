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
import {useData} from "../DataProvider";
import { useNavigate } from 'react-router-dom';
import { MdPanTool } from 'react-icons/md'; // Or any other appropriate icon
import {MdVisibility} from "react-icons/md";
import {MdVisibilityOff} from "react-icons/md";
import {MdLock} from "react-icons/md";

import InfoPanel from "./InfoPanel";
import Grid from "./GridPlane";
import AgentLayer from "./AgentLayer";
import useFetchWithInterval from "../useFetchWithInterval";

const DEFAULT_GRID_SIZE = 10;

type worldProps = {
    sidebarWidth: number;
};

interface DataItem {
    key: string;
    value: string;
}

const World: React.FC<worldProps> = ({ sidebarWidth }) => {
    const { data, error } = useFetchWithInterval<DataItem[]>('http://localhost:8000/tables/cxmetadata', 3000);

    const containerRef: RefObject<HTMLDivElement> = useRef(null);
    const mainContentRef: RefObject<HTMLDivElement> = useRef(null); // New ref for main content

    const [scale, setScale] = useState(1);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isPanning, setIsPanning] = useState(false);
    const navigate = useNavigate();

    const [showControls, setShowControls] = useState(false);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    const [isLocked, setIsLocked] = useState(false);
    const [cellSize, setCellSize] = useState(0); // New state for cell size

    const findValueByKey = (key: string): number => {
      if (!data) return 10; // Early return if data is not available

      const item = data.find(d => d.key === key);
      return item ? Number(item.value): 10; // Gracefully handle undefined
    };

    const gridSize = findValueByKey('x_size')
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
                   <AgentLayer cellSize={cellSize} navigate={navigate} />
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




