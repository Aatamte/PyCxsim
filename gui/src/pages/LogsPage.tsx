// LogsPage.tsx
import React from 'react';
import { Box, VStack, Text, Button } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

// Mock data for demonstration
const mockLogs = [
  { id: 1, message: "Log entry one" },
  { id: 2, message: "Log entry two" },
  { id: 3, message: "Log entry three" },
  // ... more log entries
];

const LogsPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box p={4}>
      {/* Back to Home Button */}
      <Button colorScheme="blue" onClick={() => navigate('/')} mb={4}>
        Back to Home
      </Button>

      {/* Logs List */}
      <VStack spacing={3} align="stretch">
        <Text fontSize="xl" fontWeight="bold">
          Application Logs
        </Text>
        {mockLogs.map(log => (
          <Box key={log.id} p={3} shadow="md" borderWidth="1px">
            {log.message}
          </Box>
        ))}
      </VStack>
    </Box>
  );
};

export default LogsPage;
