import Agent from "./agent";


export default class Environment {
    [key: string]: any; // Index signature
    public name: string;

    public currentStep: number;
    public maxSteps: number;

    public currentEpisode: number;
    public maxEpisodes: number;

    public x_size: number;
    public y_size: number;

    public agentNames: string[];
    public artifactNames: string[];

    public agents: Record<string, Agent>; // Using a dictionary (object) to store agents


  constructor() {
    this.name = "default";

    this.agentNames = [];
    this.agents = {};

    this.artifactNames = [];

    this.currentStep = 0
    this.maxSteps = 10;
    this.currentEpisode = 0;
    this.maxEpisodes = 10;
    this.x_size = 10;
    this.y_size = 10

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

  public addArtifact(name: string): void {
      this.artifactNames.push(name)
  }

  // ... other methods like removeAgent, addArtifact, etc.
}