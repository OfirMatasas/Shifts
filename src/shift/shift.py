from datetime import datetime, timedelta


class Shift:
    def __init__(self, day: str = None, start_time: datetime = None, shift_duration: int = 3):
        self.day = day
        self.start_time = start_time
        self.end_time = start_time + timedelta(hours=shift_duration)
        self.member = None

    def __str__(self):
        return f"{self.start_time.hour:02}:00-{self.end_time.hour:02}:00"

    def __eq__(self, other):
        return other is not None and self.day == other.day and self.start_time == other.start_time and self.end_time == other.end_time
    
    def is_same_day(self, other):
        return self.day == other.day
    
    def is_same_time(self, other):
        return self.start_time == other.start_time and self.end_time == other.end_time

    def get_member(self):
        return self.member if self.member else None
