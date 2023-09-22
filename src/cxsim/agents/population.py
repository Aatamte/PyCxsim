from src.cxsim.agents.agent import Agent
from src.cxsim.prompts.prompt import InitializationPrompt
import copy

class Population:
    def __init__(
            self,
            agent,
            number_of_agents: int,
            prompt: InitializationPrompt = None,
            params: dict = None,
            action_restrictions: list = None,
            query_restrictions: list = None,
            prompt_arguments: dict = None
    ):
        self.number_of_agents: int = number_of_agents
        self.agent = agent
        self.params = params
        self.action_restrictions = action_restrictions
        self.query_restrictions = query_restrictions
        self.prompt = prompt
        self.prompt_arguments = prompt_arguments

    def generate_agents(self):
        population = []
        for idx in range(self.number_of_agents):
            agent = self.agent()

            if self.params:
                agent.params = self.params

            if self.action_restrictions:
                for action_restriction in self.action_restrictions:

                    agent.add(action_restriction)

            if self.query_restrictions:
                agent.query_restrictions = self.query_restrictions

            # Assign a personalized InitializationPrompt to the agent
            if self.prompt:
                personalized_prompt = copy.deepcopy(self.prompt)
                for key, value in self.prompt_arguments.items():
                    personalized_prompt.set_variable(key, value)
                agent.prompt = personalized_prompt

            population.append(agent)

        return population
