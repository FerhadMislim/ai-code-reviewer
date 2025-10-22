"""
Tests for the main reviewer functionality
"""

import unittest
from unittest.mock import Mock, patch
from src.reviewer import GitHubModelsCodeReviewer
from src.models import ReviewResult, ReviewConfig


class TestGitHubModelsCodeReviewer(unittest.TestCase):
    """Test the main reviewer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.token = "test_token"
        self.config = ReviewConfig(model="gpt-4o", temperature=0.3)
        self.reviewer = GitHubModelsCodeReviewer(self.token, self.config)
    
    def test_initialization(self):
        """Test reviewer initialization"""
        self.assertEqual(self.reviewer.token, self.token)
        self.assertEqual(self.reviewer.config.model, "gpt-4o")
        self.assertIsNotNone(self.reviewer.headers)
    
    def test_supported_languages(self):
        """Test supported language mappings"""
        self.assertIn('.py', self.reviewer.SUPPORTED_LANGUAGES)
        self.assertIn('.js', self.reviewer.SUPPORTED_LANGUAGES)
        self.assertEqual(self.reviewer.SUPPORTED_LANGUAGES['.py'], 'python')
        self.assertEqual(self.reviewer.SUPPORTED_LANGUAGES['.js'], 'javascript')
    
    def test_create_review_prompt(self):
        """Test prompt creation"""
        code = "def test(): pass"
        language = "python"
        metrics = {'total_lines': 1, 'code_lines': 1}
        
        prompt = self.reviewer._create_review_prompt(code, language, metrics)
        
        self.assertIn('python', prompt.lower())
        self.assertIn(code, prompt)
        self.assertIn('quality_score', prompt)
    
    @patch('src.reviewer.requests.post')
    def test_call_model_success(self, mock_post):
        """Test successful API call"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"quality_score": 8, "bugs": [], "security_issues": [], "improvements": [], "best_practices": [], "summary": "Good"}'
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = self.reviewer._call_model("test prompt")
        
        self.assertIsInstance(result, str)
        self.assertIn('quality_score', result)
    
    def test_parse_review_response(self):
        """Test response parsing"""
        response = '''```json
{
    "quality_score": 7,
    "bugs": ["Bug 1"],
    "security_issues": [],
    "improvements": ["Improvement 1"],
    "best_practices": [],
    "summary": "Code looks good"
}
```'''
        
        result = self.reviewer._parse_review_response(response)
        
        self.assertIsInstance(result, ReviewResult)
        self.assertEqual(result.quality_score, 7)
        self.assertEqual(len(result.bugs), 1)
        self.assertEqual(result.summary, "Code looks good")


if __name__ == '__main__':
    unittest.main()