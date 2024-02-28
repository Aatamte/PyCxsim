import React, { useEffect, useState, memo } from 'react';
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
import axios from "axios";


interface DataItem {
    key: string;
    value: string;
}

const EnvironmentDisplay: React.FC = memo(() => {
    const [data, setData] = useState<DataItem[]>([]);


    const fetchData = async () => {
        console.log("fetching data");
        try {
            // Replace with your API endpoint
            const response = await axios.get('http://localhost:8000/tables/cxmetadata');
            console.log(response);
            setData(response.data); // Assuming the API returns an array of dictionaries
        } catch (err) {
            console.log("err", err);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const findValueByKey = (key: string): string => {
        const item = data.find(d => d.key === key);
        return item ? item.value : 'Not available';
    };

    return (
        <Box p={5}>
            {/* Header Section */}
            <Heading mb={4}>{findValueByKey('name')}</Heading>

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
                            {/* Dynamically rendered environment info based on the API response */}
                            <Text fontSize="md">Agents: {findValueByKey('agentNames')}</Text>
                            <Text fontSize="md">Grid Size: {findValueByKey('x_size')} x {findValueByKey('y_size')}</Text>
                            <Text fontSize="md">Artifacts: {findValueByKey('artifactNames')}</Text>

                            {/* Episode Progress */}
                            <Flex align="center" justify="space-between">
                                <Text fontSize="md">Episode Progress</Text>
                                <CircularProgress value={parseInt(findValueByKey('currentEpisode')) / parseInt(findValueByKey('maxEpisodes')) * 100} color="green.400">
                                    <CircularProgressLabel>{`${findValueByKey('currentEpisode')}/${findValueByKey('maxEpisodes')}`}</CircularProgressLabel>
                                </CircularProgress>
                            </Flex>

                            <Divider my={4} />

                            {/* Step Progress */}
                            <Flex align="center" justify="space-between">
                                <Text fontSize="md">Step Progress</Text>
                                <CircularProgress value={parseInt(findValueByKey('currentStep')) / parseInt(findValueByKey('maxSteps')) * 100} color="blue.400">
                                    <CircularProgressLabel>{`${findValueByKey('currentStep')}/${findValueByKey('maxSteps')}`}</CircularProgressLabel>
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


