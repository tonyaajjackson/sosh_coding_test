import calendar
from modular_datetime import DatetimeModWeek, datetime_in_range
from string import printable, digits


# Primitive parsers
def char(c):
    def char_lambda(input):
        if input == "":
            return None

        if input[0] == c:
            return ([], input[1:])
        else:
            return None

    return char_lambda


def test_char():
    fail_inputs = [
        "",
        "Mon"
    ]
    for fail_input in fail_inputs:
        assert char("-")(fail_input) is None

    # Without tail
    for c in printable:
        (data, rest) = char(c)(c)
        assert data == []
        assert rest == ""

    # With tail
    tail = " tail"
    for c in printable:
        (data, rest) = char(c)(c + tail)
        assert data == []
        assert rest == tail


def numeral(input):
    if input == "":
        return None

    if input[0] in "0123456789":
        return (
            [
                {
                    "numeral": int(input[0])
                }
            ],
            input[1:]
        )
    else:
        return None


def test_numeral():
    fail_inputs = [
        "",
        "a"
    ]
    for fail_input in fail_inputs:
        assert numeral(fail_input) is None

    for num in digits:
        (data, rest) = numeral(num)
        assert data == [
            {
                "numeral": int(num)
            }
        ]
        assert rest == ""

    tail = " orange"
    for num in digits:
        (data, rest) = numeral(num + tail)
        assert data == [
            {
                "numeral": int(num)
            }
        ]
        assert rest == tail


def weekday(input):
    if input == "":
        return None

    if input[0:3] in list(calendar.day_abbr):
        day_num = list(calendar.day_abbr).index(input[0:3])

        return (
            [
                {
                    "days": [DatetimeModWeek(day_num, 0, 0)]
                }
            ],
            input[3:],
        )
    else:
        return None


def test_weekday():
    fail_inputs = [
        "",
        "notaweekday"
    ]
    for fail_input in fail_inputs:
        assert weekday(fail_input) is None

    for (index, day) in enumerate(list(calendar.day_abbr)):
        (data, rest) = weekday(day)
        assert data == [
            {
                "days": [
                    DatetimeModWeek(index, 0, 0)
                ]
            }
        ]
        assert rest == ""

    tail = "-Fri"
    for (index, day) in enumerate(list(calendar.day_abbr)):
        (data, rest) = weekday(day + tail)
        assert data == [
            {
                "days": [
                    DatetimeModWeek(index, 0, 0)
                ]
            }
        ]
        assert rest == tail


# Combinators
def sequence(parsers):
    def sequence_lambda(rest):
        stack = []

        for parser in parsers:
            if result := parser(rest):
                (data, rest) = result

                if data:
                    stack += data
            else:
                return None

        return (stack, rest)
    return sequence_lambda


def test_sequence():
    parsers = [
        weekday,
        char("-"),
        weekday
    ]

    fail_inputs = [
        "",
        "Mon?"
    ]
    for fail_input in fail_inputs:
        assert sequence(parsers)(fail_input) is None

    pass_input = "Mon-Fri"
    (data, rest) = sequence(parsers)(pass_input)
    assert data == [
        {
            "days": [DatetimeModWeek(0, 0, 0)]
        },
        {
            "days": [DatetimeModWeek(4, 0, 0)]
        }
    ]
    assert rest == ""


def either(parsers):
    def either_lambda(rest):
        for parser in parsers:
            if result := parser(rest):
                return result

        return None
    return either_lambda


def test_either():
    parsers = [
        char(" "),
        weekday
    ]

    fail_inputs = [
        "",
        "? Mon"
    ]
    for fail_input in fail_inputs:
        assert either(parsers)(fail_input) is None

    pass_first_input = " Mon"
    (data, rest) = either(parsers)(pass_first_input)
    assert data == []
    assert rest == "Mon"

    pass_second_input = "Mon "
    (data, rest) = either(parsers)(pass_second_input)
    assert data == [
        {
            "days": [0]
        }
    ]
    assert rest == " "


