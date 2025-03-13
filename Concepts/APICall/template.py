from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()

sys_instruct = """
                You will be given a stack trace of an error in python associated with a library. You have to
                generate an upto 8 word phrase without need for punctuation and semantics
                which will be useful when performing a similarity search in FAISS vector store
                embedded in microsoft/graphcodebert-base.
            """

"""
You will be given a stack trace of an error and its associated code snippet in python. If the error is simple and solvable by your current knowledge without documentation, return "DocRequired" with False and the other paramaters with NULL. Else, you have to name the required library's documentation as an enum in "Library" and generate an upto 8 word phrase without need for punctuation and semantics which will be useful when performing a similarity search in FAISS vector store embedded in microsoft/graphcodebert-base in the parameter "SearchPhrase".
"""

user_prompt = """
                {
                    "user_prompt": "Fix the recursion error here",
                    "code_snippet": "def test_stack_overflow_error():\n    try:\n        recursive_function()\n    except RecursionError as e:\n        error_details = extract_stack_trace(e)",
                    "stack_trace": {
                        "exception": "RecursionError",
                        "message": "maximum recursion depth exceeded",
                        "error_point": {
                            "file": "C:\\Users\\sriha\\OneDrive\\Desktop\\Projects\\RAG\\StackOverFix\\tests\\test_extractor.py",
                            "line": 19,
                            "function": "recursive_function",
                            "code": "return recursive_function()  # Stack Overflow Error"
                        },
                        "filtered_trace": [
                            {
                                "file": "C:\\Users\\sriha\\OneDrive\\Desktop\\Projects\\RAG\\StackOverFix\\tests\\test_extractor.py",
                                "line": 23,
                                "function": "test_stack_overflow_error",
                                "code": "recursive_function()"
                            },
                            {
                                "file": "C:\\Users\\sriha\\OneDrive\\Desktop\\Projects\\RAG\\StackOverFix\\tests\\test_extractor.py",
                                "line": 19,
                                "function": "recursive_function",
                                "code": "return recursive_function()  # Stack Overflow Error"
                            }
                        ]
                    }
                }
            """
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content_stream(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction=sys_instruct),
    contents=[user_prompt]
)

for chunk in response:
    print(chunk.text, end="")