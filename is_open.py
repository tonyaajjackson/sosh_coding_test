import csv
from datetime import datetime
from open_hours_parser import parse_restaurant_hours
from modular_datetime import ModularDatetime


def find_open_restaurants(csv_filename, search_datetime):
    with open(csv_filename, newline="") as f:
        entries = list(csv.reader(f))

    search_datetime_modular = ModularDatetime(
        search_datetime.weekday(),
        search_datetime.hour,
        search_datetime.minute
    )

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

    return []


csv_filename = "rest_hours.csv"
search_datetime = datetime(2020, 11, 14, 13, 45)

open_restaurants = find_open_restaurants(csv_filename, search_datetime)