def n_or_more(parser, n):
    def n_or_more_lambda(rest):
        stack = []
        n_success = 0

        while True:
            if result := parser(rest):
                (data, rest) = result
                n_success += 1

                if data:
                    stack += data
            else:
                if n_success >= n:
                    return (stack, rest)
                else:
                    return None

    return n_or_more_lambda


def test_n_or_more():
    # Tests that should fail:
    fail_inputs = [
        "",
        "a",
        "ab"
    ]
    for fail_input in fail_inputs:
        assert n_or_more(char("a"), 2)(fail_input) is None

    # Tests that should pass
    pass_without_tail_input = "aaaaaa"
    (data, rest) = n_or_more(char("a"), 6)(pass_without_tail_input)
    assert data == []
    assert rest == ""

    pass_with_tail_input = "aaaaaaBanana"
    (data, rest) = n_or_more(char("a"), 6)(pass_with_tail_input)
    assert data == []
    assert rest == "Banana"

    pass_with_return_data_input = "MonTueWed"
    (data, rest) = n_or_more(weekday, 2)(pass_with_return_data_input)
    assert data == [
        {
            "days": [DatetimeModWeek(0, 0, 0)]
        },
        {
            "days": [DatetimeModWeek(1, 0, 0)]
        },
        {
            "days": [DatetimeModWeek(2, 0, 0)]
        }
    ]
    assert rest == ""

    n_equals_zero_on_empty_string_input = ""
    (data, rest) = n_or_more(
        char("a"), 0)(n_equals_zero_on_empty_string_input)
    assert data == []
    assert rest == ""

    n_equals_zero_on_tail_input = "sdfg"
    (data, rest) = n_or_more(
        char("a"), 0)(n_equals_zero_on_tail_input)
    assert data == []
    assert rest == "sdfg"


# Combined parsers
def day_range(input):
    if result := sequence(
        [
            weekday,
            char("-"),
            weekday
        ]
    )(input):
        (data, rest) = result
        start_day = data[0]["days"][0]
        end_day = data[1]["days"][0]

        # Make range with modular arithmetic
        one_day = DatetimeModWeek(1, 0, 0)
        current_day = start_day
        days = []

        # Add one_day to include end_day in generated range
        while current_day != (end_day + one_day):
            days.append(current_day)
            current_day += one_day

        data = [
            {
                "days": days
            }
        ]

        return (data, rest)
    else:
        return None


def test_day_range():
    fail_input = "Mon-Cat"
    assert day_range(fail_input) is None

    pass_without_tail_input = "Wed-Sat"
    (data, rest) = day_range(pass_without_tail_input)
    assert data == [
        {
            "days": [
                DatetimeModWeek(2, 0, 0),
                DatetimeModWeek(3, 0, 0),
                DatetimeModWeek(4, 0, 0),
                DatetimeModWeek(5, 0, 0),
            ]
        }
    ]
    assert rest == ""

    pass_with_tail_input = "Mon-Fri "
    (data, rest) = day_range(pass_with_tail_input)
    assert data == [
        {
            "days": [
                DatetimeModWeek(0, 0, 0),
                DatetimeModWeek(1, 0, 0),
                DatetimeModWeek(2, 0, 0),
                DatetimeModWeek(3, 0, 0),
                DatetimeModWeek(4, 0, 0),
            ]
        }
    ]
    assert rest == " "

    pass_with_overflow_input = "Sat-Tue"
    (data, rest) = day_range(pass_with_overflow_input)
    assert data == [
        {
            "days": [
                DatetimeModWeek(5, 0, 0),
                DatetimeModWeek(6, 0, 0),
                DatetimeModWeek(0, 0, 0),
                DatetimeModWeek(1, 0, 0),
            ]
        }
    ]
    assert rest == ""


def days(rest):
    if result := sequence([
        either([
            day_range,
            weekday
        ]),
        n_or_more(
            sequence([
                string(", "),
                either([
                    day_range,
                    weekday
                ])
            ]),
            n=0
        )
    ])(rest):
        (data, rest) = result

        # Collate all days in the stack
        days_all = []
        for item in data:
            # Discard any separators that ended up in the stack
            if "days" in item:
                days_all += item["days"]

        return (
            [
                {
                    "days_all": days_all
                }
            ],
            rest
        )
    else:
        return None


