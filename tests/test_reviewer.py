import unittest
from pathlib import Path

class TestBasic(unittest.TestCase):
    def test_imports(self):
        # Test that main module can be imported
        try:
            import code_reviewer
            self.assertTrue(True)
        except ImportError:
            self.fail("Could not import code_reviewer")

if __name__ == '__main__':
    unittest.main()
