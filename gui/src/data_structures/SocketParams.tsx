
type WebSocketStatus = "connecting" | "open" | "closing" | "closed" | "unknown";


class SocketParams {
    public host: string = 'localhost';
    public port: number = 8765;
    public status: WebSocketStatus = "unknown"

    public environment_status: WebSocketStatus = "unknown"

    constructor() {
        this.host = 'localhost';
        this.port = 8765;
        this.status = "unknown"
        this.environment_status = "unknown"
    }

}


export default SocketParams;