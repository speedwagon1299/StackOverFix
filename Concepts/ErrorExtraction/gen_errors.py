import json
import time
import sys
import os
import pyperclip

stackoverfix_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(stackoverfix_path)

import stackoverfix
from Concepts.ErrorExtraction.error_snippets import error_functions 

errors_file = "errors.json"

# Ensure errors.json exists
try:
    with open(errors_file, "r") as f:
        errors_list = json.load(f)
except FileNotFoundError:
    errors_list = []

# Function to trigger and capture errors
def capture_and_append_errors():
    for error_name, error_function in error_functions.items():
        try:
            error_function()  # Execute function to trigger an error
        except Exception as e:
            print(f"🚨 Triggered {error_name}")

            # Extract structured stack trace using stackoverfix
            stackoverfix.extract_and_copy(e)

            # Wait for clipboard update
            time.sleep(1)

            # Retrieve JSON from clipboard
            clipboard_content = pyperclip.paste()

            # Parse JSON
            try:
                error_data = json.loads(clipboard_content)
            except json.JSONDecodeError:
                print(f"⚠️ Failed to parse JSON for {error_name}.")
                continue

            # Append structured error
            error_entry = {
                "exception": error_data.get("exception", error_name),
                "message": error_data.get("message", str(e)),
                "stack_trace": error_data.get("filtered_trace", []),
                "description": f"Triggered {error_name} by executing {error_function.__name__}()"
            }

            errors_list.append(error_entry)
            print(f"✅ Captured {error_name}")

    # Save structured errors to JSON
    with open(errors_file, "w") as f:
        json.dump(errors_list, f, indent=4)

    print("📂 `errors.json` has been updated with real error stack traces.")

# Run error capture function
capture_and_append_errors()
