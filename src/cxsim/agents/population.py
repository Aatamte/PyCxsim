from src.cxsim.prompts.prompt import PromptTemplate
import copy


class Population:
    def __init__(
            self,
            agent,
            number_of_agents: int,
            system_prompt: PromptTemplate = None,
            cognitive_prompt: PromptTemplate = None,
            decision_prompt: PromptTemplate = None,
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

        self.system_prompt = system_prompt
        self.prompt_arguments = prompt_arguments

        self.cognitive_prompt = cognitive_prompt
        self.decision_prompt = decision_prompt

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
            if self.system_prompt:
                if isinstance(self.system_prompt, PromptTemplate):
                    personalized_prompt = copy.deepcopy(self.system_prompt)
                    for key, value in self.prompt_arguments.items():
                        personalized_prompt.set_variable(key, value)
                    agent.system_prompt = personalized_prompt
                elif isinstance(self.system_prompt, str):
                    agent.system_prompt = self.system_prompt

            if self.cognitive_prompt:
                if isinstance(self.cognitive_prompt, PromptTemplate):
                    cognitive_prompt = copy.deepcopy(self.cognitive_prompt)
                    agent.cognitive_prompt = cognitive_prompt
                elif isinstance(self.cognitive_prompt, str):
                    agent.cognitive_prompt = self.cognitive_prompt

            if self.decision_prompt:
                if isinstance(self.decision_prompt, PromptTemplate):
                    agent.decision_prompt = copy.deepcopy(self.decision_prompt)
                elif isinstance(self.decision_prompt, str):
                    agent.decision_prompt = self.decision_prompt

            population.append(agent)

        return population
