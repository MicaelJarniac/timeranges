from datetime import datetime, time, timedelta, timezone

from pytest import raises
from timematic.enums import Weekday

from timeranges import TimeRange, TimeRanges, WeekRange


def test_timerange_invalid():
    with raises(ValueError):
        TimeRange(time(2), time(1))
    with raises(ValueError):
        TimeRange(time(1), time(2, tzinfo=timezone(timedelta(1))))
    with raises(ValueError):
        tz = timezone(timedelta(1))
        TimeRange(time(1, tzinfo=tz), time(2, tzinfo=tz))

    tr = TimeRange(time(1), time(2))
    with raises(ValueError):
        tr.start = time(3)
    with raises(ValueError):
        tr.end = time(0)
    assert tr == TimeRange(time(1), time(2))


def test_timerange_contains_time():
    timerange = TimeRange(time(2), time(4))
    yes = [time(2), time(3), time(4)]
    no = [time(1), time(5)]

    for t in yes:
        assert t in timerange
        assert timerange.contains(t)

    for t in no:
        assert t not in timerange
        assert not timerange.contains(t)


def test_timeranges_contains_time():
    timeranges = TimeRanges(
        [
            TimeRange(time(2), time(4)),
            TimeRange(time(5), time(7)),
        ]
    )
    yes = [time(2), time(3), time(4), time(5), time(6), time(7)]
    no = [time(1), time(4, 1), time(8)]

    for t in yes:
        assert t in timeranges
        assert timeranges.contains(t)

    for t in no:
        assert t not in timeranges
        assert not timeranges.contains(t)


def test_timerange_contains_timerange():
    timerange = TimeRange(time(2), time(8))
    yes = [
        TimeRange(time(3), time(4)),
        TimeRange(time(5), time(8)),
        TimeRange(time(2), time(8)),
    ]
    no = [
        TimeRange(time(1), time(3)),
        TimeRange(time(3), time(9)),
        TimeRange(time(1), time(9)),
    ]

    for tr in yes:
        assert tr in timerange
        assert timerange.contains(tr)
        assert timerange._contains_time_range(tr)

    for tr in no:
        assert tr not in timerange
        assert not timerange.contains(tr)
        assert not timerange._contains_time_range(tr)
