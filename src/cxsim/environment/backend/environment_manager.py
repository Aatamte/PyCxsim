from cxsim.agents.agent import Agent


# methods

# init_agent
# update_agent

# init_artifact
# update_artifact

class TYPES:
    UPDATE = 1
    INIT = 0
    LOGS = 2


class EnvironmentManager:
    def __init__(self, environment):
        self.environment = environment
        self.incoming_types = {
            "play": self.play(),

        }

    def handle_message(self, message: dict):
        if message == "play":
            return self.play()
        elif message == "next":
            return self.next()
        elif message == "INIT":
            resp = self.agent_data()
            resp.append(self.get_init)
            return resp

## INITIALIZATION OF ELEMENTS ###
    def init_artifacts(self):
        response = []
        for artifact in self.environment.artifacts:
            response.append(
                {
                    "type": "INIT_ARTIFACTS",
                    "content": artifact.to_dict()
                }
            )
        return response

    def init_agents(self):
        response = []
        for agent in self.environment.agents:
            response.append(
                {
                    "type": "AGENT_INIT",
                    "content": agent.to_dict()
                }
            )

        return response

    def update_artifacts(self):
        response = []
        for name, artifact in self.environment.artifact_lookup.items():
            print(artifact)
            response.append(
                {
                    "type": "INIT_ARTIFACTS",
                    "content": artifact.to_dict()
                }
            )
        return response

# UPDATE ELEMENTS
    def logs(self):
        pass

    def play(self):
        self.environment.STATUS = 1
        return None

    def next(self):
        self.environment.STATUS = 2
        return None

    def pause(self):
        self.environment.STATUS = 0
        return None

    def update_agents(self):
        response = []
        for agent in self.environment.agents:
            response.append(
                {
                    "type": "AGENT_UPDATE",
                    "content": agent.to_dict()
                }
            )

        return response

    def agent_data(self):
        response = []
        for agent in self.environment.agents:
            response.append(
                {
                    "type": "AGENT_VARIABLES",
                    "content": agent.to_dict()
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
                "artifactNames": self.environment.artifact_names,
                "x_size": self.environment.x_size,
                "y_size": self.environment.y_size
            }
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
