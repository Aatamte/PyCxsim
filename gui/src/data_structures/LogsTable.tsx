
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
    message: string;
}

class LogsTable {
    private storageKey: string;
    private data: LogEntry[]; // Variable to hold the current logs

    constructor(storageKey: string = 'logs') {
        this.storageKey = storageKey;
        // Load existing logs from sessionStorage or initialize as an empty array
        const storedLogs = sessionStorage.getItem(this.storageKey);
        this.data = storedLogs ? JSON.parse(storedLogs) as LogEntry[] : [];
        // Ensure timestamp strings are converted back to Date objects
        this.data = this.data.map(log => ({
            ...log,
            timestamp: new Date(log.timestamp),
        }));
    }

    // Method to add a log entry
    addLog(level: LogLevel, message: string): void {
        const logEntry: LogEntry = {
            timestamp: new Date(),
            level,
            message,
        };
        const currentLogs = this.getLogs();
        currentLogs.push(logEntry);
        sessionStorage.setItem(this.storageKey, JSON.stringify(currentLogs));
    }

    // Method to retrieve all log entries
    getLogs(): LogEntry[] {
        return this.data; // Return the current logs stored in this.data
    }

   // Method to clear all log entries
    clearLogs(): void {
        this.data = []; // Clear the this.data array
        sessionStorage.removeItem(this.storageKey); // Clear sessionStorage
    }
}

export default LogsTable;
