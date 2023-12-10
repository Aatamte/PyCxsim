import React from 'react';
import { Box, Tabs, TabList, TabPanels, TabPanel, Tab } from '@chakra-ui/react';
import MessagingBox from "./agents/io/MessagingBox";

const Sidebar: React.FC = () => {
    return (
        <Box h="90vh" bg="#444" color="white" p="20px">
            <Tabs variant="enclosed" isFitted orientation="horizontal">
                <TabList>
                    <Tab>Environment</Tab>
                    <Tab>Agents</Tab>
                    <Tab>Artifact</Tab>
                    <Tab>Settings</Tab>
                    <Tab>Logs</Tab>
                </TabList>
                <TabPanels>
                    <TabPanel>
                        <p>Environment content</p>
                    </TabPanel>
                    <TabPanel>
                        <MessagingBox />
                    </TabPanel>
                    <TabPanel>
                        <p>Artifact content</p>
                    </TabPanel>
                    <TabPanel>
                        <p>Settings content</p>
                    </TabPanel>
                    <TabPanel>
                        <p>Logs content</p>
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Box>
    );
};

export default Sidebar;
