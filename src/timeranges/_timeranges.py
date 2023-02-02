from collections import defaultdict
from copy import copy, deepcopy
from datetime import datetime, time, timedelta, tzinfo
from functools import reduce
from itertools import product
from typing import DefaultDict, Dict, List, Optional, Type, TypeVar, Union, Iterator
from collections.abc import MutableMapping

import attr
from timematic.enums import Weekday
from timematic.utils import subtract_times

from ._base import BaseRange
from ._datetimeranges import DatetimeRange, DatetimeRanges

_T_TimeRange = TypeVar("_T_TimeRange", bound="TimeRange")


@attr.define(order=True, on_setattr=attr.setters.validate)
class TimeRange(BaseRange):
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
    def _validate_time(time: time, /) -> None:
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

    def _contains_time(self, other: time, /) -> bool:
        return self.start <= other <= self.end

    def _contains_time_range(self, other: "TimeRange", /) -> bool:
        sct = self._contains_time
        return sct(other.start) and sct(other.end)

    _contains_types = Union[time, "TimeRange"]

    def contains(self, other: _contains_types, /) -> bool:
        if isinstance(other, time):
            return self._contains_time(other)
        elif isinstance(other, TimeRange):
            return self._contains_time_range(other)
        else:
            raise TypeError

    def __contains__(self, other: _contains_types) -> bool:
        return self.contains(other)

    def intersection(self, other: "TimeRange", /) -> Optional["TimeRange"]:
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        return TimeRange(start, end) if start <= end else None

    def __and__(self, other: "TimeRange") -> Optional["TimeRange"]:
        return self.intersection(other)


_TimeRanges_contains_types = Union[time, TimeRange, "TimeRanges"]


@attr.define
class TimeRanges(BaseRange):
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

        # Interpolate to `time.max`
        if interpolate and subtract_times(time.max, aux[-1].end) <= interpolate:
            aux[-1].end = time.max

        self.time_ranges = aux
        self.sort()

    def __attrs_post_init__(self) -> None:
        self.validate()

    def __bool__(self) -> bool:
        return bool(self.time_ranges)

    def _contains_time(self, other: time, /) -> bool:
        return any(other in time_range for time_range in self.time_ranges)

    def _contains_time_range(self, other: TimeRange, /) -> bool:
        return any(other in time_range for time_range in self.time_ranges)

    def _contains_time_ranges(self, other: "TimeRanges", /) -> bool:
        return all(
            self._contains_time_range(time_range) for time_range in other.time_ranges
        )

    def contains(self, other: _TimeRanges_contains_types, /) -> bool:
        if isinstance(other, time):
            return self._contains_time(other)
        elif isinstance(other, TimeRange):
            return self._contains_time_range(other)
        elif isinstance(other, TimeRanges):
            return self._contains_time_ranges(other)
        else:
            raise TypeError

    def __contains__(self, other: _TimeRanges_contains_types) -> bool:
        return self.contains(other)

    def union(self, other: "TimeRanges", /) -> "TimeRanges":
        time_ranges_list = self.time_ranges + other.time_ranges
        time_ranges = TimeRanges(time_ranges_list)
        time_ranges.merge()
        return time_ranges

    def __or__(self, other: "TimeRanges") -> "TimeRanges":
        return self.union(other) if isinstance(other, TimeRanges) else NotImplemented

    def intersection(self, other: "TimeRanges", /) -> "TimeRanges":
        time_ranges_list: List[Optional[TimeRange]] = [
            a & b for a, b in product(self.time_ranges, other.time_ranges)
        ]

        time_ranges = TimeRanges([tr for tr in time_ranges_list if tr is not None])
        time_ranges.merge()
        return time_ranges

    def __and__(self, other: "TimeRanges") -> "TimeRanges":
        return self.intersection(other)


