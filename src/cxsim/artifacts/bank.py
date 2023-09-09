from src.cxsim import Artifact


class Bank(Artifact):
    def __init__(self, interest_rate: float = 2.0):
        super().__init__("Bank")
        self.interest_rate = interest_rate
        self.accounts = {}  # Map from Agent id to account balance
        self.loans = {}  # Map from Agent id to loan amount

    def execute(self, agent, action_details):
        action, amount = action_details
        if action == "deposit":
            self.deposit(agent, amount)
        elif action == "withdraw":
            self.withdraw(agent, amount)
        elif action == "loan":
            self.loan(agent, amount)

    def deposit(self, agent, amount):
        if agent.inventory.get_quantity('money') < amount:
            return  # Agent does not have enough money to deposit
        self.accounts[agent.id] = self.accounts.get(agent.id, 0) + amount
        agent.inventory.remove_item('money', amount)

    def withdraw(self, agent, amount):
        if self.accounts.get(agent.id, 0) < amount:
            return  # Not enough money in account
        self.accounts[agent.id] -= amount
        agent.inventory.add_item('money', amount)

    def loan(self, agent, amount):
        # Here we don't check the agent's creditworthiness
        # You might want to add such a check in a more detailed simulation
        self.loans[agent.id] = self.loans.get(agent.id, 0) + amount
        agent.inventory['money'] = amount

    def generate_interest(self):
        # Generate interest on both deposits and loans
        for agent_id, balance in self.accounts.items():
            self.accounts[agent_id] = balance * (1 + self.interest_rate)
        for agent_id, loan in self.loans.items():
            self.loans[agent_id] = loan * (1 + self.interest_rate)

    def generate_observations(self, agents):
        # Here we just return the account balance and loan amount as observations
        observations = {}
        for agent_id in set(list(self.accounts.keys()) + list(self.loans.keys())):
            observations[agent_id] = {
                'account_balance': self.accounts.get(agent_id, 0),
                'loan_amount': self.loans.get(agent_id, 0),
            }
        return observations

    def should_continue(self):
        # A bank might stop the simulation if it runs out of money
        # Here we just return True so the simulation always continues
        return True




