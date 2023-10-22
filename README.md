![PyCxsim Logo](docs/assets/pycxsim_full_logo.png)

[![docs](https://github.com/Aatamte/PyCxsim/workflows/docs/badge.svg)](https://Aatamte.github.io/PyCxsim/)
![Tests](https://github.com/Aatamte/PyCxsim/actions/workflows/python-tests.yml/badge.svg)

## Note

PyCxsim is still under active development. 

## Installation

You can install PyCxsim directly from the GitHub repository (>=Python 3.8):

```bash
python -m pip install git+https://github.com/Aatamte/PyCxsim.git
```

See the [Documentation](https://Aatamte.github.io/PyCxsim/).

## Overview

PyCxsim is a framework to simulate computational agents in a confined environment.

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
    env.add(Population(agent=MyAgent, number_of_agents=2))

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

One of the unique (and cool!) features of Pycxsim is the functioning GUI.
The GUI is composed of three parts:
1. Control Panel
2. World window
3. Information window

![Image Description](./docs/assets/GUI_example.JPG)

### Control Panel
The GUI allows users to:
- control the simulation
  - Resume: Start the simulation
  - Next Step: Only run the next step in the simulation
  - Pause:  the simulation
- view summary information
  - current step and max steps in the simulation
  - number of agents
  - number of artifacts

![Image Description](./docs/assets/GUI_control_panel.JPG)


### World window


![Image Description](./docs/assets/GUI_gridworld.JPG)


### Information window

The information window contains five tabs:
1. Environment (implemented, but limited)
2. Agents (implemented)
3. Artifacts (semi-implemented)
4. Settings (not implemented yet)
5. Logs (implemented)

![Image Description](./docs/assets/GUI_info_tab.JPG)


## Examples

## Standard Artifacts

Below are the standard artifacts provided with the CAES package:

- [Marketplace](https://github.com/Aatamte/CAES/blob/main/src/caes/artifacts/marketplace.py)
  - Agents can trade goods with each other (capital <-> good transactions only)
- [Dialogue](https://github.com/Aatamte/CAES/blob/main/src/caes/artifacts/dialogue.py)
  - Messaging 
- Gridworld
  - Agents can move around the map
