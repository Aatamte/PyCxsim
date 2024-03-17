import { useCallback } from 'react';
import socket from './socketConnection';

type Payload<T> = {
  table_name: string;
  content: T;
};

const useSocketSender = <T,>() => {
  const sendData = useCallback((payload: Payload<T>) => {
    socket.emit('data_send', payload);
  }, []);

  return sendData;
};

export default useSocketSender;