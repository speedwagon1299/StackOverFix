"""
Compare number of colliding values
"""

import json

with open("data/processed_questions_pytorch.json", "r", encoding="utf-8") as f1, open("data/processed_questions_python.json", "r", encoding="utf-8") as f2:
    list1 = json.load(f1)  # Assuming each file contains a list of dictionaries
    list2 = json.load(f2)

set1 = set(list1)
set2 = set(list2)

intersection = set1 & set2  
union = set1 | set2  

print(f"Intersection count: {len(intersection)}")
print(f"Union count: {len(union)}")

# Save results if needed
# with open("intersection.json", "w", encoding="utf-8") as f:
#     json.dump(list(intersection), f, indent=4)

# with open("union.json", "w", encoding="utf-8") as f:
#     json.dump(list(union), f, indent=4)