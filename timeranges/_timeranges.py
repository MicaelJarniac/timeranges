from copy import deepcopy
from datetime import datetime, time, timedelta, tzinfo
from typing import Dict, Final, List, Optional, TypeVar

import attr

from ._types import Weekday

S_IN_H: Final = 3600
S_IN_M: Final = 60
US_IN_S: Final = 1000000


def time_in_microseconds(time: time) -> int:
    return (
        time.hour * S_IN_H + time.minute * S_IN_M + time.second
    ) * US_IN_S + time.microsecond


def subtract_times(first: time, second: time) -> timedelta:
    # Subtract two times
    assert first.tzinfo == second.tzinfo, "Timezones must match"
    return timedelta(
        microseconds=time_in_microseconds(first) - time_in_microseconds(second)
    )


_T_TimeRange = TypeVar("_T_TimeRange", bound="TimeRange")


@attr.define(order=True, on_setattr=attr.setters.validate)
class TimeRange:
    def _validate_start(
        instance: _T_TimeRange, attribute: attr.Attribute, start: time
    ) -> None:
        instance._validate_time(start)
        instance._validate_range(start, instance.end)

    def _validate_end(
        instance: _T_TimeRange, attribute: attr.Attribute, end: time
    ) -> None:
        instance._validate_time(end)
        instance._validate_range(instance.start, end)

    # Maybe use `None`?
    start: time = attr.ib(default=time.min, validator=_validate_start)
    end: time = attr.ib(default=time.max, order=False, validator=_validate_end)

    @staticmethod
    def _validate_time(time: time) -> None:
        if time.tzinfo is not None:
            raise ValueError(f"Time {time} has timezone info")

    @staticmethod
    def _validate_range(start: time, end: time) -> None:
        if start > end:
            raise ValueError(f"Start time {start} is after end time {end}")

    def validate(self) -> None:
        for t in [self.start, self.end]:
            self._validate_time(t)

        self._validate_range(self.start, self.end)

    def __attrs_post_init__(self) -> None:
        self.validate()

    def __contains__(self, t: time) -> bool:
        return self.start <= t <= self.end


@attr.define
class TimeRanges:
    time_ranges: List[TimeRange] = attr.Factory(list)

    def validate(self) -> None:
        for time_range in self.time_ranges:
            time_range.validate()

    def sort(self) -> None:
        self.validate()
        self.time_ranges.sort()

    def merge(self, interpolate: timedelta = timedelta(0)) -> None:
        assert interpolate >= timedelta(0), "Interpolation must be positive"
        self.sort()
        time_ranges = deepcopy(self.time_ranges)
        aux: List[TimeRange] = []
        # Merge overlapping time ranges
        for time_range in time_ranges:
            if not aux:
                aux.append(time_range)
                continue
            aux_last = aux[-1]
            if subtract_times(time_range.start, aux_last.end) <= interpolate:
                if time_range.end > aux_last.end:
                    aux_last.end = time_range.end
            else:
                aux.append(time_range)
        self.time_ranges = aux
        self.sort()

    def __attrs_post_init__(self) -> None:
        self.validate()

    def __contains__(self, t: time) -> bool:
        return any(t in time_range for time_range in self.time_ranges)


@attr.define
class WeekRange:
    day_ranges: Dict[Weekday, TimeRanges] = attr.Factory(dict)
    timezone: Optional[tzinfo] = None

    def validate(self) -> None:
        for day_range in self.day_ranges.values():
            day_range.validate()

    def merge(self, interpolate: timedelta = timedelta(0)) -> None:
        for day_range in self.day_ranges.values():
            day_range.merge(interpolate=interpolate)

    def __attrs_post_init__(self) -> None:
        self.validate()

    def __contains__(self, dt: datetime) -> bool:
        tz = self.timezone
        if tz is not None:
            dt = dt.astimezone(tz)
        weekday = Weekday.from_datetime(dt)
        day_range = self.day_ranges.get(weekday)
        if day_range is not None:
            return dt.time() in day_range
        return False
