


export default class Artifact {
    [key: string]: any; // Index signature
    public name: string;

    constructor() {
        this.name = "default"
    }

    updateArtifact(key: string, value: any) {
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

    // Method to check if a string is a valid JSON string
    private isJsonString(str: string): boolean {
        try {
            JSON.parse(str);
            return true;
        } catch (e) {
            return false;
        }
    }
}