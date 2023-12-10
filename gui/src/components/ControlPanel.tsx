// ControlPanel.jsx
import React from 'react';
import {
  Box, Flex, IconButton, VStack, Text, CircularProgress, CircularProgressLabel, Divider
} from '@chakra-ui/react';
import { MdPlayArrow, MdPause, MdSkipNext, MdSkipPrevious } from 'react-icons/md';
import TurnAnimation from "./TurnAnimation";

const ControlPanel = () => {
  // Replace with actual data and functionality
  const currentStep = 5;
  const maxSteps = 10;
  const currentEpisode = 2;
  const maxEpisodes = 5;

  // Calculate progress as a percentage
  const stepProgress = (currentStep / maxSteps) * 100;
  const episodeProgress = (currentEpisode / maxEpisodes) * 100;

  return (
    <Box h="10vh" bg="gray.100" p="20px">
      <Flex justify="space-between" align="center" h="100%">
        <VStack spacing={4} width="200px"> {/* Fixed width */}
          <Text fontSize="sm">Episode Progress</Text>
          <CircularProgress value={episodeProgress} color="green.400">
            <CircularProgressLabel>{`${currentEpisode}/${maxEpisodes}`}</CircularProgressLabel>
          </CircularProgress>
        </VStack>

        <Divider orientation="vertical" />

        <VStack spacing={4} width="200px"> {/* Fixed width */}
          <Text fontSize="sm">Step Progress</Text>
          <CircularProgress value={stepProgress} color="blue.400">
            <CircularProgressLabel>{`${currentStep}/${maxSteps}`}</CircularProgressLabel>
          </CircularProgress>
        </VStack>

        <Divider orientation="vertical" />

        <VStack spacing={2}>
          <Text fontSize="sm" mb="2">Simulation Status</Text>
          <Flex>
            <IconButton icon={<MdPlayArrow />} size="lg" aria-label="Play" m="2" />
            <IconButton icon={<MdPause />} size="lg" aria-label="Pause" m="2" />
            <IconButton icon={<MdSkipNext />} size="lg" aria-label="Next Step" m="2" />
            <IconButton icon={<MdSkipPrevious />} size="lg" aria-label="Last Step" m="2" />
          </Flex>
        </VStack>

        <Divider orientation="vertical" />

        <Box flex="1" pl="4">
          <TurnAnimation />
        </Box>
      </Flex>
    </Box>
  );
};

export default ControlPanel;







