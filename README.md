# CAES Simulation Documentation

## Overview

The CAES (Complex Adaptive Economic Simulator) is a framework designed to simulate interactions between agents and artifacts within a defined environment. This document provides a high-level overview of the core components of the simulation.

## Components

### 1. Environment

**Definition**: 
The `Environment` represents the main context of the simulation where agents and artifacts interact. It manages the state of the simulation and facilitates interactions between agents and artifacts.

**Key Responsibilities**:
- Managing agents and artifacts: The environment keeps track of all agents and artifacts within the simulation.
- Facilitating interactions: It processes agent actions, queries, and ensures smooth interactions between agents and artifacts.

**Core Methods**:
- `process_turn(agent: Agent)`: Processes the actions and queries of a given agent during its turn.


### 2. Artifact

**Definition**: 
The `Artifact` represents objects or entities within the simulation that agents can interact with. It provides interfaces for actions and queries and maintains its own state.

**Key Responsibilities**:
- Maintaining state: Each artifact has its own state, which can change based on interactions or over time.
- Providing interaction interfaces: Artifacts define the actions that can be performed on them and the queries that can retrieve information about them.

**Core Methods**:
- `process_action(agent: Agent, action)`: Processes an action performed by an agent on the artifact.
- `process_query(agent: Agent, query)`: Processes a query made by an agent about the artifact.
- `step()`: Executes a step or update for the artifact, potentially changing its state or triggering events.

### 3. Agent

**Definition**: 
The `Agent` represents individual actors in the simulation. They can perform actions, make queries, and interact with artifacts and the environment based on their state and capabilities.

**Key Responsibilities**:
- Maintaining state and capabilities: Agents have their own state, inventory, and set of capabilities that determine their actions and interactions.
- Interacting with the environment and artifacts: Agents can perform actions on artifacts, make queries, and process observations.

**Core Methods**:
- `execute_action()`: Determines and performs an action based on the agent's state, observations, and strategy.
- `execute_query()`: Determines and makes a query based on the agent's state and observations.

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


Environment:
The Environment represents the simulation's main context where agents and artifacts interact. It manages the state of the simulation, including the current step, episode, and other parameters. The environment provides methods to add agents and artifacts, process agent actions and queries, and control the simulation's progression. It also integrates with visualization tools and handles the flow of information between agents and artifacts.

Key Responsibilities:

Managing agents and artifacts.
Processing agent actions and queries.
Controlling the simulation's progression (steps and episodes).
Handling communication and information flow.
Integrating with visualization tools.
Artifact:
The Artifact represents objects or entities within the simulation environment that agents can interact with. Artifacts have a defined set of actions that can be performed on them and queries that can retrieve information about them. Each artifact has its own state, behavior, and set of interactions that it supports.

Key Responsibilities:

Maintaining its own state and behavior.
Defining and processing actions and queries.
Interacting with agents and the environment.
Agent:
The Agent represents individual actors or entities within the simulation that can perform actions, make queries, and interact with artifacts and the environment. Agents have their own state, inventory, and set of capabilities. They can execute actions, make queries, and process observations based on the environment's state and their interactions with artifacts.

Key Responsibilities:

Maintaining its own state, inventory, and capabilities.
Executing actions and making queries.
Processing observations and information from the environment and artifacts.
Interacting with artifacts and the environment.