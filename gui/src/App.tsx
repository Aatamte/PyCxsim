// App.tsx
import React, {useState, useEffect} from 'react';
import { Grid, Box } from '@chakra-ui/react';
import TopBar from "./Topbar";
import Sidebar from "./Sidebar";
import World from "./pages/world/World";
import {DataProvider} from "./DataProvider";
import { Provider } from 'react-redux';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SettingsPage from "./pages/SettingsPage";
import LogsPage from "./pages/LogsPage";
import { ChakraProvider } from "@chakra-ui/react";
import customTheme from './theme'; // Import your custom theme
import SplitterLayout from 'react-splitter-layout';

import './css/CustomSplitterLayout.css'; // Path to your custom CSS file

import {store} from "./store";

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
  return (
      <ChakraProvider theme={customTheme}>
      <DataProvider>
          <Provider store={store}>
        <BrowserRouter>
          <div>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/settings" element={<SettingsPage />} />
                <Route path="/logs" element={<LogsPage />} />
            </Routes>
          </div>
        </BrowserRouter>
          </Provider>
      </DataProvider>
      </ChakraProvider>

  );
};

export default App;

