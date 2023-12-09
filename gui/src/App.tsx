// App.tsx
import React from 'react';
import { Box, Flex, Grid, GridItem } from '@chakra-ui/react';
import TopBar from './components/topbar';
import Sidebar from './components/sidebar';

const App = () => {
  return (
    <Box>
      <TopBar />
      <Flex h="calc(100vh - 60px)"> {/* Adjust the height based on TopBar's height */}
        <Box w="250px" bg="gray.200"> {/* Sidebar Width */}
          <Sidebar />
        </Box>
        <Box flex="1" overflow="hidden">

        </Box>
      </Flex>
    </Box>
  );
};

export default App;

