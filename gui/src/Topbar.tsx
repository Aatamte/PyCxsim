import React, { useState, useEffect, useRef } from 'react';
import LogoImage from './assets/pycxsim_full_logo_no_background.png';
import { Flex, Image, Text, Button, Circle, Divider, Spacer, Box, Menu, MenuButton, MenuList, MenuItem, IconButton, useToast } from '@chakra-ui/react';

import { MdMoreVert } from 'react-icons/md'; // This icon represents the nine-dot app icon, you can replace it with your preferred icon
import { useNavigate } from 'react-router-dom';

import { useData } from './DataProvider';

type WebSocketStatus = "connecting" | "open" | "closing" | "closed" | "unknown";

const TopBar: React.FC = () => {
    const { state, handleReconnect, sendData } = useData();
    const navigate = useNavigate();
    const toast = useToast();

    const connectButton = async () => {
        // Create an initial toast with a loading indicator
        const toastId = toast({
            title: "Connecting...",
            description: `Attempting to connect to ${state.socketParams.host}:${state.socketParams.port}`,
            status: "info",
            duration: null, // Keep it open indefinitely
            isClosable: true,
            position: "top",
        });

        try {
            const result = await handleReconnect(); // wait for the promise to resolve

            // Update the toast based on the result
            if (result) {
                toast.update(toastId, {
                    title: "Connected",
                    description: "You have successfully connected.",
                    status: "success",
                    duration: 3000, // Close after 3 seconds
                });
            } else {
                toast.update(toastId, {
                    title: "Connection Failed",
                    description: "Unable to reconnect. Please try again.",
                    status: "error",
                    duration: 3000, // Close after 3 seconds
                });
            }
        } catch (error) {
            // Handle any errors that occur during the reconnect process
            toast.update(toastId, {
                title: "Connection Error",
                description: `Error occurred: ${error}`,
                status: "error",
                duration: 3000, // Close after 3 seconds
            });
        }
    };

    const webSocketIndicatorColor: Record<WebSocketStatus, string> = {
        open: 'green.400',
        connecting: 'orange.400',
        closed: 'red.400',
        closing: 'orange.400',
        unknown: 'orange.400'
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
                <Text fontSize="lg" mr={4}>{state.environment.name}</Text>
            </Flex>

            <Spacer /> {/* This pushes everything else to the right */}

            {/* Reconnect Button */}
            <Button colorScheme="blue" onClick={connectButton} leftIcon={<Circle size="20px" bg={webSocketIndicatorColor[state.socketParams.status]} />}>
                Connect
            </Button>

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



