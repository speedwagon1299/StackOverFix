"""
Ensure all unique values
"""

import json

with open("data/union.json", "r", encoding="utf-8") as f1, open("tensorflow_errors.json", "r", encoding="utf-8") as f2:
    list1 = json.load(f1)  
    list2 = json.load(f2)

set1 = { (item.get("title", ""), item.get("body", "")): item for item in list1 }
set2 = { (item.get("title", ""), item.get("body", "")): item for item in list2 }

intersection_keys = set(set1.keys()) & set(set2.keys())  
union_keys = set(set1.keys()) | set(set2.keys()) 

intersection = [set1[key] for key in intersection_keys]  
union = [set1.get(key, set2.get(key)) for key in union_keys] 

print(f"Intersection count: {len(intersection)}")
print(f"Union count: {len(union)}")

with open("intersection.json", "w", encoding="utf-8") as f:
    json.dump(intersection, f, indent=4)

with open("union.json", "w", encoding="utf-8") as f:
    json.dump(union, f, indent=4)