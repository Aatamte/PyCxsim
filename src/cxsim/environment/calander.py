import datetime


class Calender:
    def __init__(self, step_timedelta: datetime.timedelta = datetime.timedelta(days=1)):
        self.step_timedelta = step_timedelta
        self.current_date = datetime.date.today()

    def step(self):
        self.current_date += self.step_timedelta
