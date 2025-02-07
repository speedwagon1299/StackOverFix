"""
To ensure no duplicates
"""

import json

with open("pytorch_errors_sample.json", "r", encoding="utf-8") as f:
    data = json.load(f) 

# Use a set to track seen (title, body) pairs
seen = set()
unique_data_list = []

for item in data:
    identifier = (item.get("title", ""), item.get("body", "")) 
    if identifier not in seen:
        seen.add(identifier)
        unique_data_list.append(item)  

with open("pytorch_errors.json", "w", encoding="utf-8") as f:
    json.dump(unique_data_list, f, indent=4)

print(f"Original size: {len(data)}, Unique size: {len(unique_data_list)}")
