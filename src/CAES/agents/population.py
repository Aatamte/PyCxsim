from src.CAES.agents.agent import Agent


class Population:
    def __init__(
            self,
            agent: Agent,
            number_of_agents: int,
            params: dict = None,
            action_restrictions: list = None,
            query_restrictions: list = None
    ):
        self.number_of_agents: int = number_of_agents
        self.agent = agent
        self.params = params
        self.action_restrictions = action_restrictions
        self.query_restrictions = query_restrictions

    def generate_agents(self):
        population = []
        for idx in range(self.number_of_agents):
            agent = self.agent.copy()

            if self.params:
                agent.params = self.params

            if self.action_restrictions:
                for action_restriction in self.action_restrictions:

                    agent.add(action_restriction)

            if self.query_restrictions:
                agent.query_restrictions = self.query_restrictions

            population.append(agent)

        return population
