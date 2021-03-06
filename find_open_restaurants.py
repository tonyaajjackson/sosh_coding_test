import csv
from datetime import datetime
from open_hours_parser import parse
from modular_datetime import DatetimeModWeek, datetime_in_range


def find_open_restaurants(csv_filename, search_datetime):
    with open(csv_filename, newline="") as f:
        entries = list(csv.reader(f))

    search_datetime_modular = DatetimeModWeek(
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
        result = parse(rest["hours_string"])

        assert result is not None
        (data, rest) = result
        assert rest == ""

        restaurants[i]["hours_datetimes"] = data

    open_restaurants = []
    
    for rest in restaurants:
        for hour_range in rest["hours_datetimes"]:
            if datetime_in_range(
                hour_range["open_datetime"],
                hour_range["close_datetime"],
                search_datetime_modular
            ):
                open_restaurants.append(rest["name"])
    
    return open_restaurants

def test_find_open_restaurants():
    csv_filename = "rest_hours.csv"
    search_datetime = datetime(2020, 11, 14, 13, 45)

    open_restaurants = find_open_restaurants(csv_filename, search_datetime)

    print(open_restaurants)

if __name__ == "__main__":
    test_find_open_restaurants()