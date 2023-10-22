from cxsim.examples import Smith1962Environment
import openai
import os


if __name__ == '__main__':
    openai.api_key = os.environ["openai_api_key"]

    env = Smith1962Environment(n_agents=25)

    env.test_one()


