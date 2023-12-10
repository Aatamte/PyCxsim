// App.tsx
import React from 'react';
import { Box, Flex } from '@chakra-ui/react';
import TopBar from './components/topbar';
import Sidebar from './components/sidebar';
import ControlPanel from "./components/ControlPanel";
import World from './components/World'; // Import the World component

const App = () => {
  return (
    <Box h="100vh" overflow="hidden">
      <TopBar />
      <Flex h=""> {/* Adjust for TopBar height */}
        <Flex direction="column" flex="2" overflow="hidden"> {/* Main content area and Control Panel */}
            <World />
          <ControlPanel /> {/* Control Panel taking up a fixed portion of the height */}
        </Flex>
        <Box flex="1" bg="gray.200"> {/* Sidebar */}
          <Sidebar />
        </Box>
      </Flex>
    </Box>
  );
};

export default App;