def test_days():
    # Tests that should fail
    fail_inputs = [
        "",
        " Mon"
    ]
    for fail_input in fail_inputs:
        assert days(fail_input) is None

    # Tests that should pass
    single_day_input = "Wed"
    (data, rest) = days(single_day_input)
    assert data == [
        {
            "days_all": [DatetimeModWeek(2, 0, 0)]
        }
    ]
    assert rest == ""

    day_range_input = "Mon-Fri"
    (data, rest) = days(day_range_input)
    assert data == [
        {
            "days_all": [
                DatetimeModWeek(0, 0, 0),
                DatetimeModWeek(1, 0, 0),
                DatetimeModWeek(2, 0, 0),
                DatetimeModWeek(3, 0, 0),
                DatetimeModWeek(4, 0, 0),
            ]
        }
    ]
    assert rest == ""

    days_input = "Mon-Wed, Fri"
    (data, rest) = days(days_input)
    assert data == [
        {
            "days_all": [
                DatetimeModWeek(0, 0, 0),
                DatetimeModWeek(1, 0, 0),
                DatetimeModWeek(2, 0, 0),
                DatetimeModWeek(4, 0, 0),
            ]
        }
    ]
    assert rest == ""

    days_with_rollover_input = "Wed, Sat-Tue"
    (data, rest) = days(days_with_rollover_input)
    assert data == [
        {
            "days_all": [
                DatetimeModWeek(2, 0, 0),
                DatetimeModWeek(5, 0, 0),
                DatetimeModWeek(6, 0, 0),
                DatetimeModWeek(0, 0, 0),
                DatetimeModWeek(1, 0, 0)
            ]
        }
    ]
    assert rest == ""

    pass_with_tail_input = "Mon-Tue, Thu, Sat-Sun 9:00"
    (data, rest) = days(pass_with_tail_input)
    assert data == [
        {
            "days_all": [
                DatetimeModWeek(0, 0, 0),
                DatetimeModWeek(1, 0, 0),
                DatetimeModWeek(3, 0, 0),
                DatetimeModWeek(5, 0, 0),
                DatetimeModWeek(6, 0, 0),
            ]
        }
    ]
    assert rest == " 9:00"


def number(input):
    if result := n_or_more(
        numeral,
        n=1
    )(input):
        (data, rest) = result
        number_found = 0

        for (index, item) in enumerate(list(reversed(data))):
            number_found += int(item["numeral"])*10**(index)

        return (
            [
                {
                    "number_found": number_found
                }
            ],
            rest
        )
    else:
        return None


def test_number():
    fail_inputs = [
        "",
        "aa"
    ]
    for fail_input in fail_inputs:
        assert number(fail_input) is None

    pass_single_input = "5"
    (data, rest) = number(pass_single_input)
    assert data == [
        {
            "number_found": 5
        }
    ]
    assert rest == ""

    pass_with_tail_input = "6a"
    (data, rest) = number(pass_with_tail_input)
    assert data == [
        {
            "number_found": 6
        }
    ]
    assert rest == "a"

    pass_double_input = "56"
    (data, rest) = number(pass_double_input)
    assert data == [
        {
            "number_found": 56
        }
    ]
    assert rest == ""

    pass_triple_input = "567"
    (data, rest) = number(pass_triple_input)
    assert data == [
        {
            "number_found": 567
        }
    ]
    assert rest == ""


def number_in_range(input, n, m):
    if result := number(input):
        (data, rest) = result
        number_found = data[0]["number_found"]

        if number_found < n or number_found >= m:
            return None

        else:
            return (
                [
                    {
                        "number_found": number_found
                    }
                ],
                rest
            )
    else:
        return None


