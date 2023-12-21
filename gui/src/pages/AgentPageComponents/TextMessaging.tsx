import React from 'react';
import { Box, Text, Flex, Avatar } from '@chakra-ui/react';

interface MessageProps {
  role: string,
  content: string;
}

interface MarkdownTextProps {
  text: string;
}

const MarkdownText: React.FC<MarkdownTextProps> = ({ text }) => {
    const convertMarkdown = (inputText: string): string => {
        let htmlText = inputText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        htmlText = htmlText.split('\n').map((item, index) => {
            if (item.startsWith('- ')) {
                return `<li key=${index}>${item.substring(2)}</li>`;
            }
            return `<div key=${index}>${item}</div>`;
        }).join('');

        return htmlText;
    };

    return (
        <div dangerouslySetInnerHTML={{ __html: convertMarkdown(text) }} />
    );
};

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
         <MarkdownText text={content} />
      </Box>
    </Flex>
  );
};

export default Message;


