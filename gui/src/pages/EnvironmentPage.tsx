import React, { useEffect, useState, memo } from 'react';
import {
    Divider,
    Text,
    VStack,
    Tabs,
    TabList,
    TabPanels,
    Tab,
    TabPanel,
    Box,
    Heading
} from "@chakra-ui/react";

import useFetchWithInterval from "../useFetchWithInterval";

interface DataItem {
    key: string;
    value: string;
}

const EnvironmentDisplay: React.FC = memo(() => {
    const { data, error } = useFetchWithInterval<DataItem[]>('http://localhost:8000/tables/cxmetadata', 3000);

    const findValueByKey = (key: string): string => {
      if (!data) return 'Not available'; // Early return if data is not available

      const item = data.find(d => d.key === key);
      return item ? item.value : 'Not available'; // Gracefully handle undefined
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
                            <Divider my={4} />

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


