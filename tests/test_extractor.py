import pytest
import json
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from stackoverfix.extractor import extract_stack_trace

def test_basic_runtime_error():
    try:
        1 / 0  # ZeroDivisionError
    except Exception as e:
        error_details = extract_stack_trace(e)
        print("Basic Runtime Error Test:\n", json.dumps(error_details, indent=4))
        assert error_details["exception"] == "ZeroDivisionError"
        assert len(error_details["filtered_trace"]) == 1 

def recursive_function():
    return recursive_function()  # Stack Overflow Error

def test_stack_overflow_error():
    try:
        recursive_function()
    except RecursionError as e:
        error_details = extract_stack_trace(e)
        print("Stack Overflow Error Test:\n", json.dumps(error_details, indent=4))
        assert error_details["exception"] == "RecursionError"
        assert len(error_details["filtered_trace"]) == 3  

def test_incorrect_pandas_command():
    try:
        df = pd.DataFrame({"col1": [1, 2, 3]})
        df["col2"]  # KeyError
    except Exception as e:
        error_details = extract_stack_trace(e)
        print("Incorrect Pandas Command Test:\n", json.dumps(error_details, indent=4))
        assert error_details["exception"] == "KeyError"
        assert len(error_details["filtered_trace"]) == 1

def function_with_error():
    pd.read_csv("non_existent_file.csv")  # Raises FileNotFoundError

def user_function():
    function_with_error()  # Calls another function having an error from a package

def test_user_defined_function_with_package_error():
    try:
        user_function()
    except Exception as e:
        error_details = extract_stack_trace(e)
        print("User Defined Function Calling Package Error Test:\n", json.dumps(error_details, indent=4))
        assert error_details["exception"] == "FileNotFoundError"
        assert len(error_details["filtered_trace"]) == 3
