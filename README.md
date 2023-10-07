![PyCxsim Logo](docs/assets/pycxsim_full_logo.png)

# PyCxsim Documentation
[![docs](https://github.com/Aatamte/PyCxsim/workflows/docs/badge.svg)](https://Aatamte.github.io/PyCxsim/)
![Tests](https://github.com/Aatamte/PyCxsim/actions/workflows/python-tests.yml/badge.svg)
## Installation

As the PyCxsim package is currently in development and not yet available on PyPI, you can install it directly from the GitHub repository (>=Python 3.8):

```bash
pip install git+https://github.com/Aatamte/PyCxsim.git
```

## Overview

PyCxsim is a framework designed to simulate interactions between agents and artifacts within a defined environment.

A high-level overview of the core components of the simulation:
- Environment
- Agents
- Artifacts


## Components

### 1. Environment

**Definition**: 
The `Environment` represents the main context of the simulation where agents and artifacts interact. It manages the state of the simulation and facilitates interactions between agents and artifacts.

**Key Responsibilities**:
- Managing agents and artifacts: The environment keeps track of all agents and artifacts within the simulation.
- Facilitating interactions: It processes agent actions, queries, and ensures smooth interactions between agents and artifacts.

**Core Methods**:
- `run()`: Starts the simulation
- `process_turn(agent: Agent)`: Processes the actions of a given agent during its turn.


### 2. Artifact

**Definition**: 
The `Artifact` represents objects or entities within the simulation that agents can interact with. It provides interfaces for actions and queries and maintains its own state.

**Key Responsibilities**:
- Maintaining state: Each artifact has its own state, which can change based on interactions or over time.
- Providing interaction interfaces: Artifacts define the actions that can be performed on them.

**Core Methods**:
- `process_action(agent: Agent, action)`: Processes an action performed by an agent on the artifact.
- `step()`: Executes a step or update for the artifact, potentially changing its state or triggering events.

### 3. Agent

**Definition**: 
The `Agent` represents individual actors in the simulation. They can perform actions, make queries, and interact with artifacts and the environment based on their state and capabilities.

**Key Responsibilities**:
- Maintaining state and capabilities: Agents have their own state, inventory, and set of capabilities that determine their actions and interactions.
- Interacting with the environment and artifacts: Agents can perform actions on artifacts, make queries, and process observations.

**Core Methods**:
- `decide()`: Determines and performs an action based on the agent's state, observations, and strategy.

# Quickstart

```Python
import os
import openai

from cxsim import Environment
from cxsim.artifacts import Marketplace
from cxsim.agents import OAIAgent, Population


class MyAgent(OAIAgent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.set_starting_inventory(
            {
                "capital": 1000,
                "socks": 10
            }
        )


if __name__ == '__main__':
    openai.api_key = os.environ["open_ai_key"]

    # Define the environment, and enable the gui
    env = Environment(gui=True)

    # add an agent
    env.add(MyAgent())

    # or add a population of agents
    env.add(Population(agent=MyAgent(), number_of_agents=2))

    # add a pre-configured artifact or your own artifact
    marketplace = Marketplace(infer_goods_from_agents=True)
    env.add(marketplace)

    # similar to reinforcement learning styled environments, you can specify maximum episodes and steps
    env.max_episodes = 1
    env.max_steps = 50

    # set up the environment (done adding stuff to the environment)
    env.set_up()

    for step in env.iter_steps():
        env.step()
```

## GUI


## Standard Artifacts

Below are the standard artifacts provided with the CAES package:

- [marketplace](https://github.com/Aatamte/CAES/blob/main/src/caes/artifacts/marketplace.py)
- [dialogue](https://github.com/Aatamte/CAES/blob/main/src/caes/artifacts/dialogue.py)
