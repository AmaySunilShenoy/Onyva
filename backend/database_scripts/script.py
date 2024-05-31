
import json

file_path = 'arrets-lignes.json'

# metro lines
metro_lines_list = ['1', '2', '3', '3bis', '4', '5', '6', '7', '7bis', '8', '9', '10', '11', '12', '13', '14']

try:
    # Open the JSON file
    with open(file_path, 'r') as file:
        # Load the JSON data
        data = json.load(file)

        # Filter the data to include only the specified metro lines
        metro_lines = [item['stop_name'] for item in data if item['route_long_name'] in metro_lines_list]

        # Print the filtered data
        print(metro_lines)
except Exception as e:
    print(f"Failed to read the file with json: {e}")


