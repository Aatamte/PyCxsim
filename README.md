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

## GUI

One of the unique (and cool!) features of Pycxsim is the embedded GUI.
The GUI is composed of a Control Panel, World, and Information window

![Image Description](./docs/assets/GUI_example.JPG)

## Examples

## Standard Artifacts

Below are the standard artifacts provided with the CAES package:

- [Marketplace](https://github.com/Aatamte/CAES/blob/main/src/caes/artifacts/marketplace.py)
  - Agents can trade goods with each other (capital <-> good transactions only)
- [Dialogue](https://github.com/Aatamte/CAES/blob/main/src/caes/artifacts/dialogue.py)
  - Messaging 
- Gridworld
  - Agents can move around the map
