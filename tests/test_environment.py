import unittest
from unittest.mock import MagicMock, patch
from cxsim import Environment, Agent
from cxsim.agents import Population
from cxsim.artifacts import Marketplace
from cxsim.environment.environment import UnsupportedItemType, Artifact


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_add_agent(self):
        agent = Agent()
        self.env.add_agent(agent)
        self.assertIn(agent, self.env.agents)

    def test_add_artifact(self):
        artifact = Marketplace()
        self.env.add_artifact(artifact)
        self.assertIn(artifact, self.env.artifacts)

    def test_add_unsupported(self):
        with self.assertRaises(UnsupportedItemType):
            self.env.add(123)  # Assuming int is not supported


if __name__ == "__main__":
    unittest.main()
