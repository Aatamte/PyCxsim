from unittest.mock import MagicMock, patch
import unittest

from src.cxsim import Population, Agent


class TestPopulation(unittest.TestCase):

    def setUp(self):
        self.agent_mock = Agent()
        self.agent_mock.add = MagicMock()
        self.agent_mock.copy = MagicMock(return_value=self.agent_mock)

        self.population = Population(self.agent_mock, 3)

    def test_generate_agents_length(self):
        agents = self.population.generate_agents()
        self.assertEqual(len(agents), 3)

    def test_generate_agents_copy(self):
        self.population.generate_agents()

    def test_generate_agents_with_params(self):
        params = {"param1": "value1", "param2": "value2"}
        self.population.params = params
        agents = self.population.generate_agents()
        for agent in agents:
            self.assertEqual(agent.params, params)

    def test_generate_agents_with_action_restrictions(self):
        action_restrictions = ["restriction1", "restriction2"]
        self.population.action_restrictions = action_restrictions
        agents = self.population.generate_agents()
        for agent in agents:
            self.agent_mock.add.assert_called()

    def test_generate_agents_with_query_restrictions(self):
        query_restrictions = ["restriction1", "restriction2"]
        self.population.query_restrictions = query_restrictions
        agents = self.population.generate_agents()
        for agent in agents:
            self.assertEqual(agent.query_restrictions, query_restrictions)


if __name__ == "__main__":
    unittest.main()
