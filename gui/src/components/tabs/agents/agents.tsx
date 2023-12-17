import React, { useState } from 'react';
import { Tabs, TabList, TabPanels, Tab, TabPanel, Box, Select } from '@chakra-ui/react';
import MessagingBox from "./io/MessagingBox";
import {useData} from "../../DataProvider";

const AgentsTab: React.FC = () => {
    const { state, handleReconnect } = useData();
    const [selectedAgent, setSelectedAgent] = useState(state.environment.agentNames[0]);



    return (
        <Box p={0}>
            <Select
                placeholder="Select agent"
                mb={4}
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
                style={{ color: 'black' }} // Inline style for black text
            >
                {state.environment.agentNames.map((agent, index) => (
                    <option key={index} value={agent}>{agent}</option>
                ))}
            </Select>
            <Box
                borderWidth="1px"
                borderRadius="lg"
                p={0} // Increased padding
                borderColor="gray.200"
                w="full" // Set the width to full to use the full container width
                // Optionally set a specific width or max-width
                // maxWidth="800px"
                // height="500px" // Optionally set a specific height
            >
                <Tabs isFitted variant="enclosed">
                    <TabList mb="1em">
                        <Tab>I/O</Tab>
                        <Tab>Inventory</Tab>
                        <Tab>Actions</Tab>
                        <Tab>Parameters</Tab>
                    </TabList>
                    <TabPanels>
                        <TabPanel>
                            <MessagingBox selectedAgent={selectedAgent}/>
                        </TabPanel>
                    <TabPanel>
                        {selectedAgent && state.environment.agents[selectedAgent] ?
                            Object.entries(state.environment.agents[selectedAgent].inventory).map(([key, value]: [string, any], index: number) => (
                                <div key={index}>{`${key}: ${JSON.stringify(value)}`}</div>
                            ))
                            : <p>No agent selected or agent not found</p>
                        }
                    </TabPanel>
                        <TabPanel>
                            <p>Actions Content</p>
                            {/* Add your Actions content here */}
                        </TabPanel>
                        <TabPanel>
                            {selectedAgent && state.environment.agents[selectedAgent] ?
                            Object.entries(state.environment.agents[selectedAgent].parameters).map(([key, value]: [string, any], index: number) => (
                                <div key={index}>{`${key}: ${JSON.stringify(value)}`}</div>
                            ))
                            : <p>No agent selected or agent not found</p>
                        }
                        </TabPanel>
                    </TabPanels>
                </Tabs>
            </Box>
        </Box>
    );
};

export default AgentsTab;


