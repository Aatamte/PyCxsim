import React, { useState } from 'react';
import { Box, VStack, Input, Flex, IconButton, Collapse } from '@chakra-ui/react';
import { MdSend } from 'react-icons/md';
import { AiOutlineRobot } from 'react-icons/ai'; // Import a different AI-related icon
import Message from './TextMessaging';

const MessagingBox: React.FC = () => {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Welcome to the AI chat!', timestamp: '10:00 AM' },
    { role: 'user', content: 'Hello!', timestamp: '10:00 AM' },
    { role: 'assistant', content: 'Hi there!', timestamp: '10:05 AM' },
  ]);

  const [newMessage, setNewMessage] = useState('');
  const [currentUser, setCurrentUser] = useState('user');
  const [isSystemMessageCollapsed, setSystemMessageCollapsed] = useState(false);

  const handleMessageSubmit = () => {
    if (newMessage.trim() !== '') {
      const newMessageObj = {
        role: currentUser,
        content: newMessage,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages([...messages, newMessageObj]);
      setNewMessage('');

      // Switch the role between 'user' and 'assistant'
      setCurrentUser(currentUser === 'user' ? 'assistant' : 'user');
    }
  };

  return (
    <Box>
      <Collapse in={!isSystemMessageCollapsed}>
        <Message {...messages[0]} />
      </Collapse>
      <VStack spacing="4">
        {messages.slice(1).map((message, index) => (
          <Message key={index} {...message} />
        ))}
      </VStack>

      <Flex mt="4">
        <Input
          placeholder="Type your message..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          resize="vertical"
          minH="40px" // Minimum height for the input
        />
        <IconButton
          icon={<MdSend />}
          colorScheme="blue"
          onClick={handleMessageSubmit}
        />
      </Flex>
    </Box>
  );
};

export default MessagingBox;


