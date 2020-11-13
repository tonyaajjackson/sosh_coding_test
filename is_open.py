import csv
import calendar

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


def parse_open_hours(hours_string):
    ranges = hours_string.split("  / ")
    print(ranges)


def weekday(input):
    if input[0:3] in list(calendar.day_abbr):
        return {
            "success": True,
            "day_as_int": list(calendar.day_abbr).index(input[0:3]),
            "rest": input[3:]
        }
    else:
        return {
            "success": False,
            "rest": input
        }


def test_weekday():
    fail_test = weekday("notaweekday")
    assert fail_test["success"] == False
    assert fail_test["rest"] == "notaweekday"

    pass_test = weekday("Mon-Fri")
    assert pass_test["success"] == True
    assert pass_test["day_as_int"] == 0
    assert pass_test["rest"] == "-Fri"


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
    fail_test = start_range("Mon")
    assert fail_test["success"] == False
    assert fail_test["rest"] == "Mon"

    pass_test = start_range("-Thu")
    assert pass_test["success"] == True
    assert pass_test["rest"] == "Thu"

def sequence(parsers):
    def apply_parsers(input):
        next = input

        for parser in parsers:
            result = parser(next)
            success = result["success"]
            rest = result["rest"]

            if not success:
                return {
                    "success": success,
                    "rest": rest
                }
            
            next = rest
        
        return {
            "success": True,
            "rest": next
        }

    return apply_parsers


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

    fail_input = "Mon?"
    fail_test = sequence(parsers)(fail_input)
    assert fail_test["success"] == False
    assert fail_test["rest"] == "?"


# Tests
test_weekday()
test_start_range()
test_sequence()
