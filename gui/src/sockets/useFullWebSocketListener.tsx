import { useState, useEffect } from 'react';
import socket from "./socketConnection";

type Response<T> = {
  table_name: string;
  content: T;
};

const useFullWebSocketListener = <T,>(): { data: Record<string, T | null>; error: Error | null } => {
  const [data, setData] = useState<Record<string, T | null>>({});
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Function to handle data updates from any room
    const handleDataUpdate = (receivedData: Response<T>) => {
      setData(prevData => ({
        ...prevData,
        [receivedData.table_name]: receivedData.content, // Update the room-specific data
      }));
    };

    // Subscribe to the data_update event
    socket.on('data_update', handleDataUpdate);

    return () => {
      // Unsubscribe from the data_update event
      socket.off('data_update', handleDataUpdate);

      // Emit a leave event for each room that has been joined
      // This assumes you have a way to track which rooms have been joined
      Object.keys(data).forEach(room => {
        socket.emit('leave_room', { room });
      });
    };
  }, []); // The empty dependency array means this effect runs only once when the component mounts

  return { data, error };
};

export default useFullWebSocketListener;