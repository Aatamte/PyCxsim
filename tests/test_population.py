from unittest.mock import MagicMock, patch
import unittest

from src.cxsim.agents import Agent, Population


class TestPopulation(unittest.TestCase):

    def setUp(self):
        self.agent_mock = Agent()
        self.agent_mock.add = MagicMock()
        self.agent_mock.copy = MagicMock(return_value=self.agent_mock)

        self.population = Population(self.agent_mock, 3)


if __name__ == "__main__":
    unittest.main()