@attr.define(on_setattr=attr.setters.convert)
class WeekRange(BaseRange):
    def _convert_day_ranges(day_ranges: Dict[Weekday, TimeRanges]) -> DefaultDict[Weekday, TimeRanges]:  # type: ignore
        return defaultdict(TimeRanges, day_ranges)

    day_ranges: DefaultDict[Weekday, TimeRanges] = attr.ib(
        factory=dict, converter=_convert_day_ranges
    )
    timezone: Optional[tzinfo] = None

    def validate(self) -> None:
        for day_range in self.day_ranges.values():
            day_range.validate()

    def merge(self, interpolate: timedelta = timedelta(0)) -> None:
        for day_range in self.day_ranges.values():
            day_range.merge(interpolate=interpolate)

    def __attrs_post_init__(self) -> None:
        self.validate()

    def __bool__(self) -> bool:
        return any(self.day_ranges.values())

    def _assert_timezone(self, other: "WeekRange", /) -> None:
        tz = self.timezone
        otz = other.timezone
        ref = datetime(2000, 1, 1)
        # FIXME This isn't the best way to do it, but `pytz` is pain
        if tz == otz:
            return
        elif (
            tz is not None
            and otz is not None
            and tz.utcoffset(ref) == otz.utcoffset(ref)
        ):
            return
        raise ValueError(f"Incompatible timezones ({tz} and {otz})")

    def _contains_datetime(self, other: datetime, /) -> bool:
        tz = self.timezone
        if tz is not None:
            other = other.astimezone(tz)
        weekday = Weekday.from_datetime(other)
        return other.time() in self.day_ranges[weekday]

    def _contains_week_range(self, other: "WeekRange", /) -> bool:
        self._assert_timezone(other)

        return all(
            day_range in self.day_ranges[weekday]
            for weekday, day_range in other.day_ranges.items()
        )

    _contains_types = Union[datetime, "WeekRange"]

    def contains(self, other: _contains_types, /) -> bool:
        if isinstance(other, datetime):
            return self._contains_datetime(other)
        elif isinstance(other, WeekRange):
            return self._contains_week_range(other)
        else:
            raise TypeError

    def __contains__(self, other: _contains_types) -> bool:
        return self.contains(other)

    def union(self, other: "WeekRange", /) -> "WeekRange":
        self._assert_timezone(other)

        day_ranges = copy(self.day_ranges)
        for weekday, day_range in other.day_ranges.items():
            day_ranges[weekday] |= day_range

        return WeekRange(day_ranges, timezone=self.timezone)

    def __or__(self, other: "WeekRange") -> "WeekRange":
        return self.union(other) if isinstance(other, WeekRange) else NotImplemented

    def intersection(self, other: "WeekRange", /) -> "WeekRange":
        self._assert_timezone(other)

        week_range = WeekRange(timezone=self.timezone)
        for weekday, day_range in self.day_ranges.items():
            week_range.day_ranges[weekday] = day_range & other.day_ranges[weekday]

        return week_range

    def __and__(self, other: "WeekRange") -> "WeekRange":
        return self.intersection(other)

    _has_transition_types = Union["WeekRange", DatetimeRange, DatetimeRanges]

    def _has_transition_week_range(self, other: "WeekRange") -> bool:
        return bool(other not in self and other & self)

    def _has_transition_datetime_range(self, other: DatetimeRange) -> bool:
        other_week_range = WeekRange.from_datetime_range(
            other, replace_timezone=self.timezone
        )
        return self._has_transition_week_range(other_week_range)

    def _has_transition_datetime_ranges(self, other: DatetimeRanges) -> bool:
        other_week_range = WeekRange.from_datetime_ranges(
            other, replace_timezone=self.timezone
        )
        return self._has_transition_week_range(other_week_range)

    def has_transition(self, other: _has_transition_types) -> bool:
        if isinstance(other, WeekRange):
            return self._has_transition_week_range(other)
        elif isinstance(other, DatetimeRange):
            return self._has_transition_datetime_range(other)
        elif isinstance(other, DatetimeRanges):
            return self._has_transition_datetime_ranges(other)
        else:
            raise TypeError

    @classmethod
    def from_datetime_range(
        cls, datetime_range: DatetimeRange, /, replace_timezone: Optional[tzinfo] = None
    ) -> "WeekRange":
        start = datetime_range.start
        if replace_timezone is not None:
            start = start.astimezone(replace_timezone)

        tz = start.tzinfo
        end = datetime_range.end.astimezone(tz)

        date_start = start.date()
        date_end = end.date()

        week_range = cls(timezone=tz)

        d = date_start
        while d <= date_end:
            # TODO Skip unnecessary iterations if week is already full
            tr_start: Optional[time] = None
            tr_end: Optional[time] = None
            if d == date_start:
                tr_start = start.time()
            if d == date_end:
                tr_end = end.time()

            time_range = TimeRange()
            if tr_start is not None:
                time_range.start = tr_start
            if tr_end is not None:
                time_range.end = tr_end

            week_range.day_ranges[Weekday(d.weekday())] = TimeRanges([time_range])

            d += timedelta(days=1)

        return week_range

    @classmethod
    def from_datetime_ranges(
        cls, datetime_ranges: DatetimeRanges, replace_timezone: Optional[tzinfo] = None
    ) -> "WeekRange":
        week_ranges: list["WeekRange"] = [
            cls.from_datetime_range(datetime_range, replace_timezone=replace_timezone)
            for datetime_range in datetime_ranges.datetime_ranges
        ]

        return reduce(lambda a, b: a | b, week_ranges)


T = TypeVar("T")


# https://stackoverflow.com/a/19775773/11521074
@attr.define
class TimeMap(MutableMapping[TimeRanges, T]):
    time_map: Dict[TimeRanges, T] = attr.Factory(dict)

    def __getitem__(self, __key: _TimeRanges_contains_types) -> T:
        for k, v in self.time_map.items():
            if __key in k:
                return v
        raise KeyError(__key)

    def __setitem__(self, __key: TimeRanges, __value: T) -> None:
        if not isinstance(__key, TimeRanges):
            raise TypeError(
                f"Expected key of type {TimeRanges}, got {type(__key)} instead"
            )
        # TODO Add logic for detecting and merging overlaps
        self.time_map[__key] = __value

    def __delitem__(self, __key: _TimeRanges_contains_types) -> None:
        for k in self.time_map.keys():
            if __key in k:
                del self.time_map[k]
                return
        raise KeyError(__key)

    def __iter__(self) -> Iterator[TimeRanges]:
        yield from self.time_map.keys()

    def __len__(self) -> int:
        return len(self.time_map)
