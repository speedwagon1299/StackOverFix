import pyperclip
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from stackoverfix.clipboard import copy_to_clipboard

def test_clipboard_copy():
    test_data = "Clipboard test"
    copy_to_clipboard(test_data)
    assert pyperclip.paste() == test_data  # Verify clipboard contains correct data
