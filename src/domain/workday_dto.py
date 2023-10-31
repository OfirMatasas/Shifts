from dataclasses import dataclass
import datetime

@dataclass
class WorkdaySequence():

    day_names: list[str]
    day_dates: list[datetime.date]

    def __init__(self, day_names: list[str] = [], day_dates: list[datetime.date] = []):
        self.day_names: list[str] = day_names if len(day_names) > 0 else []
        self.day_dates: list[datetime.date] = day_dates if len(day_dates) > 0 else []