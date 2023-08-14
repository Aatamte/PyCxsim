from dataclasses import dataclass


@dataclass
class Prompt:
    content: str

    def approximate_tokens(self):
        return len(self.content) * 4

    def calculate_tokens(self):
        return 0

    def merge(self, other):
        self.content += "\n"
        self.content += other.content



@dataclass
class SetupPrompt(Prompt):
    pass


if __name__ == '__main__':
    prompt = ""
    print()

