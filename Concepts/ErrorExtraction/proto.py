import traceback
import sys
import os

def is_user_defined_file(file_path):
    """
    Checks if a file belongs to the user-defined project (not an external package).
    
    Args:
        file_path (str): The path of the file in the traceback.
    
    Returns:
        bool: True if user-defined, False if it belongs to a package.
    """
    if not file_path:
        return False

    # Normalize path for consistency
    file_path = os.path.abspath(file_path)

    # Identify site-packages directory correctly on Windows
    site_packages_path = os.path.join(sys.prefix, "Lib", "site-packages")
    
    return not file_path.startswith(site_packages_path)

def extract_custom_traceback(exc_type, exc_value, exc_traceback):
    """
    Extracts a structured traceback that:
      - Captures the last failure (error point).
      - Includes all user-defined function calls.
      - Records only the first site-package failure.
    
    Args:
        exc_type: Exception type
        exc_value: Exception message
        exc_traceback: Traceback object
    
    Returns:
        dict: A structured JSON-friendly representation of the traceback.
    """
    formatted_traceback = traceback.extract_tb(exc_traceback)
    stack_frames = []
    last_error_frame = None
    first_site_package_frame = None
    recursion_count = 0
    recursion_limit = 3

    for trace in formatted_traceback:
        file_path, line_number, function_name, code_line = trace

        # Capture the last error frame (point of failure)
        last_error_frame = {
            "file": file_path,
            "line": line_number,
            "function": function_name,
            "code": code_line.strip()
        }

        # If the error is due to recursion, limit recorded frames
        if exc_type.__name__ == "RecursionError":
            recursion_count += 1
            if recursion_count > recursion_limit:
                continue  # Skip additional recursive frames
        
        # Identify the first site-package failure
        if not first_site_package_frame and not is_user_defined_file(file_path):
            first_site_package_frame = {
                "file": file_path,
                "line": line_number,
                "function": function_name,
                "code": code_line.strip()
            }
            continue  # Store first site-package frame but don't add to user trace

        # Only include user-defined files
        if is_user_defined_file(file_path):
            stack_frames.append({
                "file": file_path,
                "line": line_number,
                "function": function_name,
                "code": code_line.strip()
            })

    # Construct the final structured error report
    structured_traceback = {
        "error_point": last_error_frame,  # Highlight the exact error line
        "filtered_trace": stack_frames,  # Only user-defined function calls
        "exception": exc_type.__name__,  # Keep the final exception
        "message": str(exc_value)  # Error message for user clarity
    }

    # If a site-package error was detected, include it
    if first_site_package_frame:
        structured_traceback["first_site_package_error"] = first_site_package_frame

    return structured_traceback
