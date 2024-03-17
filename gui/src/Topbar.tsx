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
    useColorMode
} from '@chakra-ui/react';

import { MdMoreVert } from 'react-icons/md'; // This icon represents the nine-dot app icon, you can replace it with your preferred icon
import { useNavigate } from 'react-router-dom';
import useWebSocketListener from "./sockets/useWebSocketListener";

type WebSocketStatus = "connecting" | "open" | "closing" | "closed" | "unknown";

const webSocketIndicatorColor = {
    open: 'green.400',
    connecting: 'orange.400',
    closed: 'red.400',
    closing: 'orange.400',
    unknown: 'orange.400',
};

interface DataItem {
    key: string;
    value: string;
}

const TopBar: React.FC = () => {
    const navigate = useNavigate();
    const { data, error } = useWebSocketListener<DataItem[]>('cxmetadata');

    const { colorMode } = useColorMode();
    const color = { light: 'black', dark: 'white' };

    // Placeholder functions for connection actions
    const reconnectServer = async () => {/* Implementation here */};

    const disconnectServer = () => {/* Implementation here */};

    const findValueByKey = (key: string): string => {
      if (!data) return 'Not available'; // Early return if data is not available

      const item = data.find(d => d.key === key);
      return item ? item.value : 'N/A'; // Gracefully handle undefined
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
                <Image src={LogoImage} alt="Logo" maxW="20%" h="auto" />
                <Divider orientation="vertical" height="5vh" mx={4} />
                <Text fontSize="lg" mr={4}>{findValueByKey('name')}</Text>
            </Flex>

            <Spacer /> {/* This pushes everything else to the right */}

             {/* Server Connection Menu */}
            <Menu>
                <MenuButton as={Button} colorScheme="blue" mx={2} rightIcon={<Circle size="10px" bg={webSocketIndicatorColor["unknown"]} />} >
                    Connection
                </MenuButton>
                <MenuList>
                    <Box px={4} py={2}>
                        <Text color={color[colorMode]}>Status: {"unknown"}</Text>
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



