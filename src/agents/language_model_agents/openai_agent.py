from src.agents.language_model_agents.language_model_agent import LanguageModelAgent
import openai


class OAIAgent(LanguageModelAgent):
    def __init__(
            self,
            model_id: str = "gpt-3.5-turbo-0613"
    ):
        super(OAIAgent, self).__init__()
        self.model_id = model_id

        self.language_model_logs = []

    def receives_message(self, text):
        self.messages.append(
            {
                "role": "user",
                "content": text
            }
        )
        self.create_ChatCompletion()
        print(self.messages)

    def set_up(self):
        self.messages.append(self.system_prompt)
        self.create_ChatCompletion()
        print(self.messages)

    def create_ChatCompletion(self, ):
        response = openai.ChatCompletion.create(model=self.model_id, messages=self.messages, temperature=self.temperature)
        self.messages.append(
            {'role': response.choices[0].message.role, 'content': response.choices[0].message.content}
        )





