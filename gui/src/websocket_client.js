import socketio from 'socket.io-client';

export default class SocketClient {
    constructor(callbacks = {}) {
        this.sio = null;
        this.callbacks = callbacks;
    }

   // Connect to WebSocket server
    connect(host = 'localhost', port = 8765, callbacks = {}) {
        // Merge constructor callbacks with connect callbacks
        const url = `${host}:${port}`;
        if (!this.sio) {
            this.callbacks = { ...this.callbacks, ...callbacks };
            this.sio = socketio(url, {
                autoConnect: true,
                logger: true,
                engineio_logger: true,
                reconnection: false
            });

            // Define callback functions
            this.sio.on('connect', this.handleConnect);
            this.sio.on('disconnect', this.handleDisconnect);
            this.sio.on('data', this.handleData);
            this.sio.on('connect_error', this.handleError);
            this.sio.on('connect_failed', this.handleError);

            // Initiate connection
            this.sio.connect();
        }
    }

    handleData = (data) => {
        console.log("Data recieved: ", data)
        if (this.callbacks.onData) {
            this.callbacks.onData(data);
        }

    };

    handleGUI = (data) => {
        if (this.callbacks.onGUI) {
            this.callbacks.onGUI(data);
        }
    };

    handleConnect = () => {
        console.log('Connected to server');
        this.registerClient();
        if (this.callbacks.onConnect) {
            this.callbacks.onConnect();
        }
    };

    handleDisconnect = () => {
        console.log('Disconnected from server');
        if (this.callbacks.onDisconnect) {
            this.callbacks.onDisconnect();
        }
    };

    handleEnvironment = (data) => {
        console.log('Environment data:', data);
        if (this.callbacks.onEnvironment) {
            this.callbacks.onEnvironment(data);
        }
    };

    handleRequest = (data) => {
        console.log('Request data:', data);
        if (this.callbacks.onRequest) {
            this.callbacks.onRequest(data);
        }
    };

    handleError = (error) => {
        console.error('Connection Error:', error);
        if (this.callbacks.onError) {
            this.callbacks.onError(error);
        }
    };

    // Register this client as a GUI client
    registerClient() {
        this.send('register_client', { type: 'gui' });
    }

    // Disconnect from WebSocket server
    disconnect() {
        if (this.sio) {
            this.sio.disconnect();
        }
    }

    // Send data to server
    send(event, data) {
        console.log('Event:', event, 'Data:', data);

        if (this.sio) {
            this.sio.emit(event, data);
        } else {
            console.error('Socket instance is null. Cannot send data.');
        }
    }
}


