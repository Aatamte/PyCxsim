import React, { useState } from 'react';
import { Tabs, TabList, TabPanels, Tab, TabPanel, Box, Select } from '@chakra-ui/react';
import MessagingBox from "./io/MessagingBox";

const AgentsTab: React.FC = () => {
    const agents = ["Agent 1", "Agent 2", "Agent 3"];
    const [selectedAgent, setSelectedAgent] = useState(agents[0]);

    return (
        <Box p={0}>
            <Select
                placeholder="Select agent"
                mb={4}
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
            >
                {agents.map((agent, index) => (
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
                            <MessagingBox></MessagingBox>
                        </TabPanel>
                        <TabPanel>
                            <p>Inventory Content</p>
                            {/* Add your Inventory content here */}
                        </TabPanel>
                        <TabPanel>
                            <p>Actions Content</p>
                            {/* Add your Actions content here */}
                        </TabPanel>
                        <TabPanel>
                            <p>Parameters Content</p>
                            {/* Add your Parameters content here */}
                        </TabPanel>
                    </TabPanels>
                </Tabs>
            </Box>
        </Box>
    );
};

export default AgentsTab;


