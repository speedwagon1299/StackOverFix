import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from SolutionSearch.evidence_score import check_relevance_with_llm

class TestEvidenceScoring(unittest.TestCase):
    def setUp(self):
        """Setup a sample error and fake retrieved answers."""
        self.sample_error = {
            "exception": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
            "message": "Cannot add integer and string",
            "code_snippet": "x = 5 + 'hello'",
            "description": "Attempting to add an integer to a string."
        }

        self.sample_solutions = [
            {"title": "Fixing TypeError", "body": "You should convert the string to an integer."},
            {"title": "Debugging Tips", "body": "Ensure you are not mixing data types in calculations."}
        ]

    def test_evidence_scoring(self):
        """Check if the LLM correctly scores answers."""
        scores = check_relevance_with_llm(self.sample_error, self.sample_solutions)
        self.assertIsNotNone(scores, "No scores returned by LLM.")

if __name__ == "__main__":
    unittest.main()
