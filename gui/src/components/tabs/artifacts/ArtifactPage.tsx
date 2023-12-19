

import React, { useState } from 'react';
import {Tabs, TabList, TabPanels, Tab, TabPanel, Box, Select, Flex, Text} from '@chakra-ui/react';
import {useData} from "../../DataProvider";
import {  Table, Thead, Tr, Th, Tbody, Td } from '@chakra-ui/react';


const ArtifactPage: React.FC = () => {
    const { state, handleReconnect } = useData();
    const [selectedArtifact, setSelectedArtifact] = useState(state.environment.artifactNames[0]);

    const getArtifactProperties = () => {
        console.log(state.environment.agents)
        console.log(state.environment.artifacts)
        const artifact = state.environment.artifacts[selectedArtifact];
        return artifact ? Object.entries(artifact) : [];
    };

    return (
        <Box p={0}>
            <Flex align="center" mb={4}>
                <Text mr={2}>Artifact:</Text>
                <Select
                    placeholder="Select artifact"
                    value={selectedArtifact}
                    onChange={(e) => setSelectedArtifact(e.target.value)}
                    style={{ color: 'black' }} // Inline style for black text
                >
                    {state.environment.artifactNames.map((agent, index) => (
                        <option key={index} value={agent}>{agent}</option>
                    ))}
                </Select>
            </Flex>
              <Box
                borderWidth="1px"
                borderRadius="lg"
                p={0}
                borderColor="gray.200"
                w="full"
            >
                <Tabs isFitted variant="enclosed">
                    <TabList mb="1em">
                        <Tab>Overview</Tab>
                        <Tab>Actions</Tab>
                    </TabList>
                    <TabPanel>
                        {selectedArtifact ? (
                            <Table variant="simple">
                                <Thead>
                                    <Tr>
                                        <Th>Key</Th>
                                        <Th>Value</Th>
                                    </Tr>
                                </Thead>
                                <Tbody>
                                    {getArtifactProperties().map(([key, value], index) => (
                                        <Tr key={index}>
                                            <Td>{key}</Td>
                                            <Td>{JSON.stringify(value)}</Td>
                                        </Tr>
                                    ))}
                                </Tbody>
                            </Table>
                        ) : (
                            <Text>No artifact selected or artifact not found</Text>
                        )}
                    </TabPanel>
                </Tabs>
            </Box>
        </Box>
    );
};

export default ArtifactPage;