# sosh_coding_test

A Python-based attempt at solving [Sosh's take-home programming test](https://medium.com/@rodbegbie/find-open-restaurants-an-engineering-take-home-test-dissected-1ada20282ceb), begun with next to no knowledge of parsers.

## Notable Features
### Recursive-Descent Parser
Implements a recursive-descent parser to flexibly parse restaurant hours. Primitive parsers such as numerals, characters, and weekdays are combined with combinators to form complex parsers such as times and date ranges, eventually building up to the full restaurant hours parser.

### Modular Datetime
Implements a modular arithmetic datetime with a modulus of one week to elegantly handle hour ranges overflowing over into the next week, e.g. "Sun 11am - 2am"

With modular arithmetic, if a restaurant is open from `start` to `finish`, a given `time` is between `start` and `finish` if `(time - start) < (end - start)`, even if `start` and `finish` span the week overflow boundary. This removes the need for edge case testing around rollovers.

### Comes With Tests & Fuzzer
Each parser comes with tests expected to fail and tests expected to pass, including as many edge cases as I could discover. Tests automatically run on import and provide redundancy of expression of expected behaviour.

Also included is a parser fuzzer to flesh out unexpected edge cases by triggering failures in the tests.

## What I Might Do Differently Next Time
### Change from returning a list of dictionaries to just a list
Each parser returns a tuple the form (data, rest), where data is a list of dictionaries. This allows the returned data type to be identified by the key. For example, a possible data return for the day_range parser could be:
```
[
    {
        "days": [1, 2, 3, 4]
    }
]
```

In theory, having the data tagged this way makes it harder to incorrectly chain parsers together. For example, the days_all parser is expecting to find a "days" key in the returned dictionary and would fail if the returned dictionary contained only an "hours" key.

However, using a dictionary to tag data might be overkill as errors in chaining would happen during coding higher-level parsers and would be caught by the tests. It would be simpler to just return the data directly without a key to identify its type.

### Use a parser generator
After finishing this test, I discovered a wealth of parser generators where I could just pass a grammar definition into the parser generator, which would have simplified a lot of the parser code. If I were to write another parser I would try to build it atop a parser generator like [Lark](https://github.com/lark-parser/lark) or [PyParsing](https://github.com/pyparsing/pyparsing).