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

user_prompt = """
                {
                    "error_point": {
                        "file": "C:\\Users\\sriha\\OneDrive\\Desktop\\Projects\\RAG\\StackOverFix\\tests\\test_extractor.py",
                        "line": 19,
                        "function": "recursive_function",
                        "code": "return recursive_function()  # Stack Overflow Error"
                    },
                    "first_site_package_error": null,
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
                        },
                        {
                            "file": "C:\\Users\\sriha\\OneDrive\\Desktop\\Projects\\RAG\\StackOverFix\\tests\\test_extractor.py",
                            "line": 19,
                            "function": "recursive_function",
                            "code": "return recursive_function()  # Stack Overflow Error"
                        }
                    ],
                    "exception": "RecursionError",
                    "message": "maximum recursion depth exceeded"
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