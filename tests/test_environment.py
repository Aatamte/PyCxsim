import unittest
from unittest.mock import MagicMock, patch
from src.cxsim import Environment, Agent, Population
from src.cxsim.environment.environment import UnsupportedItemType, Artifact, ArtifactController


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_init(self):
        self.assertEqual(self.env.name, "default environment")
        self.assertFalse(self.env.should_stop_simulation)
        self.assertIsInstance(self.env.artifact_controller, ArtifactController)
        # ... further assertions for attributes

    def test_add_agent(self):
        agent = Agent()
        self.env.add_agent(agent)
        self.assertIn(agent, self.env.agents)

    def test_add_artifact(self):
        artifact = Artifact("marketplace")
        self.env.add_artifact(artifact)
        # Assume artifact_controller has a method called has_artifact
        self.assertTrue(self.env.artifact_controller.has_artifact(artifact))

    def test_add_unsupported(self):
        with self.assertRaises(UnsupportedItemType):
            self.env.add(123)  # Assuming int is not supported

    def test_add_population(self):
        # Given
        agent_mock = MagicMock(spec=Agent)
        agent_mock.copy = MagicMock(return_value=agent_mock)

        population_size = 5
        population = Population(agent_mock, population_size)

        environment = Environment()

        # When
        environment.add(population)

        # Then
        #self.assertEqual(len(environment.agents), population_size)
        #agent_mock.copy.assert_called_exactly(population_size)

        # Also check if all added agents are instances of the Agent class
        #all_are_agents = all(isinstance(agent, Agent) for agent in environment.agents)
        #self.assertTrue(all_are_agents)

    def test_validate_agents(self):
        agent = Agent()
        agent.execute_action = MagicMock()
        agent.execute_query = MagicMock()
        self.env.add_agent(agent)
        # This should not raise any assertion error
        self.env.validate_agents()

    def test_validate_artifacts(self):
        artifact = Artifact("marketplace")
        artifact.execute_action = MagicMock()
        artifact.execute_query = MagicMock()
        self.env.add_artifact(artifact)
        # This should not raise any assertion error
        self.env.validate_artifacts()

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