def test_number_in_range():
    n = 5
    m = 12
    
    # Tests that should fail
    fail_inputs = [
        "a",
        n - 1,
        m
    ]
    for fail_input in fail_inputs:
        assert number_in_range(str(fail_input), n, m) is None

    # Tests that should succeed
    pass_without_tail_inputs = [
        n,
        10,
        m -1
    ]

    for pass_input in pass_without_tail_inputs:
        (data, rest) = number_in_range(str(pass_input), n, m)
        assert data == [
            {
                "number_found": pass_input
            }
        ]
        assert rest == ""

    pass_with_tail_input = "7c"
    (data, rest) = number_in_range(pass_with_tail_input, n, m)
    assert data == [
        {
            "number_found": 7
        }
    ]
    assert rest == "c"


def string(search_string):
    def string_lambda(input):
        parsers = [char(c) for c in search_string]

        if result := sequence(parsers)(input):
            (_, rest) = result
            return (
                [
                    {
                        "string": search_string
                    }
                ],
                rest
            )
    return string_lambda


def test_string():
    search_string = "abcd"

    fail_inputs = [
        "",
        "qwerty"
    ]
    
    for fail_input in fail_inputs:
        assert string(search_string)(fail_input) is None

    pass_without_tail_input = "abcd"
    (data, rest) = string(search_string)(pass_without_tail_input)
    assert data == [
        {
            "string": search_string
        }
    ]
    assert rest == ""
    
    pass_with_tail_input = "abcde"
    (data, rest) = string(search_string)(pass_with_tail_input)
    assert data == [
        {
            "string": search_string
        }
    ]
    assert rest == "e"


def hour(input):
    if result := number_in_range(
        input,
        1,
        13
    ):
        (data, rest) = result

        # Change "number_found" to "hour"
        data[0]["hour"] = data[0].pop("number_found")
        return (data, rest)
    else:
        return None


def test_hour():
    fail_inputs = [
        "",
        "16"
    ]
    for fail_input in fail_inputs:
        assert hour(fail_input) is None

    for tail in ["", "tail"]:
        for hour_input in range(1, 12+1):
            (data, rest) = hour(str(hour_input) + tail)
            assert data == [
                {
                    "hour": hour_input
                }
            ]
            assert rest == tail


def minute(input):
    if result := number_in_range(
        input,
        0,
        60
    ):
        (data, rest) = result

        # Change "number_found" to "minute"
        data[0]["minute"] = data[0].pop("number_found")
        return (data, rest)
    else:
        return None


def test_minute():
    fail_inputs = [
        "",
        "75"
    ]

    for fail_input in fail_inputs:
        assert minute(fail_input) is None

    
    for tail in ["", "tail"]:
        for min_input in range(0, 59+1):
            (data, rest) = minute(str(min_input) + tail)
            assert data == [
                {
                    "minute": min_input
                }
            ]
            assert rest == tail


def time(input):
    if result := sequence([
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
    ])(input):
        (data, rest) = result
        is_pm = data.pop()["string"] == "pm"

        if "minute" in data[-1]:
            found_minute = data.pop()["minute"]
        else:
            found_minute = 0

        found_hour = data.pop()["hour"]

        if found_hour == 12:
            # PM spans [12, 1, ... 10, 11].
            # Make PM actually span [1...12]
            is_pm = not is_pm

        if is_pm:
            found_hour = (found_hour + 12) % 24
            # Convert to 24 hour clock with range [0, 23]

        found_time = DatetimeModWeek(0, found_hour, found_minute)

        return (
            [
                {
                    "time": found_time
                }
            ],
            rest
        )
    else:
        return None


