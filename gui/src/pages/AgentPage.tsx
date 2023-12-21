import React, { useState } from 'react';
import { Tabs, TabList, TabPanels, Tab, TabPanel, Box, Select, Flex, Text} from '@chakra-ui/react';
import MessagingBox from "./AgentPageComponents/MessagingBox";
import {useData} from "../DataProvider";
import { useSearchParams } from 'react-router-dom';

import { Table, Thead, Tbody, Tr, Th, Td } from '@chakra-ui/react';

const InventoryTable = ({ inventory }: { inventory: { [key: string]: any } }) => {
    if (!inventory || Object.keys(inventory).length === 0) {
        return <Text>No items in inventory.</Text>;
    }

    return (
        <Box overflowX="auto">
            <Table variant="simple">
                <Thead>
                    <Tr>
                        <Th>Key</Th>
                        <Th>Value</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {Object.entries(inventory).map(([key, value], index) => (
                        <Tr key={index}>
                            <Td>{key}</Td>
                            <Td>{JSON.stringify(value)}</Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
        </Box>
    );
};

const AgentsTab: React.FC = () => {
    const { state } = useData();
    const [searchParams, setSearchParams] = useSearchParams();
    const [selectedAgent, setSelectedAgent] = useState(state.environment.agentNames[0] || '');

    const handleSelectAgent = (agentName: string) => {
        setSelectedAgent(agentName);
        // Update the search parameters to include both 'tab' and 'agent'
        searchParams.set('agent', encodeURIComponent(agentName));
        // Retain the tab parameter when selecting an agent
        searchParams.set('tab', 'agents');
        setSearchParams(searchParams);
    };
    return (
        <Box p={0}>
            <Flex align="center" mb={4}>
                <Text mr={2}>Agent:</Text>
                <Select
                    placeholder="Select agent"
                    value={selectedAgent}
                    onChange={(e) => handleSelectAgent(e.target.value)}
                    style={{ color: 'black' }} // Inline style for black text
                >
                    {state.environment.agentNames.map((agent, index) => (
                        <option key={index} value={agent}>{agent}</option>
                    ))}
                </Select>
            </Flex>
            <Box
                borderWidth="1px"
                borderRadius="lg"
                p={0} // Increased padding
                borderColor="gray.200"
                w="full" // Set the width to full to use the full container width
                // Optionally set a specific width or max-width
            >
                <Tabs isFitted variant="enclosed">
                    <TabList mb="1em">
                        <Tab>I/O</Tab>
                        <Tab>Inventory</Tab>
                        <Tab>Actions</Tab>
                        <Tab>Other</Tab>
                    </TabList>
                    <TabPanels
                        h="70vh" // Set a fixed height for the box
                        overflowY="auto" // Enable vertical scrolling
                        overflowX={'hidden'}
                    >
                        <TabPanel >
                            <MessagingBox selectedAgent={selectedAgent}/>
                        </TabPanel>
                            <TabPanel>
                                {selectedAgent && state.environment.agents[selectedAgent] ? (
                                    <InventoryTable inventory={state.environment.agents[selectedAgent].inventory} />
                                ) : (
                                    <Text>No agent selected or agent not found</Text>
                                )}
                            </TabPanel>
                        <TabPanel>
                            <p>Actions Content</p>
                            {/* Add your Actions content here */}
                        </TabPanel>
                        <TabPanel>
                            {selectedAgent && state.environment.agents[selectedAgent] ? (
                                <InventoryTable inventory={state.environment.agents[selectedAgent].parameters} />
                            ) : (
                                <Text>No agent selected or agent not found</Text>
                            )}
                        </TabPanel>
                    </TabPanels>
                </Tabs>
            </Box>
        </Box>
    );
};

export default AgentsTab;


