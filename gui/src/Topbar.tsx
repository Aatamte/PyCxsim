import React, { useState, useEffect, useRef } from 'react';
import LogoImage from './assets/pycxsim_full_logo_no_background.png';
import {
    Flex,
    Image,
    Text,
    Button,
    Circle,
    Divider,
    Spacer,
    Box,
    Menu,
    MenuButton,
    MenuList,
    MenuItem,
    IconButton,
    useToast,
    useColorMode
} from '@chakra-ui/react';

import { MdMoreVert } from 'react-icons/md'; // This icon represents the nine-dot app icon, you can replace it with your preferred icon
import { useNavigate } from 'react-router-dom';
import { useData } from './DataProvider';

type WebSocketStatus = "connecting" | "open" | "closing" | "closed" | "unknown";

const webSocketIndicatorColor = {
    open: 'green.400',
    connecting: 'orange.400',
    closed: 'red.400',
    closing: 'orange.400',
    unknown: 'orange.400',
};

const TopBar: React.FC = () => {
    const { state, handleReconnect, sendData } = useData();
    const navigate = useNavigate();
    const { colorMode } = useColorMode();
    const bgColor = { light: 'gray.100', dark: '#333' };
    const color = { light: 'black', dark: 'white' };
    const borderColor = { light: 'gray.200', dark: 'gray.600' };
    const menuListBgColor = { light: 'white', dark: 'gray.700' };
    const toast = useToast();

        // Ensure the server connection status is a valid WebSocketStatus
    const serverConnectionStatus = state.kv_storage.get("server_connection");
    const isValidStatus = Object.keys(webSocketIndicatorColor).includes(serverConnectionStatus);
    const serverStatus: WebSocketStatus = isValidStatus ? serverConnectionStatus as WebSocketStatus : "unknown";


    // Placeholder functions for connection actions
    const reconnectServer = async () => {/* Implementation here */};

    const disconnectServer = () => {/* Implementation here */};

    const reconnectEnvironment = async () => {/* Implementation here */};

    const disconnectEnvironment = () => {/* Implementation here */};


    return (
        <Flex
            bg="#333"
            color="white"
            px="20px"
            py="10px"
            align="center"
            justify="space-between"
            h="7vh"
        >
            {/* Logo + Indicator (20% of the total width) */}
            <Flex flex="2" align="center" mr={4}>
                <Image src={LogoImage} alt="Logo" maxW="30%" h="auto" />
                <Divider orientation="vertical" height="5vh" mx={4} />
                <Text fontSize="lg" mr={4}>{state.environment.name}</Text>
            </Flex>

            <Spacer /> {/* This pushes everything else to the right */}

            {/* Environment Connection Menu */}
            <Menu>
                <MenuButton as={Button} colorScheme="blue" mx={2} rightIcon={<Circle size="10px" bg={webSocketIndicatorColor[state.socketParams.environment_status]} />} >
                    Environment
                </MenuButton>
                <MenuList>
                    <Box px={4} py={2}>
                        <Text color={color[colorMode]}>Status: {state.socketParams.environment_status}</Text>
                    </Box>
                    <MenuItem onClick={reconnectEnvironment} color={color[colorMode]}>Reconnect Environment</MenuItem>
                    <MenuItem onClick={disconnectEnvironment} color={color[colorMode]}>Disconnect Environment</MenuItem>
                </MenuList>
            </Menu>

             {/* Server Connection Menu */}
            <Menu>
                <MenuButton as={Button} colorScheme="blue" mx={2} rightIcon={<Circle size="10px" bg={webSocketIndicatorColor[serverStatus]} />} >
                    Server
                </MenuButton>
                <MenuList>
                    <Box px={4} py={2}>
                        <Text color={color[colorMode]}>Status: {serverStatus}</Text>
                    </Box>
                    <MenuItem onClick={reconnectServer} color={color[colorMode]}>Reconnect Server</MenuItem>
                    <MenuItem onClick={disconnectServer} color={color[colorMode]}>Disconnect Server</MenuItem>
                </MenuList>
            </Menu>

            <Divider orientation="vertical" height="5vh" mx={4} />

            {/* Triple Dot Button (10% of the total width) */}
            <Box>
                <Menu>
                    <MenuButton as={IconButton} icon={<MdMoreVert />} size="lg" />
                    <MenuList>
                        <MenuItem onClick={() => navigate('/settings')} color={'black'}>Settings</MenuItem>
                        <MenuItem onClick={() => navigate('/logs')} color={'black'} >Logs</MenuItem>
                    </MenuList>
                </Menu>
            </Box>
        </Flex>
    );
};

export default TopBar;



