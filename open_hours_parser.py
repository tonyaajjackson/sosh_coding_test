import calendar
from modular_datetime import ModularDatetime, datetime_in_range


def weekday(input):
    if input[0:3] in list(calendar.day_abbr):
        return {
            "success": True,
            "rest": input[3:],
            "stack": [
                {
                    "days": [list(calendar.day_abbr).index(input[0:3])]
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
    fail_result = weekday(fail_input)
    assert fail_result["success"] == False
    assert fail_result["rest"] == fail_input

    pass_result = weekday("Mon-Fri")
    assert pass_result["success"] == True
    assert pass_result["rest"] == "-Fri"
    assert pass_result["stack"] == [
        {
            "days": [0]
        }
    ]


def char(c):
    def char_lambda(input):
        if input[0] == c:
            return {
                "success": True,
                "rest": input[1:]
            }
        else:
            return {
                "success": False,
                "rest": input
            }

    return char_lambda


def test_char():
    fail_input = "Mon"
    fail_result = char("-")(fail_input)
    assert fail_result["success"] == False
    assert fail_result["rest"] == fail_input

    pass_result = char("-")("-Thu")
    assert pass_result["success"] == True
    assert pass_result["rest"] == "Thu"


def sequence(parsers):
    def sequence_lambda(input):
        next = input
        stack = []

        for parser in parsers:
            if next == "":
                return {
                    "success": False,
                    "rest": input
                }
            
            result = parser(next)
            if "stack" in result:
                stack += result["stack"]

            if not result["success"]:
                return {
                    "success": result["success"],
                    "rest": input
                }

            next = result["rest"]

        return {
            "success": True,
            "rest": next,
            "stack": stack
        }

    return sequence_lambda


def test_sequence():
    parsers = [
        weekday,
        char("-"),
        weekday
    ]

    pass_input = "Mon-Fri"
    pass_result = sequence(parsers)(pass_input)
    assert pass_result["success"] == True
    assert pass_result["rest"] == ""
    assert pass_result["stack"] == [
        {
            "days": [0]
        },
        {
            "days": [4]
        }
    ]

    fail_input = "Mon?"
    fail_result = sequence(parsers)(fail_input)
    assert fail_result["success"] == False
    assert fail_result["rest"] == fail_input


def either(parsers):
    def either_lambda(input):
        next = input
        stack = []

        for parser in parsers:
            result = parser(next)
            if "stack" in result:
                stack += result["stack"]

            if result["success"]:
                return {
                    "success": result["success"],
                    "rest": result["rest"],
                    "stack": stack
                }

            next = result["rest"]

        return {
            "success": False,
            "rest": input
        }

    return either_lambda


def test_either():
    parsers = [
        char(" "),
        weekday
    ]

    fail_input = "? Mon"
    fail_result = either(parsers)(fail_input)
    assert fail_result["success"] == False
    assert fail_result["rest"] == fail_input

    pass_input = "Mon "
    pass_result = either(parsers)(pass_input)
    assert pass_result["success"] == True
    assert pass_result["rest"] == " "
    assert pass_result["stack"] == [
        {
            "days": [0]
        }
    ]


def day_range(input):
    result = sequence(
        [
            weekday,
            char("-"),
            weekday
        ]
    )(input)

    if result["success"]:
        end_day = result["stack"].pop()["days"][0]
        start_day = result["stack"].pop()["days"][0]

        stack = [
            {
                "days": list(range(start_day, end_day + 1))
            }
        ]
        # Make sure end_day is included in range

        return {
            "success": result["success"],
            "rest": result["rest"],
            "stack": stack
        }

    else:
        return {
            "success": False,
            "rest": input
        }


def test_day_range():
    fail_input = "Mon-Cat"
    fail_result = day_range(fail_input)
    assert fail_result["success"] == False
    assert fail_result["rest"] == fail_input

    pass_input = "Mon-Fri "
    pass_result = day_range(pass_input)
    assert pass_result["success"] == True
    assert pass_result["rest"] == " "
    assert pass_result["stack"] == [
        {
            "days": [0, 1, 2, 3, 4]
        }
    ]


def n_or_more(parser, n):
    def n_or_more_lambda(input):
        stack = []

        if input == "":
            if n == 0:
                return {
                    "success": True,
                    "rest": input,
                    "stack": stack
                }
            else:
                return {
                    "success": False,
                    "rest": input
                }

        next = input
        n_success = 0

        while True:
            result = parser(next)

            if result["success"]:
                n_success += 1

            if "stack" in result:
                stack += result["stack"]

            if not result["success"] or result["rest"] == "":
                if n_success >= n:
                    return {
                        "success": True,
                        "rest": result["rest"],
                        "stack": stack
                    }
                else:
                    return {
                        "success": False,
                        "rest": input
                    }

            next = result["rest"]

    return n_or_more_lambda


def test_n_or_more():
    # Tests that should fail:
    zero_match_input = "NoWeekdaysHere"
    zero_match_result = n_or_more(weekday, 1)(zero_match_input)
    assert zero_match_result["success"] == False
    assert zero_match_result["rest"] == zero_match_input

    less_than_n_input = "MonBanana"
    less_than_n_result = n_or_more(weekday, 2)(less_than_n_input)
    assert less_than_n_result["success"] == False
    assert less_than_n_result["rest"] == less_than_n_input

    empty_string_input = ""
    empty_string_result = n_or_more(char("a"), 1)(empty_string_input)
    assert empty_string_result["success"] == False
    assert empty_string_result["rest"] == empty_string_input

    # Tests that should pass
    pass_with_tail_input = "MonTueWedBanana"
    pass_with_tail_result = n_or_more(weekday, 2)(pass_with_tail_input)
    assert pass_with_tail_result["success"] == True
    assert pass_with_tail_result["rest"] == "Banana"
    assert pass_with_tail_result["stack"] == [
        {
            "days": [0]
        },
        {
            "days": [1]
        },
        {
            "days": [2]
        }
    ]

    pass_without_tail_input = "aaaaaa"
    pass_without_tail_result = n_or_more(char("a"), 6)(pass_without_tail_input)
    assert pass_without_tail_result["success"] == True
    assert pass_without_tail_result["rest"] == ""

    n_equals_zero_on_empty_string_input = ""
    n_equals_zero_on_empty_string_result = n_or_more(
        char("a"), 0)(n_equals_zero_on_empty_string_input)
    assert n_equals_zero_on_empty_string_result["success"] == True
    assert n_equals_zero_on_empty_string_result["rest"] == ""
    assert n_equals_zero_on_empty_string_result["stack"] == []

    n_equals_zero_on_tail_input = "sdfg"
    n_equals_zero_on_tail_result = n_or_more(
        char("a"), 0)(n_equals_zero_on_tail_input)
    assert n_equals_zero_on_tail_result["success"] == True
    assert n_equals_zero_on_tail_result["rest"] == "sdfg"
    assert n_equals_zero_on_tail_result["stack"] == []


def days(input):
    result = sequence([
        either([
            day_range,
            weekday
        ]),
        n_or_more(
            either([
                day_range,
                weekday,
                char(","),
                char(" ")
            ]),
            n=1
        )
    ])(input)

    if not result["success"]:
        return {
            "success": False,
            "rest": input
        }

    stack = result["stack"]

    # Collate all days in the stack
    days_all = []
    for item in stack:
        days_all += item["days"]

    return {
        "success": result["success"],
        "rest": result["rest"],
        "stack": [
            {
                "days_all": days_all
            }
        ]
    }


def test_days():
    fail_input = " Mon"
    fail_result = days(fail_input)
    assert fail_result["success"] == False
    assert fail_result["rest"] == fail_input

    pass_input = "Mon-Tue, Thu, Sat-Sun 9:00"
    pass_result = days(pass_input)
    assert pass_result["success"] == True
    assert pass_result["rest"] == "9:00"
    assert pass_result["stack"] == [
        {
            "days_all": [0, 1, 3, 5, 6]
        }
    ]


def numeral(input):
    if input[0] in "0123456789":
        return {
            "success": True,
            "rest": input[1:],
            "stack": [
                {
                    "numeral": int(input[0])
                }
            ]
        }
    else:
        return {
            "success": False,
            "rest": input
        }


def test_numeral():
    fail_input = "a"
    fail_result = numeral(fail_input)
    assert fail_result["success"] == False
    assert fail_result["rest"] == fail_input

    pass_input = "55"
    pass_result = numeral(pass_input)
    assert pass_result["success"] == True
    assert pass_result["rest"] == "5"
    assert pass_result["stack"] == [
        {
            "numeral": 5
        }
    ]


def number(input):
    result = n_or_more(
        numeral,
        n=1
    )(input)

    if not result["success"]:
        return {
            "success": False,
            "rest": input
        }

    number_found = 0

    for (index, item) in enumerate(list(reversed(result["stack"]))):
        number_found += int(item["numeral"])*10**(index)

    return {
        "success": result["success"],
        "rest": result["rest"],
        "stack": [
            {"number_found": number_found}
        ]
    }


def test_number():
    fail_input = "aa"
    fail_result = number(fail_input)
    assert fail_result["success"] == False
    assert fail_result["rest"] == fail_input

    pass_single_input = "5a"
    pass_single_result = number(pass_single_input)
    assert pass_single_result["success"] == True
    assert pass_single_result["rest"] == "a"
    assert pass_single_result["stack"] == [
        {
            "number_found": 5
        }
    ]

    pass_double_input = "56a5"
    pass_double_result = number(pass_double_input)
    assert pass_double_result["success"] == True
    assert pass_double_result["rest"] == "a5"
    assert pass_double_result["stack"] == [
        {
            "number_found": 56
        }
    ]

    pass_triple_input = "567"
    pass_triple_result = number(pass_triple_input)
    assert pass_triple_result["success"] == True
    assert pass_triple_result["rest"] == ""
    assert pass_triple_result["stack"] == [
        {
            "number_found": 567
        }
    ]


def number_in_range(input, n, m):
    result = number(input)

    if not result["success"]:
        return {
            "success": False,
            "rest": input
        }

    number_found = result["stack"][0]["number_found"]

    if number_found < n or number_found >= m:
        return {
            "success": False,
            "rest": input
        }

    else:
        return {
            "success": True,
            "rest": result["rest"],
            "stack": [
                {
                    "number_found": number_found
                }
            ]
        }


def test_number_in_range():
    # Tests that should fail
    fail_input = "a"
    fail_result = number_in_range(fail_input, 0, 10)
    assert fail_result["success"] == False
    assert fail_result["rest"] == fail_input

    too_large_input = "13"
    too_large_result = number_in_range(too_large_input, 0, 13)
    assert too_large_result["success"] == False
    assert too_large_result["rest"] == too_large_input

    too_small_input = "4"
    too_small_result = number_in_range(too_small_input, 5, 12)
    assert too_small_result["success"] == False
    assert too_small_result["rest"] == too_small_input

    # Tests that should succeed
    pass_without_tail_input = "10"
    pass_without_tail_result = number_in_range(
        pass_without_tail_input, 0, 12)
    assert pass_without_tail_result["success"] == True
    assert pass_without_tail_result["rest"] == ""
    assert pass_without_tail_result["stack"] == [
        {
            "number_found": 10
        }
    ]

    pass_with_tail_input = "7c"
    pass_with_tail_result = number_in_range(pass_with_tail_input, 0, 12)
    assert pass_with_tail_result["success"] == True
    assert pass_with_tail_result["rest"] == "c"
    assert pass_with_tail_result["stack"] == [
        {
            "number_found": 7
        }
    ]


def hour(input):
    result = number_in_range(
        input,
        1,
        13
    )

    # Change "number_found" to "hour"
    if result["success"]:
        result["stack"].append(
            {"hour": result["stack"].pop()["number_found"]}
        )

    return result


def test_hour():
    fail_input = "16"
    fail_result = hour(fail_input)
    assert fail_result["success"] == False
    assert fail_result["rest"] == fail_input

    pass_input = "6a"
    pass_result = hour(pass_input)
    assert pass_result["success"] == True
    assert pass_result["rest"] == "a"
    assert pass_result["stack"] == [
        {
            "hour": 6
        }
    ]


def minute(input):
    result = number_in_range(
        input,
        0,
        60
    )

    # Change "number_found" to "minute"
    if result["success"]:
        result["stack"].append(
            {"minute": result["stack"].pop()["number_found"]}
        )

    return result


def test_minute():
    fail_input = "75"
    fail_result = minute(fail_input)
    assert fail_result["success"] == False
    assert fail_result["rest"] == fail_input

    pass_input = "38a"
    pass_result = minute(pass_input)
    assert pass_result["success"] == True
    assert pass_result["rest"] == "a"
    assert pass_result["stack"] == [
        {
            "minute": 38
        }
    ]


def string(search_string):
    def string_lambda(input):
        parsers = [char(c) for c in search_string]

        result = sequence(parsers)(input)

        if result["success"]:
            result["stack"] = [
                {
                    "string": search_string
                }
            ]

        return result
    return string_lambda


def test_string():
    search_string = "abcd"

    fail_input = "qwerty"
    fail_result = string(search_string)(fail_input)
    assert fail_result["success"] == False
    assert fail_result["rest"] == fail_input

    pass_input = "abcde"
    pass_result = string(search_string)(pass_input)
    assert pass_result["success"] == True
    assert pass_result["rest"] == "e"
    assert pass_result["stack"] == [
        {
            "string": search_string
        }
    ]


def time(input):
    result = sequence([
        either([
            sequence([
                hour,
                char(":"),
                minute
            ]),
            hour
        ]),
        char(" "),
        either([
            string("am"),
            string("pm")
        ])
    ])(input)

    if not result["success"]:
        return result

    is_pm = result["stack"].pop()["string"] == "pm"
    
    if "minute" in result["stack"][-1]:
        found_minute = result["stack"].pop()["minute"]
    else:
        found_minute = 0

    found_hour = result["stack"].pop()["hour"]

    if found_hour == 12:
        # PM spans [12, 1, 2, ... 10, 11].
        # Make PM actually span [1, 12]
        is_pm = not is_pm

    if is_pm:
        found_hour = (found_hour + 12) % 24
        # Convert to 24 hour clock with range [0, 23]

    found_time = ModularDatetime(0, found_hour, found_minute)

    return {
        "success": True,
        "rest": result["rest"],
        "stack": [
            {
                "time": found_time
            }
        ]
    }


def test_time():
    # Tests that should fail
    no_time_input = "abcde"
    no_time_result = time(no_time_input)
    assert no_time_result["success"] == False
    assert no_time_result["rest"] == no_time_input

    only_hour_input = "12cde"
    only_hour_result = time(only_hour_input)
    assert only_hour_result["success"] == False
    assert only_hour_result["rest"] == only_hour_input

    hour_and_min_input = "12:45 cde"
    hour_and_min_result = time(hour_and_min_input)
    assert hour_and_min_result["success"] == False
    assert hour_and_min_result["rest"] == hour_and_min_input

    # Tests that should pass
    single_digit_input = "1:02 am"
    single_digit_result = time(single_digit_input)
    assert single_digit_result["success"] == True
    assert single_digit_result["rest"] == ""
    assert single_digit_result["stack"] == [
        {
            "time": ModularDatetime(0, 1, 2)
        }
    ]

    single_digit_with_tail_input = "3:05 am banana"
    single_digit_with_tail_result = time(single_digit_with_tail_input)
    assert single_digit_with_tail_result["success"] == True
    assert single_digit_with_tail_result["rest"] == " banana"
    assert single_digit_with_tail_result["stack"] == [
        {
            "time": ModularDatetime(0, 3, 5)
        }
    ]

    double_digit_input = "10:56 am"
    double_digit_result = time(double_digit_input)
    assert double_digit_result["success"] == True
    assert double_digit_result["rest"] == ""
    assert double_digit_result["stack"] == [
        {
            "time": ModularDatetime(0, 10, 56)
        }
    ]

    pm_input = "6:24 pm"
    pm_result = time(pm_input)
    assert pm_result["success"] == True
    assert pm_result["rest"] == ""
    assert pm_result["stack"] == [
        {
            "time": ModularDatetime(0, 18, 24)
        }
    ]

    noon_pm_input = "12:56 pm"
    noon_pm_result = time(noon_pm_input)
    assert noon_pm_result["success"] == True
    assert noon_pm_result["rest"] == ""
    assert noon_pm_result["stack"] == [
        {
            "time": ModularDatetime(0, 12, 56)
        }
    ]

    midnight_am_input = "12:43 am"
    midnight_am_result = time(midnight_am_input)
    assert midnight_am_result["success"] == True
    assert midnight_am_result["rest"] == ""
    assert midnight_am_result["stack"] == [
        {
            "time": ModularDatetime(0, 0, 43)
        }
    ]

    no_minute_input = "9 am"
    no_minute_result = time(no_minute_input)
    assert no_minute_result["success"] == True
    assert no_minute_result["rest"] == ""
    assert no_minute_result["stack"] == [
        {
            "time": ModularDatetime(0, 9, 0)
        }
    ]


def time_range(input):
    result = sequence([
        time,
        string(" - "),
        time
    ])(input)

    if not result["success"]:
        return result

    close_time = result["stack"].pop()["time"]
    result["stack"].pop()  # Throw away " - "
    open_time = result["stack"].pop()["time"]

    return {
        "success": True,
        "rest": result["rest"],
        "stack": [
            {
                "open_time": open_time,
                "close_time": close_time
            }
        ]
    }


def test_time_range():
    # Tests that should fail
    fail_inputs = [
        "asdf",  # No valid input
        "9:45 am",  # Only one time
        "9:45 am - ",  # Only one time with separator
    ]

    for input in fail_inputs:
        result = time_range(input)
        assert result["success"] == False
        assert result["rest"] == input

    # Tests that should pass
    pass_without_tail_input = "9:45 am - 10:15 pm"
    pass_without_tail_result = time_range(pass_without_tail_input)
    assert pass_without_tail_result["success"] == True
    assert pass_without_tail_result["rest"] == ""
    assert pass_without_tail_result["stack"] == [
        {
            "open_time": ModularDatetime(0, 9, 45),
            "close_time": ModularDatetime(0, 22, 15)
        }
    ]

    pass_with_tail_input = "4:15 pm - 2:38 am Monday"
    pass_with_tail_result = time_range(pass_with_tail_input)
    assert pass_with_tail_result["success"] == True
    assert pass_with_tail_result["rest"] == " Monday"
    assert pass_with_tail_result["stack"] == [
        {
            "open_time": ModularDatetime(0, 16, 15),
            "close_time": ModularDatetime(0, 2, 38)
        }
    ]


# Tests
test_weekday()
test_char()
test_sequence()
test_either()
test_day_range()
test_n_or_more()
test_days()
test_numeral()
test_number()
test_number_in_range()
test_hour()
test_minute()
test_string()
test_time()
test_time_range()
