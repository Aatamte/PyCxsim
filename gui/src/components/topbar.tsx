import React, { useState, useEffect, useRef } from 'react';
import {
    Image, Flex, Text, Divider, VStack, Circle, Button,
    CircularProgress, CircularProgressLabel, IconButton, Box
} from '@chakra-ui/react';
import LogoImage from '../assets/pycxsim_full_logo_no_background.png';
import { MdPause, MdPlayArrow, MdSkipNext, MdSkipPrevious } from "react-icons/md";
import TurnAnimation from "./TurnAnimation";
import { AlertDialog, AlertDialogBody, AlertDialogFooter, AlertDialogHeader, AlertDialogContent, AlertDialogOverlay, Spacer } from '@chakra-ui/react';
import { useBreakpointValue } from '@chakra-ui/react';
import { Menu, MenuButton, MenuList, MenuItem } from '@chakra-ui/react';
import { MdMoreVert } from 'react-icons/md'; // This icon represents the nine-dot app icon, you can replace it with your preferred icon
import { useNavigate } from 'react-router-dom';

import { useData } from './DataProvider';

type WebSocketStatus = "connecting" | "open" | "closing" | "closed" | "unknown";

const TopBar: React.FC = () => {
    const [isErrorDialogOpen, setIsErrorDialogOpen] = useState(false);
    const [errorUrl, setErrorUrl] = useState('');
    const cancelRef = useRef<HTMLButtonElement>(null); // Correctly typed ref for the AlertDialog

    const { state, dispatch, handleReconnect, sendData } = useData();

    // Example of using useBreakpointValue
    const fontSize = useBreakpointValue({ base: 'sm', md: 'md', lg: 'lg' });

    // Example of responsive spacing
    const paddingX = ['10px', '20px']; // Smaller padding on smaller screens
    const imageMaxWidth = ['50%', '10%']; // Larger relative width on smaller screens

    // Example of Flex direction change
    const flexDirection = useBreakpointValue({ base: 'column', md: 'row' });

    const navigate = useNavigate();

    useEffect(() => {

    }, []);

    const sendButtonAction = (action: string) => {
        sendData(action)
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
            px={paddingX}
            py="10px"
            align="center"
            justify="space-between"
            h="10vh"
        >
            {/* Error Dialog */}
            <AlertDialog
                isOpen={isErrorDialogOpen}
                leastDestructiveRef={cancelRef}
                onClose={() => setIsErrorDialogOpen(false)}
            >
                <AlertDialogOverlay>
                    <AlertDialogContent>
                        <AlertDialogHeader>Connection Error</AlertDialogHeader>
                        <AlertDialogBody>
                            Unable to reconnect to: {errorUrl}
                        </AlertDialogBody>
                        <AlertDialogFooter>
                            <Button ref={cancelRef} onClick={() => setIsErrorDialogOpen(false)}>
                                Close
                            </Button>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialogOverlay>
            </AlertDialog>
         {/* Left side: Logo and Name */}
            <Flex align="center">
                <Image
                    src={LogoImage}
                    alt="Logo"
                    maxW="20%"
                    maxH="75%"
                    h="auto"
                    w="auto"
                />
                <Divider orientation="vertical" borderColor="whiteAlpha.600" mx="4" height="5vh"/>
                <VStack spacing={1} align="right">
                    <Circle size="20px" bg={webSocketIndicatorColor[state.status]} />
                </VStack>
            </Flex>
            {/* Spacer to push content to the sides */}
            <Spacer />

            {/* Right side: Everything else */}
            <Flex align="center">
                <VStack spacing={2} width="200px">
                    <Text fontSize="lg">
                        {state.environment.name}
                    </Text>
               </VStack>
                <Divider orientation="vertical" borderColor="whiteAlpha" mx={4} height="8vh" />
                <VStack spacing={2} width="200px">
                    <Text fontSize="md">
                        {"Episode " + state.environment.currentEpisode + "/" + state.environment.maxEpisodes}
                    </Text>
                    <Text fontSize="md">
                        {"Step " + state.environment.currentStep + "/" + state.environment.maxSteps}
                    </Text>
               </VStack>
                <Divider orientation="vertical" borderColor="whiteAlpha" mx={4} height="8vh" />
                {/* Progress and control buttons */}
                <VStack spacing={2}>
                    <Flex>
                        {/* Control Buttons */}
                        <IconButton icon={<MdSkipPrevious />} size="lg" aria-label="Last Step" m="2" onClick={() => sendButtonAction('back')} />
                        <IconButton icon={<MdPause />} size="lg" aria-label="Pause" m="2" onClick={() => sendButtonAction('pause')} />
                        <IconButton icon={<MdPlayArrow />} size="lg" aria-label="Play" m="2" onClick={() => sendButtonAction('play')} />
                        <IconButton icon={<MdSkipNext />} size="lg" aria-label="Next Step" m="2" onClick={() => sendButtonAction('next')} />
                    </Flex>
                </VStack>

                <Divider orientation="vertical" borderColor="whiteAlpha" mx={4} height="8vh" />

                {/* Reconnect Button and WebSocket Indicator */}
                <Button colorScheme="blue" onClick={handleReconnect}>Reconnect</Button>

                <Divider orientation="vertical" borderColor="whiteAlpha" mx={4} height="8vh" />

            {/* App Menu Dropdown */}
            <Menu>
                <MenuButton
                    as={IconButton}
                    aria-label="Options"
                    icon={<MdMoreVert />}
                    size="lg"
                />
                <MenuList>
                    <MenuItem onClick={() => navigate('/settings')}>
                        <Text style={{ color: 'black' }}>
                            Settings
                        </Text>
                    </MenuItem>
                    <MenuItem onClick={() => navigate('/logs')}>
                        <Text style={{ color: 'black' }}>
                            Logs
                        </Text>
                    </MenuItem>
                    {/* ... other menu items ... */}
                </MenuList>
            </Menu>
            </Flex>
        </Flex>
    );
};

export default TopBar;



