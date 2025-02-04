import traceback
import sys
import os
import json
from .clipboard import copy_to_clipboard  # Import clipboard function

def is_user_defined_file(file_path):
    """Checks if a file is user-defined (not from site-packages)."""
    if not file_path:
        return False

    file_path = os.path.abspath(file_path)
    site_packages_path = os.path.join(sys.prefix, "Lib", "site-packages")

    return not file_path.startswith(site_packages_path)

def extract_stack_trace(exception):
    """Extracts the structured stack trace from an exception."""
    exc_type, exc_value, exc_traceback = type(exception), exception, exception.__traceback__
    extracted_tb = traceback.extract_tb(exc_traceback)

    stack_frames = []
    last_error_frame = None
    first_site_package_frame = None
    recursion_count = 0
    recursion_limit = 3

    for trace in extracted_tb:
        file_path, line_number, function_name, code_line = trace

        last_error_frame = {
            "file": file_path,
            "line": line_number,
            "function": function_name,
            "code": code_line.strip() if code_line else None
        }

        if exc_type.__name__ == "RecursionError":
            recursion_count += 1
            if recursion_count > recursion_limit:
                continue 
            
        if not first_site_package_frame and not is_user_defined_file(file_path):
            first_site_package_frame = last_error_frame
            continue

        if is_user_defined_file(file_path):
            stack_frames.append(last_error_frame)

    return {
        "error_point": last_error_frame,
        "first_site_package_error": first_site_package_frame,
        "filtered_trace": stack_frames,
        "exception": exc_type.__name__,
        "message": str(exc_value)
    }

def extract_and_copy(exception):
    """Extracts the stack trace and copies the JSON to clipboard."""
    error_data = extract_stack_trace(exception)
    json_output = json.dumps(error_data, indent=4)
    
    copy_to_clipboard(json_output)  # Copies to clipboard
    return json_output  # Also returns JSON for logging/debugging
