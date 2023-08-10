from src.agents.agent import Agent
import openai
# NOTES
#
# a language model agent should have the following features:
#   - strict enforcement of following actions specified by the environment
#       - class would automatically recall select action if the agent took an invalid action
#
#
#
#
#
#
#


class OAIAgent(Agent):
    def __init__(self, model_id: str = "gpt-3.5-turbo-0613"):
        super(OAIAgent, self).__init__()
        self.model_id = model_id
        self.n_unfollowed_actions = 0

        self.language_model_logs = []

    def make_api_request(self):
        pass





class LanguageModelAgent(Agent):
    def __init__(self):
        super(LanguageModelAgent, self).__init__()
        self.n_unfollowed_actions = 0

    def retry_select_action(self):
        self.n_unfollowed_actions += 1
        self.select_action()

    def select_action(self):
        pass



if __name__ == '__main__':
    pass