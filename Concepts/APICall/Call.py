from dotenv import load_dotenv
import os
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash-lite"

# Step 1: First API Call (Preserve the Context)
def analyze_error():
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""{
                    \"user_prompt\": \"Fix the recursion error here\",
                    \"code_snippet\": \"def test_stack_overflow_error():\\n    try:\\n        recursive_function()\\n    except RecursionError as e:\\n        error_details = extract_stack_trace(e)\",
                    \"stack_trace\": {
                        \"exception\": \"RecursionError\",
                        \"message\": \"maximum recursion depth exceeded\",
                        \"error_point\": {
                            \"file\": \"C:\\\\Users\\\\sriha\\\\OneDrive\\\\Desktop\\\\Projects\\\\RAG\\\\StackOverFix\\\\tests\\\\test_extractor.py\",
                            \"line\": 19,
                            \"function\": \"recursive_function\",
                            \"code\": \"return recursive_function()  # Stack Overflow Error\"
                        },
                        \"filtered_trace\": [
                            {
                                \"file\": \"C:\\\\Users\\\\sriha\\\\OneDrive\\\\Desktop\\\\Projects\\\\RAG\\\\StackOverFix\\\\tests\\\\test_extractor.py\",
                                \"line\": 23,
                                \"function\": \"test_stack_overflow_error\",
                                \"code\": \"recursive_function()\"
                            },
                            {
                                \"file\": \"C:\\\\Users\\\\sriha\\\\OneDrive\\\\Desktop\\\\Projects\\\\RAG\\\\StackOverFix\\\\tests\\\\test_extractor.py\",
                                \"line\": 19,
                                \"function\": \"recursive_function\",
                                \"code\": \"return recursive_function()  # Stack Overflow Error\"
                            }
                        ]
                    }
                }"""),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type=genai.types.Type.OBJECT,
            required=["DocReq"],
            properties={
                "DocReq": genai.types.Schema(type=genai.types.Type.BOOLEAN),
                "SearchPhrase": genai.types.Schema(type=genai.types.Type.STRING),
                "Library": genai.types.Schema(
                    type=genai.types.Type.STRING,
                    enum=["Numpy", "Pandas", "PyTorch", "Scikit-Learn", "TensorFlow Keras", "Python"],
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(
                text="""You will be given a stack trace of an error and its associated code snippet in Python.
                If the error is simple and solvable by your current knowledge without available documentation in enum,
                return \"DocRequired\" with False and the other parameters with NULL.
                Else, return the required library documentation as an enum in \"Library\"
                and generate a compact (≤8 words) phrase for FAISS-based similarity search in the parameter \"SearchPhrase\"."""
            ),
        ],
    )

    response = client.models.generate_content_stream(
        model=model, contents=contents, config=generate_content_config
    )

    response_text = ""
    for chunk in response:
        response_text += chunk.text
        print(chunk.text, end="")

    return response_text, contents  # Preserve content for next call


# Step 2: Second API Call (Reusing Context with New System Prompt)
def submit_documents( previous_contents, documents):
    # Append new documents without structured input
    previous_contents.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"Here are the required documents: {', '.join(documents)}")
            ],
        )
    )

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
        system_instruction=[
            types.Part.from_text(
                text="""You now have additional documents. Use them to refine your solution.
                You do not need to reprocess the stack trace—only update the previous response using the provided documents.
                Return the best fix or explanation based on the additional context."""
            ),
        ],
    )

    response = client.models.generate_content_stream(
        model=model, contents=previous_contents, config=generate_content_config
    )

    for chunk in response:
        print(chunk.text, end="")


if __name__ == "__main__":
    # First call (Analyze error)
    response_text, previous_contents = analyze_error()

    # Simulate Second API Call (Submit additional documents)
    submit_documents(previous_contents, ["debugging_guide.pdf", "library_docs.txt"])
