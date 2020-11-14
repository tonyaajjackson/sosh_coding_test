import csv
import calendar
from collections import deque

# Import file
with open("rest_hours.csv", newline="") as f:
    entries = list(csv.reader(f))

# Rearrange CSV into useful data structure
restaurants = []

for entry in entries:
    restaurants.append(
        {
            "name": entry[0],
            "hours_string": entry[1]
        }
    )


def weekday(input):
    if input[0:3] in list(calendar.day_abbr):
        return {
            "success": True,
            "rest": input[3:],
            "stack": [
                {
                    "day_as_int": list(calendar.day_abbr).index(input[0:3])
                }
            ]
        }
    else:
        return {
            "success": False,
            "rest": input
        }


def test_weekday():
    fail_input = "notaweekday"
    fail_test = weekday(fail_input)
    assert fail_test["success"] == False
    assert fail_test["rest"] == fail_input

    pass_test = weekday("Mon-Fri")
    assert pass_test["success"] == True
    assert pass_test["rest"] == "-Fri"
    assert pass_test["stack"] == [
        {
            "day_as_int": 0
        }
    ]


def start_range(input):
    if input[0] == "-":
        return {
            "success": True,
            "rest": input[1:]
        }
    else:
        return {
            "success": False,
            "rest": input
        }


def test_start_range():
    fail_input = "Mon"
    fail_test = start_range(fail_input)
    assert fail_test["success"] == False
    assert fail_test["rest"] == fail_input

    pass_test = start_range("-Thu")
    assert pass_test["success"] == True
    assert pass_test["rest"] == "Thu"


def space(input):
    if input[0] == " ":
        return {
            "success": True,
            "rest": input[1:]
        }
    else:
        return {
            "success": False,
            "rest": input
        }


def test_space():
    fail_input = "Mon"
    fail_test = space(fail_input)
    assert fail_test["success"] == False
    assert fail_test["rest"] == fail_input

    pass_test = space(" Thu")
    assert pass_test["success"] == True
    assert pass_test["rest"] == "Thu"


def sequence(parsers):
    def sequence_lambda(input):
        next = input
        stack = []

        for parser in parsers:
            result = parser(next)
            success = result["success"]
            rest = result["rest"]
            if "stack" in result:
                stack += result["stack"]

            if not success:
                return {
                    "success": success,
                    "rest": input
                }

            next = rest

        return {
            "success": True,
            "rest": next,
            "stack": stack
        }

    return sequence_lambda


def test_sequence():
    parsers = [
        weekday,
        start_range,
        weekday
    ]

    pass_input = "Mon-Fri"
    pass_test = sequence(parsers)(pass_input)
    assert pass_test["success"] == True
    assert pass_test["rest"] == ""
    assert pass_test["stack"] == [
        {
            "day_as_int": 0
        },
        {
            "day_as_int": 4
        }
    ]

    fail_input = "Mon?"
    fail_test = sequence(parsers)(fail_input)
    assert fail_test["success"] == False
    assert fail_test["rest"] == fail_input


def either(parsers):
    def either_lambda(input):
        next = input
        stack = []

        for parser in parsers:
            result = parser(next)
            success = result["success"]
            rest = result["rest"]
            if "stack" in result:
                stack += result["stack"]

            if success:
                return {
                    "success": success,
                    "rest": rest,
                    "stack": stack
                }

            next = rest

        return {
            "success": False,
            "rest": input
        }

    return either_lambda


def test_either():
    parsers = [
        space,
        weekday
    ]

    fail_input = "? Mon"
    fail_test = either(parsers)(fail_input)
    assert fail_test["success"] == False
    assert fail_test["rest"] == fail_input

    pass_input = "Mon "
    pass_test = either(parsers)(pass_input)
    assert pass_test["success"] == True
    assert pass_test["rest"] == " "
    assert pass_test["stack"] == [
        {
            "day_as_int": 0
        }
    ]


# Tests
test_weekday()
test_start_range()
test_space()
test_sequence()
test_either()
