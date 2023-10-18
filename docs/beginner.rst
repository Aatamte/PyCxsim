Beginner's Guide
================

Welcome, newcomers! This guide is tailored for those who are new to PyCxsim and simulations in general.

Installation
------------

Before diving into simulations, let's get PyCxsim installed:

.. code-block:: bash

   pip install pycxsim

First Simulation
----------------

With PyCxsim installed, let's create a basic simulation using the `Environment` class:

.. code-block:: python

   from cxsim import Environment
   env = Environment(gui=True)
   env.set_up()
   for step in env.iter_steps():
       env.step()

This simple simulation sets up an environment and runs it for a default number of steps.

Next Steps
----------

Feeling confident? Move on to the `Intermediate Guide`_ to explore more features!

.. _Intermediate Guide: intermediate.rst
