import unittest
from unittest.mock import MagicMock, patch
from src.cxsim import Environment, Agent
from src.cxsim.agents import Population
from src.cxsim.artifacts import Marketplace
from src.cxsim.environment.environment import UnsupportedItemType, Artifact


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

    def test_set_up(self):
        # This is a complex method, you might want to mock various calls or have fixture data to test against.
        # For simplicity, I'll just add an agent and an artifact and call set_up.
        agent = Agent()
        artifact = Artifact()
        self.env.add_agent(agent)
        self.env.add_artifact(artifact)

        agent.set_up = MagicMock()
        artifact.set_up = MagicMock()

        self.env.set_up()

        agent.set_up.assert_called_once()
        artifact.set_up.assert_called_once()

    # You should further test other methods and cases, including edge cases and error conditions.


if __name__ == "__main__":
    unittest.main()
