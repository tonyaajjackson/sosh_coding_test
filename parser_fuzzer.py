from string import printable
import random
from open_hours_parser import parse_restaurant_hours

rounds = int(1e5)
string_length = int(1e3)

for n in range(rounds):
    print("{:2.0f}".format(n/rounds*100) + "% Complete")
    parse_restaurant_hours(
        [random.choice(printable) for c in range(string_length)]
    )

print("No errors encountered")