def test_time():
    # Tests that should fail
    fail_inputs = [
        "",
        "abcde",
        "12cde",
        "12:45 cde"
    ]

    for fail_input in fail_inputs:
        assert time(fail_input) is None

    # Tests that should pass
    single_digit_input = "1:02 am"
    (data, rest) = time(single_digit_input)
    assert data == [
        {
            "time": DatetimeModWeek(0, 1, 2)
        }
    ]
    assert rest == ""

    single_digit_with_tail_input = "3:05 am banana"
    (data, rest) = time(single_digit_with_tail_input)
    assert data == [
        {
            "time": DatetimeModWeek(0, 3, 5)
        }
    ]
    assert rest == " banana"

    double_digit_input = "10:56 am"
    (data, rest) = time(double_digit_input)
    assert data == [
        {
            "time": DatetimeModWeek(0, 10, 56)
        }
    ]
    assert rest == ""

    pm_input = "6:24 pm"
    (data, rest) = time(pm_input)
    assert data == [
        {
            "time": DatetimeModWeek(0, 18, 24)
        }
    ]
    assert rest == ""

    noon_pm_input = "12:56 pm"
    (data, rest) = time(noon_pm_input)
    assert data == [
        {
            "time": DatetimeModWeek(0, 12, 56)
        }
    ]
    assert rest == ""

    midnight_am_input = "12:43 am"
    (data, rest) = time(midnight_am_input)
    assert data == [
        {
            "time": DatetimeModWeek(0, 0, 43)
        }
    ]
    assert rest == ""

    no_minute_input = "9 am"
    (data, rest) = time(no_minute_input)
    assert data == [
        {
            "time": DatetimeModWeek(0, 9, 0)
        }
    ]
    assert rest == ""


def time_range(input):
    if result := sequence([
        time,
        string(" - "),
        time
    ])(input):
        (data, rest) = result

        close_time = data.pop()["time"]
        data.pop()  # Throw away " - "
        open_time = data.pop()["time"]

        return (
            [
                {
                    "open_time": open_time,
                    "close_time": close_time
                }
            ],
            rest
        )
    else:
        return None


def test_time_range():
    # Tests that should fail
    fail_inputs = [
        "", # Empty string
        "asdf",  # No valid input
        "9:45 am",  # Only one time
        "9:45 am - ",  # Only one time with separator
    ]

    for input in fail_inputs:
        assert time_range(input) is None

    # Tests that should pass
    pass_without_tail_input = "9:45 am - 10:15 pm"
    (data, rest) = time_range(pass_without_tail_input)
    assert data == [
        {
            "open_time": DatetimeModWeek(0, 9, 45),
            "close_time": DatetimeModWeek(0, 22, 15)
        }
    ]
    assert rest == ""

    pass_with_tail_input = "4:15 pm - 2:38 am Monday"
    (data, rest) = time_range(pass_with_tail_input)
    assert data == [
        {
            "open_time": DatetimeModWeek(0, 16, 15),
            "close_time": DatetimeModWeek(0, 2, 38)
        }
    ]
    assert rest == " Monday"


def datetime(input):
    if result := sequence([
        days,
        char(" "),
        time_range
    ])(input):
        (data, rest) = result

        times_found = data.pop()
        days_all_found = data.pop()["days_all"]

        hours = []

        if times_found["close_time"] < times_found["open_time"]:
            day_rollover = DatetimeModWeek(1, 0, 0)
        else:
            day_rollover = DatetimeModWeek(0, 0, 0)

        for day_found in days_all_found:
            hours.append({
                "open_datetime": day_found + times_found["open_time"],
                "close_datetime": day_found + day_rollover + times_found["close_time"],
            })

        return (hours, rest)
    else:
        return None


def test_datetime():
    # Tests that should fail
    fail_inputs = [
        "",  # Empty string
        "asdf",  # No valid input
        "Mon, Wed-Fri ",  # Just days
        "Tue-Thu, Sat 9:45 am",  # Missing end time
    ]

    for fail_input in fail_inputs:
        assert datetime(fail_input) is None

    # Tests that should pass
    single_day_input = "Mon 9:45 am - 6 pm"
    (data, rest) = datetime(single_day_input)
    assert data == [
        {
            "open_datetime": DatetimeModWeek(0, 9, 45),
            "close_datetime": DatetimeModWeek(0, 18, 0)
        }
    ]
    assert rest == ""

    multiple_day_input = "Mon-Wed, Fri 10:15 am - 5 pm"
    (data, rest) = datetime(multiple_day_input)
    assert data == [
        {
            "open_datetime": DatetimeModWeek(0, 10, 15),
            "close_datetime": DatetimeModWeek(0, 17, 0)
        },
        {
            "open_datetime": DatetimeModWeek(1, 10, 15),
            "close_datetime": DatetimeModWeek(1, 17, 0)
        },
        {
            "open_datetime": DatetimeModWeek(2, 10, 15),
            "close_datetime": DatetimeModWeek(2, 17, 0)
        },
        {
            "open_datetime": DatetimeModWeek(4, 10, 15),
            "close_datetime": DatetimeModWeek(4, 17, 0)
        }
    ]
    assert rest == ""

    day_overflow_input = "Mon 1 pm - 2:30 am"
    (data, rest) = datetime(day_overflow_input)
    assert data == [
        {
            "open_datetime": DatetimeModWeek(0, 13, 0),
            "close_datetime": DatetimeModWeek(1, 2, 30)
        }
    ]
    assert rest == ""

    week_overflow_input = "Sun 11 am - 4:15 am"
    (data, rest) = datetime(week_overflow_input)
    assert data == [
        {
            "open_datetime": DatetimeModWeek(6, 11, 0),
            "close_datetime": DatetimeModWeek(0, 4, 15)
        }
    ]
    assert rest == ""


