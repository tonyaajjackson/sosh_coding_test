import csv
from open_hours_parser import parse_restaurant_hours

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

for (i, rest) in enumerate(restaurants):
    result = parse_restaurant_hours(rest["hours_string"])

    assert result["success"] == True
    assert result["rest"] == ""

    restaurants[i]["hours_datetimes"] = result["stack"]