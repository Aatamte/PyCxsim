

export default class Environment {
    [key: string]: any; // Index signature
    public name: string;

    public currentStep: number;
    public maxSteps: number;

    public currentEpisode: number;
    public maxEpisodes: number;

    public agentNames: string[];
    public artifactNames: string[];

  constructor() {
    this.name = "default";
    this.agentNames = [];
    this.artifactNames = [];

    this.currentStep = 0
    this.maxSteps = 10;
    this.currentEpisode = 0;
    this.maxEpisodes = 10;
  }

  updateEnvironment(key: string, value: any) {
    if (key in this) {
      this[key] = value;
    } else {
      console.warn(`Key ${key} is not a valid property of Environment`);
    }
  }

  // Example of an additional method
  public addAgent(name: string): void {
    this.agentNames.push(name);
  }

  public addArtifact(name: string): void {
      this.artifactNames.push(name)
  }

  // ... other methods like removeAgent, addArtifact, etc.
}