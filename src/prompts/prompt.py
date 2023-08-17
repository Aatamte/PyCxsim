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


class ObservationPrompt:
    def __init__(self):
        pass

    def create(self):
        pass


class SystemPrompt:
    def __init__(self):
        self.simulation_description = Prompt(
            content="You are an agent participating in a multi-agent simulation."
        )
        self.artifact_prompts = [

        ]

    def create(self):

        return {
            "role": "system",
            "content": self.simulation_description.content
        }

    def insert(self):
        pass

    def add_artifact_prompt(self, artifact):
            self.artifact_prompts.append(
                {artifact.name: artifact.system_prompt}
            )

if __name__ == '__main__':
    prompt = ""
    print()

