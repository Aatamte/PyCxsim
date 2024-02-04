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
    public name: string;

    public currentStep: number;
    public maxSteps: number;

    public currentEpisode: number;
    public maxEpisodes: number;

    public x_size: number;
    public y_size: number;

    public agents: Record<string, Agent>; // Using a dictionary (object) to store agents
    public artifacts: Record<string, Artifact>; // Using a dictionary (object) to store agents

    public agentQueue: string[];
    public status: string;

    public logs: LogEntry[]; // Logs data structure


    constructor() {
        this.name = "N/A";

        this.artifacts = {}
        this.agents = {}

        this.currentStep = 0
        this.maxSteps = 10;
        this.currentEpisode = 0;
        this.maxEpisodes = 10;
        this.x_size = 10;
        this.y_size = 10;

        this.agentQueue = [];
        this.status = "stopped";

        this.logs = []; // Initialize the logs array
    }

    clear() {
        // Reset step and episode counters
        this.name = "N/A"
        this.currentStep = 0;
        this.currentEpisode = 0;
        this.status = "stopped";

        // Clear agent-related data
        this.agents = {};

        // Clear artifact-related data
        this.artifacts = {};
    }


    updateEnvironment(key: string, value: any) {
        if (key in this) {
          this[key] = value;
        } else {
          console.warn(`Key ${key} is not a valid property of Environment`);
        }
    }

  // Example of an additional method
    public addAgent(agent: Agent): void {
        if (agent.name in this.agents) {
            console.warn(`Agent with name ${agent.name} already exists.`);
            return;
        }
        this.agents[agent.name] = agent;
    }

    public removeAgent(agentName: string): void {
        if (agentName in this.agents) {
            delete this.agents[agentName];
        } else {
            console.warn(`Agent with name ${agentName} does not exist.`);
        }
    }

    public addArtifact(artifact: Artifact): void {
        if (artifact.name in this.artifacts) {
            console.warn(`Agent with name ${artifact.name} already exists.`);
            return;
        }

        this.artifacts[artifact.name] = artifact;
    }

    public set(key: string, value: any): void {
        if (key in this) {
            this[key] = value;
        } else {
            console.warn(`Key '${key}' is not a valid property of Environment`);
        }
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
    public addLog(level: LogLevel, message: string): void {
        const logEntry: LogEntry = {
            timestamp: new Date(), // Current timestamp
            level: level,
            message: message,
        };
        this.logs.push(logEntry); // Add the log entry to the logs array
    }

        // Method to clear logs
    public clearLogs(): void {
        this.logs = []; // Reset the logs array
    }
}