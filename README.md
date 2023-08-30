# CAES
Complex Adaptive Economic Simulator (CAES) is a modular framework to simulate agents acting in an environment within an economic context. It is a hybrid framework combining ideas from Complex Adaptive Systems (CAS), Reinforcement Learning (RL), and Agent Based Modelling  (ABM).

# Overview
The main components of CAES are the Environment, Agent, and Artifact. 

Environment: contains everything in the simulation

Agent: primary actor that can make decisions (Agent.execute_action()) and query the environment for information (Agent.execute_query()). Agents are built from the ground up to support LLM like GPT-3.5 and GPT-4. 

Artifact: 


# Quickstart

```Python
import os
import openai

from CAES import Environment, Marketplace
from CAES import Population
from CAES import OAIAgent


class MyAgent(OAIAgent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.set_starting_inventory(
            {"capital": 1000, "socks": 10}
        )

        self.params["max_price"] = 10

if __name__ == '__main__':
    openai.api_key = os.environ["open_ai_key"]

    env = Environment(visualization=True)

    buyer_population = Population(
        agent=MyAgent(),
        number_of_agents=2
    )

    seller_population = Population(
        agent=MyAgent(),
        number_of_agents=2
    )

    env.add(buyer_population)
    env.add(seller_population)

    marketplace = Marketplace()
    env.add(marketplace)

    env.step_delay = 2

    env.max_episodes = 1
    env.max_steps = 50

    # set up the environment
    env.set_up()

    for step in env.iter_steps():
        for agent in env.agents:
            print(agent.inventory)
        print(step)
        env.step()
```