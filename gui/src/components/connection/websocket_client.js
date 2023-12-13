

class WebSocketClient {
    constructor(url, port) {
        this.url = `${url}:${port}`;
        this.socket = new WebSocket(this.url);

        this.socket.onopen = () => {
            console.log("WebSocket connection established.");
            this.sendMessage({ type: 'connection_established', message: 'Client has connected.' });
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        this.socket.onclose = () => {
            console.log("WebSocket connection closed.");
        };

        this.socket.onmessage = (event) => {
            this.handleMessage(event.data);
        };
    }

    getStatus() {
        switch (this.socket.readyState) {
            case WebSocket.CONNECTING:
                return 'connecting';
            case WebSocket.OPEN:
                return 'open';
            case WebSocket.CLOSING:
                return 'closing';
            case WebSocket.CLOSED:
                return 'closed';
            default:
                return 'unknown';
        }
    }

    reconnect() {
        console.log("Attempting to reconnect...");

        // Close the existing connection if it's open or in the process of closing
        if (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CLOSING) {
            this.socket.close();
        }

        // Create a new WebSocket connection
        this.socket = new WebSocket(this.url);

        // Reinitialize the event handlers
        this.socket.onopen = () => {
            console.log("WebSocket connection reestablished.");
            this.sendMessage({ type: 'connection_reestablished', message: 'Client has reconnected.' });
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        this.socket.onclose = () => {
            console.log("WebSocket connection closed.");
        };

        this.socket.onmessage = (event) => {
            this.handleMessage(event.data);
        };
    }

    ping() {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({ type: 'ping' }));
        } else {
            console.error("WebSocket is not open. Ping not sent.");
        }
    }

    sendMessage(message) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
            console.log(message)
        } else {
            console.error("WebSocket is not open. Message not sent:", message);
        }
    }

    handleMessage(data) {
        const message = JSON.parse(data);
        console.log(message)

        switch (message.type) {
            case 'dict':
                // Handle dictionary
                break;
            case 'list':
                // Handle list
                break;
            case 'dataframe':
                // Handle DataFrame
                break;
            case 'numpy_array':
                // Handle NumPy array
                break;
            case 'string':
                // Handle string
                break;
            default:
                console.log('Unknown data type:', message.type);
        }
    }

    close() {
        this.socket.close();
    }
}

export default WebSocketClient;
