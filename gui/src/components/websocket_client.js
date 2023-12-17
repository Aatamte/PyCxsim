
class WebSocketManager {
    constructor(url, port, callbacks = {}) {
        // Pass the callbacks to the WebSocketClient
        this.client = new WebSocketClient(url, port, callbacks);
    }

    startReconnectScheduler() {
        this.reconnectTimer = setInterval(() => {
            this.client.scheduledReconnect();
        }, this.reconnectInterval);
    }

    stopReconnectScheduler() {
        clearInterval(this.reconnectTimer);
    }

    async manualReconnect() {
        try {
            const result = await this.client.reconnectPromise();
            return result;
        } catch (error) {
            console.error("Reconnect failed:", error);
            return false;
        }
    }
}

class WebSocketClient {
    constructor(url, port, callbacks = {}) {
        this.port = port
        this.url = `${url}:${port}`;
        this.callbacks = callbacks;

        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = callbacks.maxReconnectAttempts || 5;
        this.reconnectInterval = callbacks.reconnectInterval || 1000; // 1 second
        this.exponentialBackoff = callbacks.exponentialBackoff || false;

        this.connect()
    }

    // Manual reconnect triggered by UI
    manualReconnect() {
        this.resetReconnectAttempts();
        this.reconnect();
    }

    // Scheduled reconnect
    scheduledReconnect() {
        if (this.shouldReconnect()) {
            this.reconnect();
        }
    }

    shouldReconnect() {
    const currentTime = Date.now();
    if (!this.startTime) {
        this.startTime = currentTime;
    }
        // Check if within the maximum timeframe
        return currentTime - this.startTime < this.maxTimeframe;
    }

    resetReconnectAttempts() {
        this.reconnectAttempts = 0;
        this.startTime = null;
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

   connect() {
        try {
            this.socket = new WebSocket(this.url);
            this.initializeEventListeners();
        } catch (error) {
            console.error("Error creating WebSocket:", error);
        }
    }

    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
                console.log(`Reconnect attempt ${this.reconnectAttempts + 1}`);
                this.removeEventListeners();
                this.socket.close();
                this.connect()
                this.reconnectAttempts++;
            }, this.getReconnectDelay());
        } else {
            console.log("Max reconnect attempts reached.");
        }
    }

    initializeEventListeners() {
        this.socket.onopen = () => {
            console.log("WebSocket connection established.");
            if (this.callbacks.onOpen) this.callbacks.onOpen();
        };

        this.socket.onclose = () => {
            console.log("WebSocket connection closed.");
            if (this.callbacks.onClose) this.callbacks.onClose();
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
            if (this.callbacks.onError) this.callbacks.onError(error);
        };

        this.socket.onmessage = (event) => {
            if (this.callbacks.onMessage) {
                this.callbacks.onMessage(JSON.parse(event.data))
            }
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
        return new Promise((resolve, reject) => {
            if (this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify(message), (error) => {
                    if (error) {
                        reject(error);
                    } else {
                        resolve();
                    }
                });
            } else {
                reject("WebSocket is not open.");
            }
        });
    }

    close() {
        this.socket.close();
    }

    removeEventListeners() {
        this.socket.onopen = null;
        this.socket.onerror = null;
        this.socket.onclose = null;
        this.socket.onmessage = null;
    }

    getReconnectDelay() {
        return this.exponentialBackoff
            ? Math.min(30 * 1000, this.reconnectInterval * Math.pow(2, this.reconnectAttempts)) // Cap at 30 seconds
            : this.reconnectInterval;
    }

        // New method to handle pings
    startPing(interval = 30000) {
        this.pingInterval = setInterval(() => {
            if (this.socket.readyState === WebSocket.OPEN) {
                this.sendMessage({ type: 'ping' });
            }
        }, interval);
    }

    stopPing() {
        clearInterval(this.pingInterval);
    }

    reconnectPromise() {
        return new Promise((resolve, reject) => {
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.removeEventListeners();
                this.socket.close();

                this.socket = new WebSocket(this.url);
                this.initializeEventListeners();

                // Increase reconnect attempt count
                this.reconnectAttempts++;

                // Resolve or reject based on WebSocket events
                const tempOnOpen = () => {
                    resolve(true);
                };
                const tempOnError = () => {
                    reject(false);
                };

                this.socket.addEventListener('open', tempOnOpen);
                this.socket.addEventListener('error', tempOnError);

                // Clean up listeners once resolved/rejected
                this.socket.onopen = () => {
                    this.socket.removeEventListener('error', tempOnError);
                    this.socket.onopen = null;
                };
                this.socket.onerror = () => {
                    this.socket.removeEventListener('open', tempOnOpen);
                    this.socket.onerror = null;
                };
            } else {
                reject(false);
            }
        });
    }
}

export {WebSocketClient, WebSocketManager};
