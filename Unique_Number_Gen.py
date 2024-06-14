import random

def generate_unique_number():
  """Generates a unique number.

  Returns:
    A unique number.
  """

  number = random.randint(1, 1000)
  while number in used_numbers:
    number = random.randint(1, 1000)
  used_numbers.add(number)
  return number

# Example usage:

used_numbers = set()
unique_number = generate_unique_number()
print(unique_number)

'''
import json

import pandas as pd

import json
from datetime import datetime
# Read the JSON file
 with open("D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\DailyPositions\\30_04_2024.json", "r") as f:
    json_data = json.load(f)

# Replace newlines and spaces
json_data = json_data.replace("\n", "").replace(" ", "")

# Write the JSON file back
with open("D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\DailyPositions\\30_04_2024.json", "w") as f:
    json.dump(json_data, f)
# Create a JSON object
json_object = {
    "name": "John Doe",
    "age": 30,
    "occupation": "Software Engineer",
    "address": {
        "street": "123 Main Street",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94105"
    }
}

with open("D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\DailyPositions\\30_04_2024.json", "r") as in_file:
    struct = json.load(in_file)

# struct is a dictionary, modify it in place
struct[0]['Ltp'] = 656565
target_norenordno = "24043000702545" # Replace with the actual value

        # Find the record with the specified 'norenordno'
for item in struct:
    if item.get("OrderId", {}) == target_norenordno:
        # Update the 'FinalPrice' field to zero
        item[f'Ltp'] = 56666666666 

with open("D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\DailyPositions\\30_04_2024.json", "w") as out_file:
    json.dump(struct, out_file)
def update_json_file(self,id_value,update_field,update_value):
    import json

    # Read the JSON data from your file (replace 'your_file.json' with the actual file path)
    with open(self.file_name, 'r') as json_file:
        data = json.load(json_file)

    # Specify the unique 'norenordno' value for the record you want to update
    target_norenordno = id_value  # Replace with the actual value

    # Find the record with the specified 'norenordno'
    for item in data:
        if item.get('OrderId', {}) == target_norenordno:
            # Update the 'FinalPrice' field to zero
            if isinstance(item[f'{update_field}'], datetime.datetime):
                update_value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                item[f'{update_field}'] = update_value
            break  # Stop searching once the record is found

    # Write the modified data back to the file
    with open(self.file_name, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Updated 'FinalPrice' field for record with norenordno '{target_norenordno}' to zero.")

update_json_file("FinalTradedDate",datetime.datetime.now().strptime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f'))'''