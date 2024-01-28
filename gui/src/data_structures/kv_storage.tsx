type StorageKey = string; // Define a type for storage keys for better readability and future flexibility

class KVStorage<T> {
    private storage: Record<StorageKey, T>;

    constructor() {
        this.storage = {};
    }

    // Set a value for a given key
    set(key: StorageKey, value: T): void {
        this.storage[key] = value;
    }

    // Get a value by key, returns undefined if the key does not exist
    get(key: StorageKey): T | undefined {
        return this.storage[key];
    }

    // Check if a key exists in the storage
    has(key: StorageKey): boolean {
        return key in this.storage;
    }

    // Delete a value by key, returns true if the key existed and has been removed, or false if the key does not exist
    delete(key: StorageKey): boolean {
        if (this.has(key)) {
            delete this.storage[key];
            return true;
        }
        return false;
    }

    // Clear all key-value pairs in the storage
    clear(): void {
        this.storage = {};
    }
}

export default KVStorage;
