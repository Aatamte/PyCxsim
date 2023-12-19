


export default class Agent {
    [key: string]: any; // Index signature
    public name: string;
    public x_pos: number;
    public y_pos: number;

    public inventory: Record<string, any>;
    public parameters: Record<string, any>;
    public messages: Record<string, any>[];

    constructor() {
          this.name = "default";
          this.x_pos = 0;
          this.y_pos = 0;
          this.inventory = {}
          this.parameters = {}
          this.messages = []
  }

  init() {

  }

    updateAgent(key: string, value: any) {
        if (key in this) {
            // Attempt to parse the value if it's a string that looks like JSON
            if (typeof value === 'string' && this.isJsonString(value)) {
                console.log(key, value)
                try {
                    value = JSON.parse(value);
                } catch (e) {
                    console.warn(`Failed to parse value for key ${key}:`, e);
                }
            }
            this[key] = value;
        } else {
            console.warn(`Key ${key} is not a valid property of Agent`);
        }
    }

        private isJsonString(str: string): boolean {
        try {
            JSON.parse(str);
        } catch (e) {
            return false;
        }
        return true;
    }

}