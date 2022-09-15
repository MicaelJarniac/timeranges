from copy import deepcopy
from datetime import datetime, time, timedelta, timezone
from typing import List, TypeVar, Union

import attr

from ._base import BaseRange

_T_DatetimeRange = TypeVar("_T_DatetimeRange", bound="DatetimeRange")


@attr.define(order=True, on_setattr=attr.setters.validate)
class DatetimeRange(BaseRange):
    def _validate_start(
        instance: _T_DatetimeRange, attribute: attr.Attribute, start: datetime
    ) -> None:
        instance._validate_datetime(start)
        instance._validate_range(start, instance.end)

    def _validate_end(
        instance: _T_DatetimeRange, attribute: attr.Attribute, end: datetime
    ) -> None:
        instance._validate_datetime(end)
        instance._validate_range(instance.start, end)

    start: datetime = attr.ib(
        default=datetime.min.replace(tzinfo=timezone.utc), validator=_validate_start
    )
    end: datetime = attr.ib(
        default=datetime.max.replace(tzinfo=timezone.utc),
        order=False,
        validator=_validate_end,
    )

    @staticmethod
    def _validate_datetime(dt: datetime) -> None:
        if dt.tzinfo is None:
            raise ValueError(f"Datetime {dt} has no timezone information")

    @staticmethod
    def _validate_range(start: datetime, end: datetime) -> None:
        if start > end:  # This automatically ensures they're both offset-naive or aware
            raise ValueError(f"Start datetime {start} is after end datetime {end}")

    def validate(self) -> None:
        for dt in (self.start, self.end):
            self._validate_datetime(dt)

        self._validate_range(self.start, self.end)

    def __attrs_post_init__(self) -> None:
        self.validate()

    def _contains_datetime(self, other: datetime, /) -> bool:
        return self.start <= other <= self.end

    def _contains_datetime_range(self, other: "DatetimeRange", /) -> bool:
        scdt = self._contains_datetime
        return scdt(other.start) and scdt(other.end)

    _contains_types = Union[datetime, "DatetimeRange"]

    def contains(self, other: _contains_types, /) -> bool:
        if isinstance(other, datetime):
            return self._contains_datetime(other)
        elif isinstance(other, DatetimeRange):
            return self._contains_datetime_range(other)
        else:
            raise TypeError

    def __contains__(self, other: _contains_types) -> bool:
        return self.contains(other)


@attr.define
class DatetimeRanges(BaseRange):
    datetime_ranges: List[DatetimeRange] = attr.Factory(list)

    def validate(self) -> None:
        for datetime_range in self.datetime_ranges:
            datetime_range.validate()

    def sort(self) -> None:
        self.validate()
        self.datetime_ranges.sort()

    def merge(self, interpolate: timedelta = timedelta(0)) -> None:
        assert interpolate >= timedelta(0), "Interpolation must be positive"
        self.sort()
        datetime_ranges = deepcopy(self.datetime_ranges)
        aux: List[DatetimeRange] = []

        # Merge overlapping time ranges
        for datetime_range in datetime_ranges:
            if not aux:
                aux.append(datetime_range)
                continue
            aux_last = aux[-1]
            if (datetime_range.start - aux_last.end) <= interpolate:
                if datetime_range.end > aux_last.end:
                    aux_last.end = datetime_range.end
            else:
                aux.append(datetime_range)

        # TODO Interpolate to `time.max`

        self.datetime_ranges = aux
        self.sort()

    def __attrs_post_init__(self) -> None:
        self.validate()

    def __bool__(self) -> bool:
        return bool(self.datetime_ranges)

    def _contains_datetime(self, other: datetime, /) -> bool:
        return any(other in datetime_range for datetime_range in self.datetime_ranges)

    def _contains_datetime_range(self, other: DatetimeRange, /) -> bool:
        return any(other in datetime_range for datetime_range in self.datetime_ranges)

    def _contains_datetime_ranges(self, other: "DatetimeRanges", /) -> bool:
        return all(
            self._contains_datetime_range(datetime_range)
            for datetime_range in other.datetime_ranges
        )

    _contains_types = Union[time, DatetimeRange, "DatetimeRanges"]

    def contains(self, other: _contains_types, /) -> bool:
        if isinstance(other, datetime):
            return self._contains_datetime(other)
        elif isinstance(other, DatetimeRange):
            return self._contains_datetime_range(other)
        elif isinstance(other, DatetimeRanges):
            return self._contains_datetime_ranges(other)
        else:
            raise TypeError

    def __contains__(self, other: _contains_types) -> bool:
        return self.contains(other)
