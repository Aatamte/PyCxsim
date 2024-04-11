import React, { useEffect, useState } from 'react';
import { Box, Tabs, TabList, TabPanels, TabPanel, Tab } from '@chakra-ui/react';
import { useSearchParams } from 'react-router-dom';
import AgentsTab from "./pages/AgentPage";
import EnvironmentDisplay from "./pages/EnvironmentPage";
import ArtifactPage from "./pages/ArtifactPage";
import TablePage from "./pages/TablePage";

type SidebarProps = {
    sidebarWidth: number;
    setSidebarWidth: (width: number) => void;
};

const Sidebar: React.FC<SidebarProps> = ({ sidebarWidth, setSidebarWidth }) => {
    const [searchParams] = useSearchParams();
    const [tabIndex, setTabIndex] = useState(0);

    const tabIndexMap: { [key: string]: number } = {
            'environment': 0,
            'agents': 1,
            'artifacts': 2,
            'tables': 3
        };

    useEffect(() => {

        // Read the 'tab' query parameter from the URL
        const tabQueryParam = searchParams.get('tab');
        const newTabIndex = tabIndexMap[tabQueryParam as string];

        if (newTabIndex !== undefined) {
            setTabIndex(newTabIndex);
        }
    }, [searchParams, sidebarWidth]); // Include sidebarWidth in dependencies


    const handleTabsChange = (index: number) => {
        setTabIndex(index);
        // Update the URL query parameter to reflect the new tab
        const tabQueryParamValue = Object.keys(tabIndexMap).find(key => tabIndexMap[key] === index);
        searchParams.set('tab', tabQueryParamValue as string);
        const newRelativePathQuery = window.location.pathname + '?' + searchParams.toString();
        window.history.pushState(null, '', newRelativePathQuery);
    };

    return (
        <Box h="93vh" bg="#444" color="white" p="20px" overflow={"hidden"}>
            <Tabs
                variant="enclosed"
                isFitted
                orientation="horizontal"
                index={tabIndex}
                onChange={index => handleTabsChange(index)}
            >
                <TabList>
                    <Tab>Environment</Tab>
                    <Tab>Agents</Tab>
                    <Tab>Artifacts</Tab>
                    <Tab>Tables</Tab>
                </TabList>
                <TabPanels overflowY="hidden">
                    <TabPanel>
                        <EnvironmentDisplay />
                    </TabPanel>
                    <TabPanel>
                        <AgentsTab />
                    </TabPanel>
                    <TabPanel>
                        <ArtifactPage />
                    </TabPanel>
                    <TabPanel>
                        <TablePage />
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Box>
    );
};

export default Sidebar;


