from cxsim.examples import Smith1962Environment
import openai
import os


if __name__ == '__main__':
    openai.api_key = os.environ["openai_api_key"]

    env = Smith1962Environment(n_agents=25, model_id="gpt-3.5-turbo")

    env.test_one(plot_supply_demand=True, market_depth=0)


