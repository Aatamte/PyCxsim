import dataclasses


def generate_prompt(cls):
    fields = dataclasses.fields(cls)
    field_strs = ", ".join([f'"{field.name}": <{field.type.__name__}>' for field in fields])
    method_str = f'{{"action": "{cls.__name__}", "action_parameters": {{{field_strs}}}}}'
    return method_str


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

    def set_up(self, environment):
        pass

    def process_action(self, agent, action):
        pass

    def process_query(self, agent, query):
        pass

    def step(self):
        pass

    def should_continue(self):
        return True

    def get_action_space(self):
        return self.action_space

    def get_action_space_prompt(self):
        return [generate_prompt(action) for action in self.action_space]

    def get_query_space(self):
        return self.query_space

    def get_query_space_prompt(self):
        return [query.create_prompt() for query in self.query_space]

    def reset(self, environment):
        pass
