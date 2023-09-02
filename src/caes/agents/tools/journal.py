from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.caes.prompts.prompt import Prompt


class Journal:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.entries = {}
        self.titles = []
        self.vectorizer = TfidfVectorizer()

        self.prompt = Prompt(content="")

    def add_entry(self, title: str, content: str):
        if not title:
            raise ValueError("Title cannot be None or empty.")

        if title in self.entries:
            raise ValueError(f"An entry with title '{title}' already exists.")

        if len(self.entries) >= self.capacity:
            oldest_title = self.titles.pop(0)
            del self.entries[oldest_title]

        self.entries[title] = content
        self.titles.append(title)
        # Re-fit the vectorizer with the updated titles
        self.vectorizer.fit([t for t in self.titles if t])

    def retrieve_entry(self, title: str):
        if not title:
            raise ValueError("Title cannot be None or empty.")

        # If the title exists in entries, return it directly
        if title in self.entries:
            return self.entries[title]

        # Otherwise, use cosine similarity to find the most similar title
        title_vector = self.vectorizer.transform([title])
        entry_title_vectors = self.vectorizer.transform([t for t in self.titles if t])

        # Compute cosine similarities between the title and entry titles
        similarities = cosine_similarity(title_vector, entry_title_vectors).flatten()

        # Get the title of the most similar entry
        most_similar_title = self.titles[similarities.argmax()]
        return self.entries[most_similar_title]

    def remove_entry(self, title):
        if title in self.entries:
            self.titles.remove(title)
            del self.entries[title]

    def consolidate_entries(self):
        pass

    def __len__(self):
        return len(self.entries)


if __name__ == '__main__':
    # Example usage:
    journal = Journal(capacity=100)
    journal.add_entry("Cats and Kittens", "This is an entry about cats.")
    journal.add_entry("Dogs and Puppies", "This is an entry about dogs.")
    print(journal.retrieve_entry("Cats and Kittens"))  # "This is an entry about cats."
    print(journal.retrieve_entry("Kittens"))  # Should return the entry about cats based on similarity
