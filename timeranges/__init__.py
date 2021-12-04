"""Time ranges."""

__version__ = "0.3.1"

from ._timeranges import TimeRange, TimeRanges, WeekRange
from ._types import Weekday

# TODO Maybe generate it programatically?
__all__ = ["TimeRange", "TimeRanges", "WeekRange", "Weekday"]
