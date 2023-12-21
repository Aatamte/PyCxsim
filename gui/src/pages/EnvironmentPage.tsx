
import React from 'react';
import {useData} from "../DataProvider";
import {
    CircularProgress,
    CircularProgressLabel,
    Divider,
    Text,
    VStack,
    Flex,
    Tabs,
    TabList,
    TabPanels,
    Tab,
    TabPanel,
    Box,
    Heading
} from "@chakra-ui/react";

const EnvironmentDisplay: React.FC = () => {
    const { state } = useData();

    return (
        <Box p={5}>
            {/* Header Section */}
            <Heading mb={4}>{state.environment.name}</Heading>

            {/* Tabs Section */}
            <Tabs isFitted variant="enclosed">
                <TabList mb={1}>
                    <Tab>Overview</Tab>
                    <Tab>Actions</Tab>
                </TabList>

                <TabPanels>
                    {/* Overview Panel */}
                    <TabPanel>
                        <VStack spacing={4} align="stretch">
                            {/* Environment Info */}
                            <Text fontSize="md">Agents: {state.environment.agentNames.join(', ')}</Text>
                            <Text fontSize="md">Grid Size: {state.environment.x_size} x {state.environment.y_size}</Text>
                            <Text fontSize="md">Artifacts: {state.environment.artifactNames.join(', ')}</Text>

                            {/* Episode Progress */}
                            <Flex align="center" justify="space-between">
                                <Text fontSize="md">Episode Progress</Text>
                                <CircularProgress value={(state.environment.currentEpisode / state.environment.maxEpisodes) * 100} color="green.400">
                                    <CircularProgressLabel>{`${state.environment.currentEpisode}/${state.environment.maxEpisodes}`}</CircularProgressLabel>
                                </CircularProgress>
                            </Flex>

                            <Divider my={4} />

                            {/* Step Progress */}
                            <Flex align="center" justify="space-between">
                                <Text fontSize="md">Step Progress</Text>
                                <CircularProgress value={(state.environment.currentStep / state.environment.maxSteps) * 100} color="blue.400">
                                    <CircularProgressLabel>{`${state.environment.currentStep}/${state.environment.maxSteps}`}</CircularProgressLabel>
                                </CircularProgress>
                            </Flex>
                        </VStack>
                    </TabPanel>

                    {/* Actions Panel */}
                    <TabPanel>
                        <Text fontSize="md">Actions content will go here.</Text>
                        {/* Add content related to actions here */}
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Box>
    );
};

export default EnvironmentDisplay;

