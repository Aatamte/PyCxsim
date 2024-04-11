import { useState, useEffect } from 'react';
import socket from './socketConnection';

type Response<T> = {
  table_name: string;
  content: T;
};

const useSocketListener = <T,>(
  room: string | null = null
): { data: T | null; error: Error | null; connectionStatus: 'connected' | 'disconnected' } => {
  const [data, setData] = useState<T | null>(null);
  const [error] = useState<Error | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected'>('disconnected');

  useEffect(() => {
    // Listen for data updates specific to the joined room
    const handleDataUpdate = (receivedData: Response<T>) => {
      if (receivedData?.table_name === room) {
        setData(receivedData.content); // Update the state with the received data
      }
    };

    const handleConnect = () => {
      setConnectionStatus('connected');
    };

    const handleDisconnect = () => {
      setConnectionStatus('disconnected');
    };

    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    socket.on('data_update', handleDataUpdate);

    return () => {
      socket.off('connect', handleConnect);
      socket.off('disconnect', handleDisconnect);
      socket.off('data_update', handleDataUpdate); // Remove the specific event listener
      if (room) {
        // If a room was joined, leave the room before disconnecting
        socket.emit('leave_room', { room });
      }
    };
  }, [room]); // Re-run the effect if the room changes

  return { data, error, connectionStatus };
};

export default useSocketListener;

