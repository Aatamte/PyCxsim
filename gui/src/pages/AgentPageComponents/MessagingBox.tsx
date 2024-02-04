import React, { useState, useEffect} from 'react';
import { Box, VStack, Input, Flex, IconButton, Collapse } from '@chakra-ui/react';
import { MdSend } from 'react-icons/md';

import Message from "../AgentPageComponents/TextMessaging";
import {useData} from "../../DataProvider";

interface MessageProps {
  role: string,
  content: string;
}


interface MessagingBoxProps {
    selectedAgent: string;
}

const MessagingBox: React.FC<MessagingBoxProps> = ({ selectedAgent }) => {
        // Define the fontSize constant
    const fontSize = '10px'; // Example size, adjust as needed

    const { environment  } = useData();
    const [messages, setMessages] = useState(environment.agents[selectedAgent]?.messages || []);

    const [newMessage, setNewMessage] = useState('');
    const [currentUser, setCurrentUser] = useState('user');
    const [isSystemMessageCollapsed, setSystemMessageCollapsed] = useState(false);

    // Update messages when selectedAgent changes
    useEffect(() => {
        setMessages(environment.agents[selectedAgent]?.messages || []);
    }, [selectedAgent, environment.currentStep]);


    useEffect(() => {
    // For example, log when state changes
        console.log("State updated", environment);
    }, [environment]); // Dependency on state ensures this runs when state changes

    const handleMessageSubmit = () => {
        if (newMessage.trim() !== '') {
            const newMessageObj = {
                role: currentUser,
                content: newMessage,
                timestamp: new Date().toLocaleTimeString(),
            };

            setMessages(prevMessages => [...prevMessages, newMessageObj]);
            setNewMessage('');

            // Switch the role between 'user' and 'assistant'
            setCurrentUser(currentUser === 'user' ? 'assistant' : 'user');
        }
    };

       // Function to check if an object is a valid message
    const isValidMessage = (obj: any): obj is MessageProps => {
        return obj && obj.role && typeof obj.content === 'string';
    };

    return (
        <Box
        >
            <Collapse in={!isSystemMessageCollapsed} style={{ fontSize }}>
                {messages[0] && isValidMessage(messages[0]) && <Message {...messages[0]} />}
            </Collapse>
            <VStack spacing="4" style={{ fontSize }}>
                {messages.slice(1).map((message, index) => (
                    isValidMessage(message) && <Message key={index} {...message} />
                ))}
            </VStack>

            <Flex mt="4">
                <Input
                    placeholder="Type your message..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    resize="vertical"
                    minH="40px"
                />
                <IconButton
                    icon={<MdSend />}
                    colorScheme="blue"
                    onClick={handleMessageSubmit}
                    aria-label="Send message"
                />
            </Flex>
        </Box>
    );
};

export default MessagingBox;


