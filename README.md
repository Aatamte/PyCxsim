# CAES
Complex Adaptive Economic Simulator (CAES) is a modular framework to simulate agents acting in an environment within an economic context. It is a hybrid framework combining ideas from Complex Adaptive Systems (CAS), Reinforcement Learning (RL), and Agent Based Modelling  (ABM).

# Overview
The main components of CAES are the Environment, Agent, and Artifact. 

Environment: contains everything in the simulation

Agent: primary actor that can make decisions (Agent.execute_action()) and query the environment for information (Agent.execute_query()). Agents are built from the ground up to support LLM like GPT-3.5 and GPT-4. 

Artifact: 


# Quickstart

```Python
from src import Environment

if __name__ == '__main__':
    steps = 1000

    # set the environment with a default environment
    # steps is given for debug purposes for now - will change in the future
    Env = SimpleEnvironment()
    Env.max_timesteps = steps

    action_space = Env.action_space
    state_space = Env.state_space

    # using four GatheringAgents in the environment
    agents = [GatheringAgent() for _ in range(4)]

    # provide the environment with the agents for rendering, random starting states, trading, etc
    Env.set_agents(agents)

    for episode in range(100000):
        state, info = Env.reset()

        for i in range(steps):
            # environment is fast - using sleep to slow it down
            time.sleep(0.25)

            actions = [agent.select_action(state) for agent in agents]
            state, rewards, done = Env.step(actions)

            if True in done:
                break

        print(episode, Env.cumulative_rewards)
```