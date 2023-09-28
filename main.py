import os
import openai

from src.cxsim import Environment
from src.cxsim.agents import Population, OAIAgent
from src.cxsim.artifacts.gridworld import Gridworld
from src.cxsim.artifacts.dialogue import Dialogue
from src.cxsim.prompts.prompt import PromptTemplate


class MyAgent(OAIAgent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.set_starting_inventory(
            {"capital": 10000}
        )


def main():
    openai.api_key = os.environ["openai_api_key"]

    env = Environment(gui=True)

    pop = Population(
        agent=MyAgent,
        number_of_agents=3,
        system_prompt=PromptTemplate("src/cxsim/prompts/system_prompt.txt"),
        cognitive_prompt=PromptTemplate("src/cxsim/prompts/cognitive_prompt.txt"),
        decision_prompt=PromptTemplate("src/cxsim/prompts/decision_prompt.txt"),
        prompt_arguments={"role": "goal-follower"}
    )
    env.add(pop)

    gridworld = Gridworld(5)
    env.add(gridworld)

    env.add(Dialogue())

    env.step_delay = 5

    env.max_episodes = 1
    env.max_steps = 50

    # prepare the environment to be run
    env.prepare()

    for step in env.iter_steps():
        print(step)
        env.step()


if __name__ == '__main__':
    main()
