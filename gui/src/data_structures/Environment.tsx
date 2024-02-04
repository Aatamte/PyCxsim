import Agent from "./agent";
import Artifact from "./artifact";

enum LogLevel {
    DEBUG = "DEBUG",
    INFO = "INFO",
    WARNING = "WARNING",
    ERROR = "ERROR",
    CRITICAL = "CRITICAL"
}

interface LogEntry {
    timestamp: Date;
    level: LogLevel;
    message: string;
}

export default class Environment {
    [key: string]: any; // Index signature
    public name: string = "N/A";

    public currentStep: number = 0
    public maxSteps: number = 10

    public currentEpisode: number = 0;
    public maxEpisodes: number = 10;

    public x_size: number = 10
    public y_size: number = 10

    public agents: Record<string, Agent> = {}
    public artifacts: Record<string, Artifact> = {}

    public agentQueue: string[] = []
    public status: string = "Stopped"

    public logs: LogEntry[] = [];


    constructor(environment?: Partial<Environment>) {
        // Initialize from existing environment instance if provided
        if (environment) {
            Object.assign(this, environment);
        } else {
            // Default initialization
            this.name = "N/A";
            this.agents = {};
            this.artifacts = {};
            this.currentStep = 0;
            this.maxSteps = 10;
            this.currentEpisode = 0;
            this.maxEpisodes = 10;
            this.x_size = 10;
            this.y_size = 10;
            this.agentQueue = [];
            this.status = "stopped";
            this.logs = [];
        }
    }

    clear() {
        return new Environment(); // Return a new instance with default values
    }

  // Example of an additional method
    public addAgent(agent: Agent): Environment {
        if (agent.name in this.agents) {
            console.warn(`Agent with name ${agent.name} already exists.`);
            return this;
        }
        this.agents[agent.name] = agent;
        return this;
    }

    public removeAgent(agentName: string): void {
        if (agentName in this.agents) {
            delete this.agents[agentName];
        } else {
            console.warn(`Agent with name ${agentName} does not exist.`);
        }
    }

    public addArtifact(artifact: Artifact): Environment {
        if (artifact.name in this.artifacts) {
            console.warn(`Agent with name ${artifact.name} already exists.`);
            return this;
        }

        this.artifacts[artifact.name] = artifact;
        return this;
    }

    public set(key: string, value: any): Environment {
        this[key] = value;
        if (key in this) {
        } else {
            console.warn(`Key '${key}' is not a valid property of Environment`);
            return this;
        }
        return this;
    }

    // Use a getter to dynamically get agent names
    public get agentNames(): string[] {
        return Object.keys(this.agents);
    }

    // Use a getter to dynamically get artifact names
    public get artifactNames(): string[] {
        return Object.keys(this.artifacts);
    }


    // Method to add a log entry
    public addLog(level: LogLevel, message: string): Environment {
        const logEntry: LogEntry = {
            timestamp: new Date(), // Current timestamp
            level: level,
            message: message,
        };
        this.logs.push(logEntry); // Add the log entry to the logs array

        return this;
    }

        // Method to clear logs
    public clearLogs(): void {
        this.logs = []; // Reset the logs array
    }
}