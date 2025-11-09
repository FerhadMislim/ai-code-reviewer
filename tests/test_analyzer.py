"""
Tests for code complexity analyzer
"""

import unittest
from src.analyzer import ComplexityAnalyzer


class TestComplexityAnalyzer(unittest.TestCase):
    """Test complexity analysis functionality"""
    
    def test_python_basic_metrics(self):
        """Test basic Python metrics"""
        code = """
def function1():
    pass

def function2():
    return True

class MyClass:
    pass
"""
        metrics = ComplexityAnalyzer.analyze(code, 'python')
        
        self.assertGreater(metrics['total_lines'], 0)
        self.assertEqual(metrics['functions'], 2)
        self.assertEqual(metrics['classes'], 1)
    
    def test_javascript_metrics(self):
        """Test JavaScript metrics"""
        code = """
function test() {
    return true;
}

const arrow = () => {};

class MyClass {}
"""
        metrics = ComplexityAnalyzer.analyze(code, 'javascript')
        
        self.assertEqual(metrics['functions'], 1)
        self.assertEqual(metrics['arrow_functions'], 1)
        self.assertEqual(metrics['classes'], 1)
    
    def test_empty_code(self):
        """Test with empty code"""
        code = ""
        metrics = ComplexityAnalyzer.analyze(code, 'python')
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_lines', metrics)
    
    def test_comment_counting(self):
        """Test comment line counting"""
        code = """
# This is a comment
def test():
    # Another comment
    pass
"""
        metrics = ComplexityAnalyzer.analyze(code, 'python')
        
        self.assertEqual(metrics['comment_lines'], 2)
    
    def test_java_metrics(self):
        """Test Java metrics"""
        code = """
public class Test {
    public void method1() {}
    private int method2() { return 0; }
}

interface MyInterface {}
"""
        metrics = ComplexityAnalyzer.analyze(code, 'java')
        
        self.assertEqual(metrics['methods'], 2)
        self.assertEqual(metrics['interfaces'], 1)


if __name__ == '__main__':
    unittest.main()