

class Artifact:
    def __init__(self, name):
        self.name = name
        self.system_prompt = ""

        self.action_space_prompt = ""
        self.event_history = []

        self.environment = None
        self.agents = None

        self.action_space = []
        self.query_space = []

    def set_up(self):
        pass

    def execute_action(self, agent, action):
        pass

    def execute_query(self, agent, query):
        pass

    def step(self):
        pass

    def should_continue(self):
        return True

    def get_action_space(self):
        return self.action_space

    def get_action_space_prompt(self):
        return [action.create_prompt() for action in self.action_space]

    def get_query_space(self):
        return self.query_space

    def get_query_space_prompt(self):
        return [query.create_prompt() for query in self.query_space]

    def reset(self, environment):
        pass
