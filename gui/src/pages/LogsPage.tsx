import React, { useEffect } from 'react';
import { Box, VStack, HStack, Text, Button, Tag } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useData } from "../DataProvider";
import { format } from 'date-fns'; // For formatting timestamps

const LogsPage: React.FC = () => {
  const navigate = useNavigate();
  const { environment } = useData(); // Assuming `state` has the necessary logs

  const logs = environment.logs; // Assuming logs are stored here

    useEffect(() => {
    // This function is called whenever `environment.logs` changes.
    // You don't necessarily need to do anything here if just re-rendering is enough.
    console.log('Logs have been updated');
  }, [environment.logs]); // Depend on `environment.logs` to trigger this effect


  // Helper function to determine color based on log level
  const getTagColor = (level: string) => {
    switch (level) {
      case 'DEBUG': return 'gray';
      case 'INFO': return 'blue';
      case 'WARNING': return 'orange';
      case 'ERROR': return 'red';
      case 'CRITICAL': return 'purple';
      default: return 'gray';
    }
  };

  return (
    <Box p={4}>
      <Button colorScheme="blue" onClick={() => navigate('/')} mb={4}>
        Back to Home
      </Button>

      <VStack spacing={4} align="stretch">
        <Text fontSize="2xl" fontWeight="bold" mb={2}>
          Application Logs
        </Text>
        {logs && logs.length > 0 ? (
          logs.map((log, index) => (
            <Box key={index} p={4} shadow="md" borderWidth="1px" borderRadius="md">
              <HStack justifyContent="space-between">
                <Tag size="sm" variant="solid" colorScheme={getTagColor(log.level)}>
                  {log.level}
                </Tag>
                <Text fontSize="sm" color="gray.500">
                  {format(new Date(log.timestamp), 'PPpp')} {/* Formatting timestamp */}
                </Text>
              </HStack>
              <Text mt={2}>{log.message}</Text>
            </Box>
          ))
        ) : (
          <Text>No logs available</Text>
        )}
      </VStack>
    </Box>
  );
};

export default LogsPage;


