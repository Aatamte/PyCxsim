// websocket_client.js

class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
            console.log("WebSocket connection established.");
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

    sendMessage(message) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        } else {
            console.error("WebSocket is not open. Message not sent:", message);
        }
    }

    handleMessage(data) {
        const message = JSON.parse(data);

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
