"""Time ranges."""

__version__ = "1.0.1"

from ._datetimeranges import DatetimeRange, DatetimeRanges
from ._timeranges import TimeRange, TimeRanges, WeekRange

# TODO Maybe generate it programmatically?
__all__ = ["TimeRange", "TimeRanges", "WeekRange", "DatetimeRange", "DatetimeRanges"]
