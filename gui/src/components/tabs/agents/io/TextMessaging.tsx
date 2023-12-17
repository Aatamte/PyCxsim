import React from 'react';
import { Box, Text, Flex, Avatar, Spacer } from '@chakra-ui/react';

interface MessageProps {
  role: string,
  content: string;
}

const Message: React.FC<MessageProps> = ({ role, content }) => {
  let bgColor;
  let textColor;
  let alignment;

  switch (role) {
    case 'assistant':
      bgColor = 'blue.100';
      textColor = 'blue.700';
      alignment = 'flex-start';
      break;
    case 'system':
      bgColor = 'gray.100';
      textColor = 'gray.700';
      alignment = 'center';
      break;
    case 'user':
      bgColor = 'green.100';
      textColor = 'green.700';
      alignment = 'flex-end';
      break;
    default:
      bgColor = 'gray.100';
      textColor = 'gray.700';
      alignment = 'flex-start';
  }

  return (
    <Flex
      p="2"
      alignItems="flex-start"
      justifyContent={alignment}
      width="100%"
    >
      {role !== 'system' && (
        <Avatar name={role} size="sm" mr="2" />
      )}
      <Box
        bg={bgColor}
        color={textColor}
        borderRadius="md"
        p="2"
        maxW="70%"
        boxShadow="md"
      >
        {role !== 'system' && (
          <Text fontWeight="bold">{role}</Text>
        )}
        <Text>{content}</Text>
      </Box>
    </Flex>
  );
};

export default Message;


