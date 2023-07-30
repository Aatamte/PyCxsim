import datetime


class Calender:
    def __init__(self, one_step_timedelta = datetime.timedelta(days=1)):
        self.delta = one_step_timedelta
        self.current_date = datetime.date.today()

    def step(self):
        self.current_date += self.delta
        print(self.current_date)