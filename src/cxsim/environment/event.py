from typing import Optional, List
from src.cxsim.agents.agent import Agent
from src.cxsim.prompts.prompt import PromptTemplate


class TimeStepTrigger:
    def __init__(
            self,
            time_step: int,
            episode: int = None
    ):
        self.time_step = time_step
        self.episode = episode

    def should_trigger(self, env):
        # Check if episode is specified and if it matches the current_episode
        if self.episode is not None and env.current_episode != self.episode:
            return False

        # If time_step is positive, check if it matches the current_step
        if self.time_step >= 0:
            return env.current_step == self.time_step
        # If time_step is negative, check if the current_step is abs(time_step) steps before the end
        else:
            return env.current_step == (env.total_steps + self.time_step)


class Event:
    def __init__(
            self,
            name: str,
            prompt,
            trigger: TimeStepTrigger,
            special_actions: List = None,
            included_agents: Optional[List[Agent]] = -1
    ):
        self.name: str = name
        self.prompt = prompt

        self.special_actions = special_actions

        self.trigger = trigger
        self.included_agents = included_agents

    def trigger_event(self):
        pass


class EventHandler:
    def __init__(self, environment):
        self.environment = environment
        self.events = []
        self.time_step_events = []

    def add_event(self, event: Event):
        if not isinstance(event, Event):
            raise ValueError("event must be of type Event")
        else:
            if isinstance(event.trigger, TimeStepTrigger):
                self.time_step_events.append(event)
                self.events.append(event)

    def step(self):
        for event in self.time_step_events:
            should_trigger = event.trigger.should_trigger(self.environment)
            if should_trigger:
                self.handle_event(event)

    def handle_event(self, event):
        pass
