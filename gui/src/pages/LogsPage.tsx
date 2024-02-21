import React, { useState, useEffect } from 'react';
import { Box, VStack, HStack, Text, Button, Tag } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns'; // For formatting timestamps
import { useData } from '../DataProvider'; // Adjust the import path as needed
import { LogLevel, LogEntry} from "../data_structures/LogsTable";

const LogsPage: React.FC = () => {
  const navigate = useNavigate();
   const { logsTable, addLog } = useData(); // Use useData hook to access logsTable and addLog\
  const [logs, setLogs] = useState<LogEntry[]>([]); // Manage logs as component state

  // Function to add a mock log entry
  const addMockLog = () => {
    const mockLevels = Object.values(LogLevel);
    const randomLevel = mockLevels[Math.floor(Math.random() * mockLevels.length)] as LogLevel;
    addLog(randomLevel, `Mock log message at ${new Date().toISOString()}`);
    // Update component state after adding a new log
    setLogs(logsTable.getLogs());
  };

  useEffect(() => {
    // Initial load of logs
    setLogs(logsTable.getLogs());
  }, []); // Empty dependency array ensures this runs once on mount



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

      {/* Button to add a mock log entry */}
      <Button colorScheme="green" onClick={addMockLog} mb={4}>
        Add Mock Log
      </Button>

      <VStack spacing={4} align="stretch">
        <Text fontSize="2xl" fontWeight="bold" mb={2}>
          Application Logs
        </Text>
        {logs.length > 0 ? (
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



