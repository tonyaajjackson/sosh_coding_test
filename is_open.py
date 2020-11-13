import csv

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

parse_open_hours(restaurants[1]["hours_string"])
