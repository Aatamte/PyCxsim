import React, {useEffect, memo } from 'react';
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

const EnvironmentDisplay: React.FC = memo(() => {
    const { environment } = useData();

    useEffect(() => {
        console.log("environment changed!")

    }, [environment]);

    return (
        <Box p={5}>
            {/* Header Section */}
            <Heading mb={4}>{environment.name}</Heading>

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
                            <Text fontSize="md">Agents: {environment.agentNames.join(', ')}</Text>
                            <Text fontSize="md">Grid Size: {environment.x_size} x {environment.y_size}</Text>
                            <Text fontSize="md">Artifacts: {environment.artifactNames.join(', ')}</Text>

                            {/* Episode Progress */}
                            <Flex align="center" justify="space-between">
                                <Text fontSize="md">Episode Progress</Text>
                                <CircularProgress value={(environment.currentEpisode / environment.maxEpisodes) * 100} color="green.400">
                                    <CircularProgressLabel>{`${environment.currentEpisode}/${environment.maxEpisodes}`}</CircularProgressLabel>
                                </CircularProgress>
                            </Flex>

                            <Divider my={4} />

                            {/* Step Progress */}
                            <Flex align="center" justify="space-between">
                                <Text fontSize="md">Step Progress</Text>
                                <CircularProgress value={(environment.currentStep / environment.maxSteps) * 100} color="blue.400">
                                    <CircularProgressLabel>{`${environment.currentStep}/${environment.maxSteps}`}</CircularProgressLabel>
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
});

export default EnvironmentDisplay;

