


export default class Agent {
    [key: string]: any; // Index signature
    public name: string;
    public x_pos: number;
    public y_pos: number;

    constructor() {
          this.name = "default";
          this.x_pos = 1;
          this.y_pos = 5;
  }

  updateAgent(key: string, value: any) {
    if (key in this) {
        this[key] = value;
    } else {
        console.warn(`Key ${key} is not a valid property of Agent`);
    }
}

}