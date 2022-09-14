from datetime import datetime, timezone

from pytest import raises

from timeranges import DatetimeRange, DatetimeRanges


def utc(*args, **kwargs) -> datetime:
    kwargs["tzinfo"] = timezone.utc
    return datetime(*args, **kwargs)


def test_datetime_range_invalid():
    with raises(ValueError):
        DatetimeRange(datetime(2022, 1, 1), datetime(2022, 2, 2))
    with raises(ValueError):
        DatetimeRange(utc(2022, 2, 2), utc(2022, 1, 1))


def test_datetime_range_contains_invalid():
    datetime_range = DatetimeRange(utc(2022, 1, 1), utc(2022, 2, 2))

    with raises(TypeError):
        1 in datetime_range


def test_datetime_range_contains_datetime():
    datetime_range = DatetimeRange(utc(2022, 1, 1), utc(2022, 2, 2))
    yes = [utc(2022, 1, 1), utc(2022, 1, 2), utc(2022, 2, 2)]
    no = [utc(2021, 1, 1), utc(2022, 2, 3)]

    for dt in yes:
        assert dt in datetime_range
        assert datetime_range.contains(dt)

    for dt in no:
        assert dt not in datetime_range
        assert not datetime_range.contains(dt)


def test_datetime_range_contains_datetime_range():
    datetime_range = DatetimeRange(utc(2022, 1, 1), utc(2022, 2, 2))
    yes = [
        DatetimeRange(utc(2022, 1, 1), utc(2022, 1, 2)),
        DatetimeRange(utc(2022, 2, 1), utc(2022, 2, 2)),
    ]
    no = [
        DatetimeRange(utc(2021, 1, 1), utc(2023, 1, 1)),
        DatetimeRange(utc(2022, 3, 3), utc(2022, 4, 4)),
        DatetimeRange(utc(2022, 2, 1), utc(2022, 2, 3)),
    ]

    for dt in yes:
        assert dt in datetime_range
        assert datetime_range.contains(dt)

    for dt in no:
        assert dt not in datetime_range
        assert not datetime_range.contains(dt)
