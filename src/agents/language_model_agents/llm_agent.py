from src.agents.agent import Agent
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


class LanguageModelAgent(Agent):
    def __init__(self):
        super(LanguageModelAgent, self).__init__()
        self.n_unfollowed_actions = 0

    def retry_select_action(self):
        self.n_unfollowed_actions += 1
        self.select_action()

    def select_action(self):
        pass



