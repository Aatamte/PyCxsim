// App.tsx
import React from 'react';
import { Box, Flex } from '@chakra-ui/react';
import TopBar from './components/topbar';
import Sidebar from './components/sidebar';
import World from './components/World'; // Import the World component
import {DataProvider} from "./components/DataProvider";

const App = () => {
  return (
      <DataProvider>
        <Box h="100vh" overflow="hidden">
          <TopBar />
          <Flex h=""> {/* Adjust for TopBar height */}
            <Flex direction="column" flex="2" overflow="hidden"> {/* Main content area and Control Panel */}
                <World />
            </Flex>
            <Box flex="1" bg="gray.200"> {/* Sidebar */}
              <Sidebar />
            </Box>
          </Flex>
        </Box>
      </DataProvider>
  );
};

export default App;

