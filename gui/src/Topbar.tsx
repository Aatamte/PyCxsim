import React, { useState, useEffect, useRef } from 'react';
import LogoImage from './assets/pycxsim_full_logo_no_background.png';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from './store'; // Adjust the import path as needed
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

import { updateKVStorage } from "./reducers/kv_storageSlice";

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
    const { environment, kv_storage, sendData } = useData();
    const navigate = useNavigate();
    const dispatch = useDispatch(); // Hook to dispatch actions
    const kvStorage = useSelector((state: RootState) => state.kv_storage.data);

    const { colorMode } = useColorMode();
    const bgColor = { light: 'gray.100', dark: '#333' };
    const color = { light: 'black', dark: 'white' };
    const borderColor = { light: 'gray.200', dark: 'gray.600' };
    const menuListBgColor = { light: 'white', dark: 'gray.700' };
    const toast = useToast();

        // Ensure the server connection status is a valid WebSocketStatus
    const serverConnectionStatus = kv_storage.get("gui_connection");
    const isValidStatus = Object.keys(webSocketIndicatorColor).includes(serverConnectionStatus);
    const serverStatus: WebSocketStatus = isValidStatus ? serverConnectionStatus as WebSocketStatus : "unknown";


    // Ensure the server connection status is a valid WebSocketStatus
    const EnvironmentConnectionStatus = kv_storage.get("environment_connection");
    const isValidEnvStatus = Object.keys(webSocketIndicatorColor).includes(EnvironmentConnectionStatus);
    const envStatus: WebSocketStatus = isValidEnvStatus ? EnvironmentConnectionStatus as WebSocketStatus : "unknown";

    const counter = useSelector((state: RootState) => state.kv_storage.data.get('counter'));

    // Function to clear session storage
    const clearSessionStorage = () => {
        sessionStorage.clear();
        console.log('Session storage cleared');
        // Optionally, refresh the page or reset state in your app as needed
        // window.location.reload(); // Uncomment if you want to reload the page
    };



    // Placeholder functions for connection actions
    const reconnectServer = async () => {/* Implementation here */};

    const disconnectServer = () => {/* Implementation here */};

    const reconnectEnvironment = async () => {/* Implementation here */};

    const disconnectEnvironment = () => {/* Implementation here */};
    // Example function to update kv_storage

    const handleChangeKVStorage = () => {
       console.log(kv_storage)
        // Example: updating the 'exampleKey' with a new value

        const newCounterValue = (counter ?? 0) + 1;
        dispatch(updateKVStorage({ key: 'counter', value: newCounterValue }));
    };

        // Function to render kv_storage content
    const renderKVStorageContent = () => {
        // This example assumes you want to display all key-value pairs
        const entries = Object.entries(kvStorage.storage); // Accessing storage directly from the KVStorage instance
        return entries.map(([key, value], index) => (
            <Text key={index} color="white" mx={2}>
                {key}: {value.toString()}
            </Text>
        ));
    };

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
                <Text fontSize="lg" mr={4}>{environment.name}</Text>
            </Flex>

            <Spacer /> {/* This pushes everything else to the right */}

            {/* Button to clear session storage */}
            <Button colorScheme="red" mx={2} onClick={clearSessionStorage}>
                Clear Session Storage
            </Button>
            <Button colorScheme="teal" mx={2} onClick={handleChangeKVStorage}>
                Update KV Storage
            </Button>

            {/* Environment Connection Menu */}
            <Menu>
                <MenuButton as={Button} colorScheme="blue" mx={2} rightIcon={<Circle size="10px" bg={webSocketIndicatorColor[envStatus]} />} >
                    Environment
                </MenuButton>
                <MenuList>
                    <Box px={4} py={2}>
                        <Text color={color[colorMode]}>Status: {envStatus}</Text>
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


