// App.tsx
import React, {useState, useEffect} from 'react';
import { Grid, Box, Flex } from '@chakra-ui/react';
import TopBar from "./Topbar";
import Sidebar from "./Sidebar";
import World from "./world/World";
import {DataProvider} from "./DataProvider";
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import SettingsPage from "./pages/SettingsPage";
import LogsPage from "./pages/LogsPage";
import { ChakraProvider } from "@chakra-ui/react";
import customTheme from './theme'; // Import your custom theme
import SplitterLayout from 'react-splitter-layout';

import './css/CustomSplitterLayout.css'; // Path to your custom CSS file


const HomePage = () => {
    const initialSidebarPercentage = 50;
    const [sidebarWidth, setSidebarWidth] = useState(0); // Initialize with a default value

    // Handler for when the sidebar width changes
    const handleSidebarSizeChange = (newWidth: number) => {
        setSidebarWidth(newWidth);
    };

    return (
        <Grid templateRows="auto 1fr" h="100vh" overflow="hidden">
            <TopBar />
            <Box height={'93vh'} overflow="hidden">
            <SplitterLayout
                customClassName="custom-splitter"
                percentage={true}
                secondaryInitialSize={initialSidebarPercentage} // Example initial size in percentage
                onSecondaryPaneSizeChange={handleSidebarSizeChange}
            >
                <World sidebarWidth={sidebarWidth} />
                <Sidebar sidebarWidth={sidebarWidth} setSidebarWidth={setSidebarWidth} />
            </SplitterLayout>
            </Box>
        </Grid>
    );
};




const App = () => {
      useEffect(() => {
    // Log the full app (window) dimensions
    console.log('App Dimensions:', { width: window.innerWidth, height: window.innerHeight });
  }, []);

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

