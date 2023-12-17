from cxsim.agents.agent import Agent


class EnvironmentManager:
    def __init__(self, environment):
        self.environment = environment

    def handle_message(self, message: dict):
        if message == "play":
            return self.play()
        elif message == "next":
            return self.next()
        elif message == "INIT":
            resp = self.agent_data()
            resp.append(self.get_init)
            return resp

    def play(self):
        self.environment.STATUS = 1
        return None

    def next(self):
        self.environment.STATUS = 2
        return None

    def get_agent_data(self, agent: Agent):
        content = {
            "name": agent.name,
            "x_pos": agent.x_pos,
            "y_pos": agent.y_pos,
            "messages": agent.io.text.full_messages,
            "inventory": agent.inventory.inventory,
            "parameters": agent.params
        }
        return content

    def agent_data(self):
        response = []
        for agent in self.environment.agents:
            response.append(
                {
                    "type": "AGENT_VARIABLES",
                    "content": self.get_agent_data(agent)
                }
            )

        return response

    @property
    def get_init(self):
        return {
            "type": "ENVIRONMENT_CHANGE",
            "content": {
                "name": self.environment.name,
                "currentEpisode": self.environment.current_episode,
                "currentStep": self.environment.current_step,
                "maxEpisodes": self.environment.max_episodes,
                "maxSteps": self.environment.max_steps,
                "agentNames": self.environment.agent_names,
                "x_size": self.environment.x_size,
                "y_size": self.environment.y_size
            }
        }

    @property
    def get_agent_names(self):
        return {
            "agent_names": self.environment.agents
        }

    @property
    def step_variables(self):
        """

        Returns:

        """
        resp = [
            {
                "type": "ENVIRONMENT_CHANGE",
                "content": {
                    "currentEpisode": self.environment.current_episode,
                    "currentStep": self.environment.current_step,
                    "maxEpisodes": self.environment.max_episodes,
                    "maxSteps": self.environment.max_steps
                }
            }
        ]

        agent_vars = self.agent_data()

        for ag in agent_vars:
            resp.append(ag)

        return resp

    def get_env_core_variables(self):
        return {
            "type": "ENVIRONMENT_CHANGE",
            "content": {
                "name": self.environment.name,
                "currentEpisode": self.environment.current_episode,
                "currentStep": self.environment.current_step,
                "maxEpisodes": self.environment.max_episodes,
                "maxSteps": self.environment.max_steps
            }
        }