def parse_restaurant_hours(input):
    if result := sequence([
        datetime,
        n_or_more(
            sequence([
                string("  / "),
                datetime
            ]),
            n=0
        )
    ])(input):
        (data, rest) = result

        restaurant_hours_datetimes = []
        for item in data:
            if "string" in item:
                continue

            restaurant_hours_datetimes.append(item)

        return (restaurant_hours_datetimes, rest)
    else:
        return None


def test_parse_restaurant_hours():
    # Tests that should fail
    fail_inputs = [
        "",  # Empty string
        "asdf",  # No valid input
        "Mon, Wed-Fri",  # Just days
        "Tue-Thu, Sat 9:45 am",  # Missing end time
    ]

    for fail_input in fail_inputs:
        assert parse_restaurant_hours(fail_input) is None

    # Tests that should pass
    single_datetime_input = "Mon 9 am - 4 pm"
    (data, rest) = parse_restaurant_hours(single_datetime_input)
    assert data == [
        {
            "open_datetime": DatetimeModWeek(0, 9, 0),
            "close_datetime": DatetimeModWeek(0, 16, 0)
        }
    ]
    assert rest == ""

    datetime_with_tail_input = "Tue-Thu 8 am - 9 pm Banana"
    (data, rest) = parse_restaurant_hours(datetime_with_tail_input)
    assert data == [
        {
            "open_datetime": DatetimeModWeek(1, 8, 0),
            "close_datetime": DatetimeModWeek(1, 21, 0)
        },
        {
            "open_datetime": DatetimeModWeek(2, 8, 0),
            "close_datetime": DatetimeModWeek(2, 21, 0)
        },
        {
            "open_datetime": DatetimeModWeek(3, 8, 0),
            "close_datetime": DatetimeModWeek(3, 21, 0)
        }
    ]
    assert rest == " Banana"

    multiple_datetimes_input = "Mon-Wed, Fri 8:00 am - 4:30 pm  / Sat 10 am - 2:30 pm"
    (data, rest) = parse_restaurant_hours(multiple_datetimes_input)
    assert data == [
        {
            "open_datetime": DatetimeModWeek(0, 8, 0),
            "close_datetime": DatetimeModWeek(0, 16, 30)
        },
        {
            "open_datetime": DatetimeModWeek(1, 8, 0),
            "close_datetime": DatetimeModWeek(1, 16, 30)
        },
        {
            "open_datetime": DatetimeModWeek(2, 8, 0),
            "close_datetime": DatetimeModWeek(2, 16, 30)
        },
        {
            "open_datetime": DatetimeModWeek(4, 8, 0),
            "close_datetime": DatetimeModWeek(4, 16, 30)
        },
        {
            "open_datetime": DatetimeModWeek(5, 10, 0),
            "close_datetime": DatetimeModWeek(5, 14, 30)
        },
    ]
    assert rest == ""


# ==== Tests ====
# Primitive parsers
test_char()
test_numeral()
test_weekday()

# Combinators
test_sequence()
test_either()
test_n_or_more()

# Combined parsers
test_day_range()
test_days()
test_number()
test_number_in_range()
test_string()
test_hour()
test_minute()
test_time()
test_time_range()
test_datetime()
test_parse_restaurant_hours()
