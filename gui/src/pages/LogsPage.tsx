import React, { useState, useEffect } from 'react';
import { Box, VStack, HStack, Text, Button, Tag } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns'; // For formatting timestamps
import useWebSocketListener from "../sockets/useWebSocketListener";

// LogLevel enum
export enum LogLevel {
    DEBUG = "DEBUG",
    INFO = "INFO",
    WARNING = "WARNING",
    ERROR = "ERROR",
    CRITICAL = "CRITICAL"
}

// LogEntry interface
export interface LogEntry {
    timestamp: Date;
    level: LogLevel;
    msg: string;
}


const LogsPage: React.FC = () => {
  const navigate = useNavigate();
  const { data, error } = useWebSocketListener<LogEntry[]>('cxlogs');

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

  // Create a new reversed array for rendering
  const reversedData = data ? [...data].reverse() : [];

  return (
    <Box p={4}>
      <Button colorScheme="blue" onClick={() => navigate('/')} mb={4}>
        Back to Home
      </Button>

      <VStack spacing={4} align="stretch">
        <Text fontSize="2xl" fontWeight="bold" mb={2}>
          Application Logs
        </Text>
        {reversedData.length > 0 ? (
          reversedData.map((log, index) => (
            <Box key={index} p={4} shadow="md" borderWidth="1px" borderRadius="md">
              <HStack justifyContent="space-between">
                <Tag size="sm" variant="solid" colorScheme={getTagColor(log.level)}>
                  {log.level}
                </Tag>
                <Text fontSize="sm" color="gray.500">
                  {format(new Date(log.timestamp), 'PPpp')} {/* Formatting timestamp */}
                </Text>
              </HStack>
              <Text mt={2}>{log.msg}</Text>
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



