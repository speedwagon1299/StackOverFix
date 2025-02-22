import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from SolutionSearch.searcher import retrieve_hybrid_solutions

class TestHybridRetrieval(unittest.TestCase):
    def setUp(self):
        """Setup a sample error for testing retrieval."""
        self.sample_error = {
            "exception": "IndexError: list index out of range",
            "message": "list index out of range",
            "code_snippet": "arr = [1, 2, 3]\nprint(arr[5])",
            "description": "Attempting to access an index that does not exist."
        }

    def test_retrieve_hybrid_solutions(self):
        """Check if retrieval returns at least one result."""
        results = retrieve_hybrid_solutions(self.sample_error, k=3)
        self.assertGreater(len(results), 0, "No solutions retrieved.")

    def test_result_structure(self):
        """Ensure retrieved results contain necessary fields."""
        results = retrieve_hybrid_solutions(self.sample_error, k=1)
        self.assertIn("title", results[0])
        self.assertIn("body", results[0])
        self.assertIn("explicit_error_message", results[0])

if __name__ == "__main__":
    unittest.main()
