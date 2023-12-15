import React, { useState, useEffect, useRef } from 'react';
import {
    Image, Flex, Text, Divider, VStack, Circle, Button,
    CircularProgress, CircularProgressLabel, IconButton, Box
} from '@chakra-ui/react';
import LogoImage from '../assets/pycxsim_full_logo_no_background.png';
import WebSocketClient from "./websocket_client";
import { MdPause, MdPlayArrow, MdSkipNext, MdSkipPrevious } from "react-icons/md";
import TurnAnimation from "./TurnAnimation";
import { AlertDialog, AlertDialogBody, AlertDialogFooter, AlertDialogHeader, AlertDialogContent, AlertDialogOverlay } from '@chakra-ui/react';
import { useData } from './DataProvider';

type WebSocketStatus = "connecting" | "open" | "closing" | "closed" | "unknown";

const TopBar: React.FC = () => {
      // Replace with actual data and functionality
  const currentStep = 5;
  const maxSteps = 10;
  const currentEpisode = 2;
  const maxEpisodes = 5;

  // Calculate progress as a percentage
  const stepProgress = (currentStep / maxSteps) * 100;
  const episodeProgress = (currentEpisode / maxEpisodes) * 100;
    const [webSocketStatus, setWebSocketStatus] = useState<WebSocketStatus>('unknown');
    const [wsClient, setWsClient] = useState<WebSocketClient | null>(null);
    const [simulationStatus, setSimulationStatus] = useState("idle");
    const [isErrorDialogOpen, setIsErrorDialogOpen] = useState(false);
    const [errorUrl, setErrorUrl] = useState('');
    const cancelRef = useRef<HTMLButtonElement>(null); // Correctly typed ref for the AlertDialog

    const { state, dispatch } = useData();
    const environment = state.environment;

    useEffect(() => {
        const client = new WebSocketClient('ws://localhost', '8765');
        setWsClient(client);

        // Update the status whenever the state changes
        const interval = setInterval(() => {
            setWebSocketStatus(client.getStatus());
        }, 1000); // Update status every 1 second

        return () => {
            clearInterval(interval);
            client.close();
        };
    }, []);

    const handleReconnect = () => {
        if (wsClient) {
            wsClient.reconnect(); // Assuming reconnect method exists in WebSocketClient
        }

        // handleReconnectError('');
    };

    const sendButtonAction = (action: string) => {
        if (wsClient && wsClient.socket.readyState === WebSocket.OPEN) {
            wsClient.socket.send(JSON.stringify({ button: action }));
             setSimulationStatus(action); // Update internal status
        }
    };

    const handlePing = () => {
        if (wsClient) {
            wsClient.ping();
        }
    };

    const webSocketStatusText: Record<WebSocketStatus, string> = {
        open: 'Connected',
        connecting: 'Connecting',
        closed: 'Disconnected',
        closing: 'Disconnecting',
        unknown: 'Unknown'
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
            <Image
                src={LogoImage}
                alt="Logo"
                maxW="10%"
                maxH="75%"
                h="auto"
                w="auto"
            />
            <Divider orientation="vertical" borderColor="whiteAlpha.600" mx="4" height="50%" alignSelf="center" />
            <Text fontSize="lg">
              {environment.name}
            </Text>
            <Divider orientation="vertical" />
            <Flex justify="space-between" align="center" h="100%">
        <VStack spacing={4} width="200px"> {/* Fixed width */}
          <Text fontSize="sm">Episode Progress</Text>
          <CircularProgress value={(environment.currentEpisode / environment.maxEpisodes) * 100} color="green.400">
            <CircularProgressLabel>{`${environment.currentEpisode}/${environment.maxEpisodes}`}</CircularProgressLabel>
          </CircularProgress>
        </VStack>

        <Divider orientation="vertical" />

        <VStack spacing={4} width="200px"> {/* Fixed width */}
          <Text fontSize="sm">Step Progress</Text>
          <CircularProgress value={(environment.currentStep / environment.maxSteps) * 100} color="blue.400">
            <CircularProgressLabel>{`${environment.currentStep}/${environment.maxSteps}`}</CircularProgressLabel>
          </CircularProgress>
        </VStack>

        <Divider orientation="vertical" />

        <VStack spacing={2}>
          <Text fontSize="sm">
              {simulationStatus}
            </Text>
          <Flex>
            <IconButton icon={<MdSkipPrevious />} size="lg" aria-label="Last Step" m="2"  onClick={() => sendButtonAction('back')} />
              <IconButton icon={<MdPause />} size="lg" aria-label="Pause" m="2"   onClick={() => sendButtonAction('pause')} />
            <IconButton icon={<MdPlayArrow />} size="lg" aria-label="Play" m="2"   onClick={() => sendButtonAction('play')} />
            <IconButton icon={<MdSkipNext />} size="lg" aria-label="Next Step" m="2"   onClick={() => sendButtonAction('next')} />
          </Flex>
        </VStack>
       <Divider orientation="vertical" />
      </Flex>
            <Button colorScheme="blue" onClick={handlePing}>Ping</Button>
            <Button colorScheme="blue" onClick={handleReconnect}>Reconnect</Button>
            <VStack spacing={1} align="right">
                <Circle size="20px" bg={webSocketIndicatorColor[webSocketStatus]} /> {/* Larger circle */}
            </VStack>

        </Flex>
    );
};

export default TopBar;



