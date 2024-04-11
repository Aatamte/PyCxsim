import React, { useState } from 'react';
import { Tabs, TabList, TabPanels, Tab, TabPanel, Box, Select, Flex, Text} from '@chakra-ui/react';
import MessagingBox from "./AgentPageComponents/MessagingBox";
import { Table, Thead, Tbody, Tr, Th, Td } from '@chakra-ui/react';
import useWebSocketListener from "../sockets/useWebSocketListener";
import TableUI from "../TableUI";

interface MessageProps {
  role: string;
  content: string;
  timestamp?: string; // Optional timestamp property
}


interface AgentItem {
    name: string;
    x_pos: string;
    y_pos: string;
    parameters: Record<string, string>;
    inventory: Record<string, number>;
    messages: MessageProps[];
    past_actions: Array<[number, string, Record<any, any>]>;
}

const InventoryTable = ({ inventory }: { inventory: Record<string, number> }) => {
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
                            <Td>{value.toString()}</Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
        </Box>
    );
};

const AgentsTab: React.FC = () => {
    const [selectedAgent, setSelectedAgent] = useState<string>('');
    const { data, error } = useWebSocketListener<AgentItem[]>('cxagents');

    const handleSelectAgent = (agentName: string) => {
        setSelectedAgent(agentName);
    };

    const selectedAgentData = data?.find(data => data.name === selectedAgent);

    return (
        <Box p={0} overflow={"hidden"}>
            <Flex align="center" mb={4}>
                <Text mr={2}>Agent:</Text>
                <Select
                    placeholder="Select agent"
                    value={selectedAgent}
                    color={"black"}
                    onChange={(e) => handleSelectAgent(e.target.value)}
                >
                    {data?.map((agent, index) => (
                        <option key={index} value={agent.name}>{agent.name}</option>
                    ))}
                </Select>
            </Flex>
            <Box borderWidth="1px" borderRadius="lg" p={0} borderColor="gray.200" w="full">
                <Tabs isFitted variant="enclosed">
                    <TabList mb="1em">
                        <Tab>I/O</Tab>
                        <Tab>Inventory</Tab>
                        <Tab>Actions</Tab>
                        <Tab>Other</Tab>
                    </TabList>
                    <TabPanels h="70vh" overflowY="auto">
                        <TabPanel>
                            {selectedAgentData && <MessagingBox messages={selectedAgentData.messages} />}
                        </TabPanel>
                        <TabPanel>
                            {selectedAgentData ? (
                                <InventoryTable inventory={selectedAgentData.inventory} />
                            ) : (
                                <Text>No agent selected or agent not found.</Text>
                            )}
                        </TabPanel>
                            <TabPanel>
                              {selectedAgentData ? (
                                  <TableUI data={selectedAgentData.past_actions}></TableUI>
                              ) : (
                                <Text>No agent selected or agent not found.</Text>
                              )}
                            </TabPanel>
                        <TabPanel>
                            {selectedAgentData ? (
                                // Assuming you want to display the parameters the same way as the inventory
                                <InventoryTable inventory={selectedAgentData.parameters as unknown as Record<string, number>} />
                            ) : (
                                <Text>No agent selected or agent not found.</Text>
                            )}
                        </TabPanel>
                    </TabPanels>
                </Tabs>
            </Box>
        </Box>
    );
};

export default AgentsTab;


