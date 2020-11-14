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


def day_range(input):
    result = sequence(
        [
            weekday,
            start_range,
            weekday
        ]
    )(input)

    success = result["success"]
    rest = result["rest"]

    if success:
        end_day = result["stack"].pop()["day_as_int"]
        start_day = result["stack"].pop()["day_as_int"]

        stack = [
            {
                "days": list(range(start_day, end_day + 1))
            }
        ]
        # Make sure end_day is included in range

        return {
            "success": success,
            "rest": rest,
            "stack": stack
        }

    else:
        return {
            "success": False,
            "rest": input
        }


def test_day_range():
    fail_input = "Mon-Cat"
    fail_test = day_range(fail_input)
    assert fail_test["success"] == False
    assert fail_test["rest"] == fail_input

    pass_input = "Mon-Fri "
    pass_test = day_range(pass_input)
    assert pass_test["success"] == True
    assert pass_test["rest"] == " "
    assert pass_test["stack"] == [
        {
            "days": [0, 1, 2, 3, 4]
        }
    ]


def n_or_more(parser, n):
    def n_or_more_lambda(input):
        next = input
        stack = []
        n_success = 0
        
        while True:
            result = parser(next)
            success = result["success"]
            rest = result["rest"]

            if success:
                n_success += 1
            
            if "stack" in result:
                stack += result["stack"]

            if not success:
                if n_success > n:
                    return {
                        "success": True,
                        "rest": next,
                        "stack": stack
                    }
                else:
                    return {
                        "success": False,
                        "rest": input
                    }

            next = rest

    return n_or_more_lambda


def test_n_or_more():
    # Tests that should fail:
    zero_match_input = "NoWeekdaysHere"
    zero_match_test = n_or_more(weekday, 1)(zero_match_input)
    assert zero_match_test["success"] == False
    assert zero_match_test["rest"] == zero_match_input

    less_than_n_input = "MonBanana"
    less_than_n_test = n_or_more(weekday, 2)(less_than_n_input)
    assert less_than_n_test["success"] == False
    assert less_than_n_test["rest"] == less_than_n_input

    # Tests that should pass
    pass_input = "MonTueWedBanana"
    pass_test = n_or_more(weekday, 2)(pass_input)
    assert pass_test["success"] == True
    assert pass_test["rest"] == "Banana"
    assert pass_test["stack"] == [
        {
            "day_as_int": 0
        },
        {
            "day_as_int": 1
        },
        {
            "day_as_int": 2
        }
    ]

# Tests
test_weekday()
test_start_range()
test_space()
test_sequence()
test_either()
test_day_range()
test_n_or_more()
