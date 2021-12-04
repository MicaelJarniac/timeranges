from datetime import datetime
from enum import Enum, unique


@unique
class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @classmethod
    def from_datetime(cls, dt: datetime) -> "Weekday":
        return cls(dt.weekday())
