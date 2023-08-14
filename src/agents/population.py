from src.agents.agent import Agent


class Population:
    def __init__(
            self,
            agent: Agent,
            number_of_agents: int,
            params: dict
    ):
        self.number_of_agents: int = number_of_agents
        self.agent = agent
        self.params = params

    def generate_agents(self):
        population = []
        for idx in range(self.number_of_agents):
            agent = self.agent.copy()
            agent.params = self.params
            population.append(agent)

        return population
