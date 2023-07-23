from src.core import Agent, Environment
from src.core import Marketplace, Market
from src.core import Dialogue
import time
import random
import h5py


class MyAgent(Agent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.starting_capital = 1000

    def select_action(self):
        actions = [("Market", ["socks", 100, 1]), ("Dialogue", ["default", "hello"])]
        action = random.choice(actions)
        self.action_queue.append(action)


def main():
    env = Environment()
    agent = MyAgent()
    agent2 = MyAgent()

    # add a market to the environment
    market = Market("socks")

    # add the ability for agents to speak to each other to the environment through messages
    dialogue = Dialogue()

    things = [agent, agent2, market, dialogue]

    # anything that is an <Agent> or <Artifact> class can be added to the environment
    env.add(things)

    env.max_episodes = 10
    env.max_steps = 10
    start = time.time()

    # RL
    env.reset()
    for step in range(env.max_steps):
        agent.select_action()
        should_continue = env.step()  # executing next action and gives agents the
        observation = agent.view_observation()

    end = time.time()

    print(end - start)


def print_items():
    def print_attrs(name, obj):
        print(name)
        for key, val in obj.attrs.items():
            print("    %s: %s" % (key, val))
        if isinstance(obj, h5py.Dataset):  # check if the object is a dataset
            print("    value:", obj[()])

    with h5py.File("env_record.hdf5", "r") as f:
        f.visititems(print_attrs)


if __name__ == '__main__':
    main()

