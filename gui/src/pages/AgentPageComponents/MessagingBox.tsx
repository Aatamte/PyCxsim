import React from 'react';
import { Box, VStack, Collapse } from '@chakra-ui/react';

import Message from "../AgentPageComponents/TextMessaging";

interface MessageProps {
  role: string;
  content: string;
  timestamp?: string; // Optional timestamp property
}

interface MessagingBoxProps {
  messages: MessageProps[]; // Expect messages as props
  isSystemMessageCollapsed?: boolean; // Optional prop to control the visibility of the first message
}

const MessagingBox: React.FC<MessagingBoxProps> = ({ messages, isSystemMessageCollapsed = false }) => {
    // Function to check if an object is a valid message
    const isValidMessage = (obj: any): obj is MessageProps => {
        return obj && obj.role && typeof obj.content === 'string';
    };

    return (
        <Box>
            <VStack spacing="4">
                {messages.map((message, index) => (
                    isValidMessage(message) && <Message key={index} {...message} />
                ))}
            </VStack>
        </Box>
    );
};

export default MessagingBox;




