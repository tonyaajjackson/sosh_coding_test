from mod import Mod
from datetime import datetime


class DatetimeModWeek:
    def __new__(self, day, hour, minute):
        assert (day >= 0 and day < 7), "Day must be between 0 and 6"
        assert (hour >= 0 and hour < 24), "Hour must be between 0 and 23"
        assert (minute >= 0 and minute < 60), "Minute must be between 0 and 59"

        # Value is in seconds for easy interchange with Unix Epoch format
        seconds_per_week = 7*24*60*60
        raw_datetime = day*24*60*60 + hour*60*60 + minute*60
        return Mod(raw_datetime, seconds_per_week)


def test_datetime_mod_week():
    # Tests that should fail
    invalid_inputs = [
        [-1, 10, 10, "Day"],
        [7, 23, 12, "Day"],
        [4, -1, 23, "Hour"],
        [6, 24, 56, "Hour"],
        [2, 13, -1, "Minute"],
        [1, 7, 60, "Minute"]
    ]

    for [d, h, m, msg] in invalid_inputs:
        try:
            DatetimeModWeek(d, h, m)
        except AssertionError as e:
            assert msg in e.args[0]

    # Tests that should pass
    one_day = DatetimeModWeek(1, 0, 0)
    one_hour = DatetimeModWeek(0, 1, 0)

    # Addition without overflow
    monday_9_04 = DatetimeModWeek(0, 9, 4)
    no_overflow_result = monday_9_04 + one_hour
    assert no_overflow_result == DatetimeModWeek(0, 10, 4)

    # Subtraction without underflow
    no_underflow_result = monday_9_04 - one_hour
    assert no_underflow_result == DatetimeModWeek(0, 8, 4)

    # Addition with overflow
    sunday_23_11 = DatetimeModWeek(6, 23, 11)
    overflow_result = sunday_23_11 + one_day
    assert overflow_result == DatetimeModWeek(0, 23, 11)

    # Subtraction with underflow
    underflow_result = monday_9_04 - one_day
    assert underflow_result == DatetimeModWeek(6, 9, 4)


class DatetimeModDay:
    def __new__(self, hour, minute):
        assert (hour >= 0 and hour < 24), "Hour must be between 0 and 23"
        assert (minute >= 0 and minute < 60), "Minute must be between 0 and 59"

        # Value is in seconds for easy interchange with Unix Epoch format
        seconds_per_day = 24*60*60
        raw_datetime = hour*60*60 + minute*60
        return Mod(raw_datetime, seconds_per_day)


def test_datetime_mod_day():
    # Tests that should fail
    invalid_inputs = [
        [-1, 23, "Hour"],
        [24, 56, "Hour"],
        [13, -1, "Minute"],
        [7, 60, "Minute"]
    ]

    for [h, m, msg] in invalid_inputs:
        try:
            DatetimeModDay(h, m)
        except AssertionError as e:
            assert msg in e.args[0]

    # Tests that should pass
    one_hour = DatetimeModDay(1, 0)

    # Addition without overflow
    time_9_04 = DatetimeModDay(9, 4)
    no_overflow_result = time_9_04 + one_hour
    assert no_overflow_result == DatetimeModDay(10, 4)

    # Subtraction without underflow
    no_underflow_result = time_9_04 - one_hour
    assert no_underflow_result == DatetimeModDay(8, 4)

    # Addition with overflow
    time_23_11 = DatetimeModDay(23, 11)
    overflow_result = time_23_11 + one_hour
    assert overflow_result == DatetimeModDay(0, 11)

    # Subtraction with underflow
    time_0_23 = DatetimeModDay(0, 25)
    underflow_result = time_0_23 - one_hour
    assert underflow_result == DatetimeModDay(23, 25)


def datetime_in_range(start, end, current):
    current_delta = (current - start)
    end_delta = (end - start)

    # If current == start, restaurant has just opened, therefore True
    # If current == end, restaurant has just closed, therefore False
    return current_delta < end_delta


def test_current_in_range():
    # No overflow
    test_inputs = [
        [
            # No overflow
            DatetimeModWeek(1, 0, 0),
            DatetimeModWeek(3, 0, 0)
        ],
        [
            # Overflow
            DatetimeModWeek(6, 0, 0),
            DatetimeModWeek(2, 0, 0)
        ]
    ]

    for [start, end] in test_inputs:
        # Just before
        assert datetime_in_range(
            start,
            end,
            start - DatetimeModWeek(1, 0, 0)
        ) == False

        # Start
        assert datetime_in_range(
            start,
            end,
            start
        ) == True

        # Midway
        assert datetime_in_range(
            start,
            end,
            start + DatetimeModWeek(1, 0, 0)
        ) == True

        # End
        assert datetime_in_range(
            start,
            end,
            end
        ) == False


# Tests
test_datetime_mod_week()
test_datetime_mod_day()
test_current_in_range()
