import React, { useEffect, useState } from 'react';
import { Box, Tabs, TabList, TabPanels, TabPanel, Tab } from '@chakra-ui/react';
import { useSearchParams } from 'react-router-dom';
import AgentsTab from "./tabs/agents/agents";
import EnvironmentDisplay from "./EnvironmentPage";
import ArtifactPage from "./tabs/artifacts/ArtifactPage";

const Sidebar: React.FC = () => {
    const [searchParams] = useSearchParams();
    const [tabIndex, setTabIndex] = useState(0);

    const tabIndexMap: { [key: string]: number } = {
            'environment': 0,
            'agents': 1,
            'artifacts': 2
        };

    useEffect(() => {
        // Read the 'tab' query parameter from the URL
        const tabQueryParam = searchParams.get('tab');
        // Determine the index of the tab based on the parameter value

        const newTabIndex = tabIndexMap[tabQueryParam as string];
        // If the tab index is found, update the state, otherwise default to first tab
        if (newTabIndex !== undefined) {
            setTabIndex(newTabIndex);
        }
    }, [searchParams]);

    const handleTabsChange = (index: number) => {
        setTabIndex(index);
        // Update the URL query parameter to reflect the new tab
        const tabQueryParamValue = Object.keys(tabIndexMap).find(key => tabIndexMap[key] === index);
        searchParams.set('tab', tabQueryParamValue as string);
        const newRelativePathQuery = window.location.pathname + '?' + searchParams.toString();
        window.history.pushState(null, '', newRelativePathQuery);
    };

    return (
        <Box h="90vh" bg="#444" color="white" p="20px">
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
                </TabList>
                <TabPanels overflowY="auto" h="80vh">
                    <TabPanel>
                        <EnvironmentDisplay />
                    </TabPanel>
                    <TabPanel>
                        <AgentsTab />
                    </TabPanel>
                    <TabPanel>
                        <ArtifactPage />
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Box>
    );
};

export default Sidebar;


