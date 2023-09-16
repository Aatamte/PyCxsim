

class WorkingMemory:
    def __init__(self, agent):
        self.agent = agent
        self.content = "Nothing here yet"

    def show(self, step):
        self.agent.add_message("user", f"STEP {step}. It is your turn to make a query. Your WORKING MEMORY is: " + self.content)

    def add(self):
        pass

    def compress(self):
        pass
