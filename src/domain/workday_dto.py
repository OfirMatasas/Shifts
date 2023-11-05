from dataclasses import dataclass


@dataclass
class WorkdaySequence():

    day_names: list
    day_dates: list

    def __init__(self, day_names=[], day_dates=[]):
        self.day_names = day_names
        self.day_dates = day_dates
