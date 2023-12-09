import random
from typing import List, Dict, Union, Type
from cxsim.io.text.prompts.prompt import PromptTemplate
import copy


class Population:
    def __init__(
            self,
            agent: Type,
            number_of_agents: int,
            agent_kargs: dict = None,
            agent_params: Dict = None,
            action_restrictions: List = None,
            query_restrictions: List = None,
            prompt_arguments: Dict = None,
            agent_inventory: Dict = None,
            resample: Dict[str, bool] = None
    ):
        self.number_of_agents = number_of_agents
        self.agent = agent
        self.agent_kargs = agent_kargs
        self.agent_params = agent_params
        self.action_restrictions = action_restrictions
        self.query_restrictions = query_restrictions
        self.prompt_arguments = prompt_arguments
        self.agent_inventory = agent_inventory
        self.resample = resample if resample else {}
        self.pre_calculated_values = {}

        if self.number_of_agents != 0:
            for item, value in self.agent_inventory.items():
                if item in self.resample and not self.resample[item]:
                    if hasattr(value, 'rvs'):  # Check if it has an 'rvs' method
                        self.pre_calculated_values[item] = [value.rvs() for _ in range(self.number_of_agents)]
            self.pre_calculated_params = {}

            for item, value in self.agent_params.items():
                if item in self.resample and not self.resample[item]:
                    if hasattr(value, 'rvs'):  # Check if it has an 'rvs' method
                        self.pre_calculated_params[item] = [value.rvs() for _ in range(self.number_of_agents)]

        self.population = self.generate_agents()

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
            agent = self.agent(**self.agent_kargs).copy()
            self.generate_inventory(agent)
            self.apply_restrictions(agent)
            self.generate_params(agent)
            population.append(agent)
        return population

    def __getitem__(self, index):
        return self.population[index]

    def __setitem__(self, index, value):
        self.population[index] = value

    def __delitem__(self, index):
        del self.population[index]

    def __len__(self):
        return len(self.population)

    def __iter__(self):
        return iter(self.population)

    def append(self, item):
        self.population.append(item)

    def extend(self, items):
        self.population.extend(items)

    def insert(self, index, item):
        self.population.insert(index, item)

    def remove(self, item):
        self.population.remove(item)

    def pop(self, index=-1):
        return self.population.pop(index)

    def index(self, item, start=0, end=None):
        return self.population.index(item, start, end if end is not None else len(self))

    def count(self, item):
        return self.population.count(item)

    def sort(self, key=None, reverse=False):
        self.population.sort(key=key, reverse=reverse)

    def reverse(self):
        self.population.reverse()

    def clear(self):
        self.population.clear()

    def shuffle(self):
        random.shuffle(self.population)

    def __add__(self, other):
        new_agent_population = Population(self.agent, 0)
        new_agent_population.extend(self.population)  # Extend with the current population

        if isinstance(other, Population):
            new_agent_population.extend(other.population)  # Extend with the other AgentPopulation
        elif isinstance(other, list):
            new_agent_population.extend(other)  # Extend with a list of agents
        else:
            raise TypeError(f"Unsupported type: {type(other)}")

        return new_agent_population

