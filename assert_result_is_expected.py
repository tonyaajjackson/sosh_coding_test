def assert_result_is_expected(result, expected):
    for key1 in expected.keys():
        if type(expected[key1]) is dict:
            for key2 in expected[key1]:
                assert result[key1][key2] == expected[key1][key2], \
                    "result[" + str(key1) + "][" + str(key2) + "] is \"" \
                    + str(result[key1][key2]) + "\", while expected[" \
                    + str(key1) + "][" + str(key2) + "] is \"" + \
                    str(expected[key1][key2]) + "\""

        assert result[key1] == expected[key1], \
            "result[" + str(key1) + "] is \"" + str(result[key1]) + \
            "\", while expected[" + str(key1) + "] is \"" + str(expected[key1]) \
            + "\""


def test_assert_result_is_expected():
    # Failing tests
    try:
        assert_result_is_expected(
            {"val1": 1},
            {"val1": 2}
        )
    except AssertionError:
        pass

    try:
        assert_result_is_expected(
            {
                "val1": 1,
                "dict1": {
                    "dictval1": 1
                }
            },
            {
                "val1": 1,
                "dict1": {
                    "dictval1": 2
                }
            },
        )
    except AssertionError:
        pass


# Tests
test_assert_result_is_expected()
