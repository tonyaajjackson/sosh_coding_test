import calendar


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
        next = input
        stack = []
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

    for (index, item) in enumerate(result["stack"]):
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

    pass_double_input = "55a5"
    pass_double_result = number(pass_double_input)
    assert pass_double_result["success"] == True
    assert pass_double_result["rest"] == "a5"
    assert pass_double_result["stack"] == [
        {
            "number_found": 55
        }
    ]

    pass_triple_input = "555"
    pass_triple_result = number(pass_triple_input)
    assert pass_triple_result["success"] == True
    assert pass_triple_result["rest"] == ""
    assert pass_triple_result["stack"] == [
        {
            "number_found": 555
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
