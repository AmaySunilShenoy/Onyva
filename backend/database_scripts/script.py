import json

file_path = 'arrets-lignes.json'

# Metro lines to filter
metro_lines_list = ['7']

try:
    # Open the JSON file
    with open(file_path, 'r') as file:
        # Load the JSON data
        data = json.load(file)

        # Filter and collect stop names with their coordinates
        stops = [
            {'stop_name': item['stop_name'], 'lat': item['stop_lat'], 'lng': item['stop_lon']}
            for item in data if item['route_long_name'] in metro_lines_list
        ]

        # Remove duplicates by using a dictionary with stop names as keys
        unique_stops = {stop['stop_name']: stop for stop in stops}.values()

        # Sort stops first by latitude and then by longitude
        sorted_stops = sorted(unique_stops, key=lambda x: (x['lat'], x['lng']))

        # Extract the stop names in the sorted order
        metro_lines_sorted = [stop['stop_name'] for stop in sorted_stops]

        # Print the sorted stop names
        print(metro_lines_sorted)
except Exception as e:
    print(f"Failed to read the file with json: {e}")
