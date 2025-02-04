import stackoverfix

try:
    buggy_code = 1 / 0  # Causes ZeroDivisionError
except Exception as e:
    stackoverfix.extract_and_copy(e)
    print("Error copied to clipboard! Paste it into the debugging website.")
