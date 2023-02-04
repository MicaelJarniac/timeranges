from datetime import time

from pytest import raises

from timeranges import TimeMap, TimeRange, TimeRanges


def test_timemap() -> None:
    timemap: TimeMap[int] = TimeMap(
        [
            (
                TimeRanges(
                    [TimeRange(time(5), time(10)), TimeRange(time(22), time(23))]
                ),
                0,
            ),
            (TimeRange(time(15), time(20)), 1),
        ]
    )
    assert len(timemap) == 2
    assert list(timemap.values()) == [0, 1]
    assert list(timemap.keys()) == list(timemap)
    assert timemap[time(6)] == 0
    assert timemap[time(16)] == 1
    assert timemap[time(22)] == 0
    with raises(KeyError):
        timemap[time(0)]

    timemap[TimeRange(time(0), time(1))] = 2
    assert len(timemap) == 3
    assert list(timemap.values()) == [0, 1, 2]
    assert timemap[time(0)] == 2

    del timemap[time(7)]
    assert len(timemap) == 2
    assert list(timemap.values()) == [1, 2]
    with raises(KeyError):
        timemap[time(6)]
