// socketConnection.js
import io from 'socket.io-client';

const socket = io('http://localhost:8100');

socket.on('connect', () => {
  console.log('Socket.IO Connected');
});

socket.on('connect_error', (err) => {
  console.error('Socket.IO Connection Error: ', err);
});

export default socket;