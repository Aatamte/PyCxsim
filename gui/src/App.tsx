// App.tsx
import React, {useState, useEffect} from 'react';
import { Box, Flex } from '@chakra-ui/react';
import TopBar from './components/topbar';
import Sidebar from './components/sidebar';
import World from './components/World'; // Import the World component
import {DataProvider} from "./components/DataProvider";
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import SettingsPage from "./components/SettingsPage";
import LogsPage from "./components/LogsPage";
import { ChakraProvider } from "@chakra-ui/react";
import customTheme from './theme'; // Import your custom theme

import 'react-resizable/css/styles.css';

const HomePage = () => {
    const [sidebarWidth, setSidebarWidth] = useState(0); // Initialize with 0

    useEffect(() => {
        // Set the initial sidebar width to be 40% of the screen width
        setSidebarWidth(window.innerWidth * 0.4);
    }, []); // Empty dependency array ensures this runs only once after initial render

    // ... rest of your component logic ...
    const [isResizing, setIsResizing] = useState(false);

    const handleMouseDown = (e: any) => {
        e.preventDefault();
        setIsResizing(true);
    };

    const handleMouseMove = (e: any) => {
        if (isResizing) {
            // Calculate new width based on the mouse position
            const newWidth = window.innerWidth - e.clientX;
            setSidebarWidth(newWidth);
        }
    };

    const handleMouseUp = () => {
        setIsResizing(false);
    };

    return (
        <Box h="100vh" overflow="hidden" onMouseMove={handleMouseMove} onMouseUp={handleMouseUp}>
            <TopBar />
            <Flex>
                <Box flex="1" overflow="auto">
                    <World />
                </Box>
                <Box
                    width={`${sidebarWidth}px`}
                    bg="white.200"
                    overflow="auto"
                    position="relative"
                >
                    <Box
                        width="5px"
                        cursor="ew-resize"
                        bg="white.400"
                        onMouseDown={handleMouseDown}
                        position="absolute"
                        left="0"
                        top="0"
                        bottom="0"
                    />
                    <Sidebar />
                </Box>
            </Flex>
        </Box>
    );
};


const App = () => {
  return (
      <ChakraProvider theme={customTheme}>
      <DataProvider>
        <BrowserRouter>
          <div>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/settings" element={<SettingsPage />} />
                <Route path="/logs" element={<LogsPage />} />
            </Routes>
          </div>
        </BrowserRouter>
      </DataProvider>
      </ChakraProvider>
  );
};

export default App;

