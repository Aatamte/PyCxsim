type StorageKey = string; // Define a type for storage keys for better readability and future flexibility

class KVStorage<T> {
    public storage: Record<StorageKey, T>;

    constructor() {
        this.storage = {};
    }

    // Set a value for a given key
    set(key: StorageKey, value: T): KVStorage<T> {
        this.storage[key] = value;
        return this;
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
    clear(): KVStorage<T> {
        this.storage = {};
        
        return this
    }
}

export default KVStorage;
