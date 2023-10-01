from typing import List, Dict, Union, Type
from src.cxsim.prompts.prompt import PromptTemplate
import copy
import scipy


class Population:
    def __init__(
            self,
            agent: Type,
            number_of_agents: int,
            system_prompt: Union[PromptTemplate, str] = None,
            cognitive_prompt: Union[PromptTemplate, str] = None,
            decision_prompt: Union[PromptTemplate, str] = None,
            agent_params: Dict = None,
            action_restrictions: List = None,
            query_restrictions: List = None,
            prompt_arguments: Dict = None,
            agent_inventory: Dict = None,
            resample: Dict[str, bool] = None
    ):
        self.number_of_agents = number_of_agents
        self.agent = agent
        self.agent_params = agent_params
        self.action_restrictions = action_restrictions
        self.query_restrictions = query_restrictions
        self.system_prompt = system_prompt
        self.prompt_arguments = prompt_arguments
        self.cognitive_prompt = cognitive_prompt
        self.decision_prompt = decision_prompt
        self.agent_inventory = agent_inventory
        self.resample = resample if resample else {}
        self.pre_calculated_values = {}
        for item, value in self.agent_inventory.items():
            if item in self.resample and not self.resample[item]:
                if hasattr(value, 'rvs'):  # Check if it has an 'rvs' method
                    self.pre_calculated_values[item] = [value.rvs() for _ in range(self.number_of_agents)]
        self.pre_calculated_params = {}

        for item, value in self.agent_params.items():
            if item in self.resample and not self.resample[item]:
                if hasattr(value, 'rvs'):  # Check if it has an 'rvs' method
                    self.pre_calculated_params[item] = [value.rvs() for _ in range(self.number_of_agents)]

    def generate_inventory(self, agent):
        starting_inventory = {}
        if self.agent_inventory:
            for item, value in self.agent_inventory.items():
                if item in self.resample and not self.resample[item]:
                    # Use the pre-calculated value if resampling is not allowed
                    starting_inventory[item] = self.pre_calculated_values[item].pop(0)
                elif isinstance(value, list):
                    starting_inventory[item] = value.pop(0)
                elif hasattr(value, 'rvs'):
                    # Sample a new value if resampling is allowed or not specified
                    starting_inventory[item] = value.rvs()
                else:
                    # Use the fixed value
                    starting_inventory[item] = value
            agent.inventory.set_starting_inventory(starting_inventory)

    def generate_params(self, agent):
        if self.agent_params:
            for item, value in self.agent_params.items():
                if item in self.resample and not self.resample[item]:
                    # Use the pre-calculated value if resampling is not allowed
                    agent.params[item] = self.pre_calculated_params[item].pop(0)

                elif isinstance(value, list):
                    agent.params[item] = value.pop(0)

                elif hasattr(value, 'rvs'):
                    # Sample a new value if resampling is allowed or not specified
                    agent.params[item] = value.rvs()
                else:
                    # Use the fixed value
                    agent.params[item] = value

    def apply_restrictions(self, agent):
        if self.action_restrictions:
            for action_restriction in self.action_restrictions:
                agent.add(action_restriction)
        if self.query_restrictions:
            agent.query_restrictions = self.query_restrictions

    def set_prompts(self, agent):
        if self.system_prompt:
            agent.system_prompt = self._prepare_prompt(self.system_prompt)
        if self.cognitive_prompt:
            agent.cognitive_prompt = self._prepare_prompt(self.cognitive_prompt)
        if self.decision_prompt:
            agent.decision_prompt = self._prepare_prompt(self.decision_prompt)

    def _prepare_prompt(self, prompt):
        if isinstance(prompt, PromptTemplate):
            personalized_prompt = copy.deepcopy(prompt)
            for key, value in self.prompt_arguments.items():
                personalized_prompt.set_variable(key, value)
            return personalized_prompt
        elif isinstance(prompt, str):
            return prompt

    def generate_agents(self):
        population = []
        for _ in range(self.number_of_agents):
            agent = self.agent().copy()
            self.generate_inventory(agent)
            self.apply_restrictions(agent)
            self.generate_params(agent)
            self.set_prompts(agent)
            population.append(agent)
        return population
