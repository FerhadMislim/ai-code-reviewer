"""
Main code review logic using GitHub Models API
"""

import json
import requests
from pathlib import Path
from typing import List, Optional

from .models import ReviewResult, ReviewConfig
from .analyzer import ComplexityAnalyzer


class GitHubModelsCodeReviewer:
    """Code reviewer powered by GitHub Models API"""
    
    SUPPORTED_LANGUAGES = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.cs': 'csharp',
        '.scala': 'scala',
        '.pl': 'perl',
    }
    
    API_BASE_URL = "https://models.inference.ai.azure.com/chat/completions"
    
    def __init__(self, github_token: str, config: ReviewConfig = None):
        """
        Initialize the code reviewer
        
        Args:
            github_token: GitHub Personal Access Token
            config: Review configuration
        """
        self.token = github_token
        self.config = config or ReviewConfig()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
    
    def review_code(self, code: str, language: str, file_path: str = "") -> ReviewResult:
        """
        Review code and provide detailed feedback
        
        Args:
            code: Source code to review
            language: Programming language
            file_path: Path to the file (optional)
            
        Returns:
            ReviewResult with comprehensive analysis
        """
        # Analyze complexity
        complexity = ComplexityAnalyzer.analyze(code, language)
        
        # Create review prompt
        prompt = self._create_review_prompt(code, language, complexity)
        
        # Call AI model
        response = self._call_model(prompt)
        
        # Parse response
        result = self._parse_review_response(response)
        
        # Add metadata
        result.complexity_metrics = complexity
        result.language = language
        result.file_path = file_path
        
        return result
    
    def review_file(self, file_path: Path) -> Optional[ReviewResult]:
        """
        Review a single file
        
        Args:
            file_path: Path to the file
            
        Returns:
            ReviewResult or None if file is unsupported
        """
        ext = file_path.suffix.lower()
        if ext not in self.SUPPORTED_LANGUAGES:
            print(f"⚠️  Skipping {file_path}: Unsupported file type")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            language = self.SUPPORTED_LANGUAGES[ext]
            return self.review_code(code, language, str(file_path))
        
        except UnicodeDecodeError:
            print(f"⚠️  Skipping {file_path}: Binary file or encoding issue")
            return None
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return None
    
    def review_directory(self, directory: Path, recursive: bool = True) -> List[ReviewResult]:
        """
        Review all supported files in a directory
        
        Args:
            directory: Directory path
            recursive: Whether to scan recursively
            
        Returns:
            List of ReviewResults
        """
        results = []
        pattern = '**/*' if recursive else '*'
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix in self.SUPPORTED_LANGUAGES:
                print(f"🔍 Reviewing {file_path}...")
                result = self.review_file(file_path)
                if result:
                    results.append(result)
        
        return results
    
    def _create_review_prompt(self, code: str, language: str, metrics: dict) -> str:
        """Create a structured prompt for code review"""
        return f"""You are an expert code reviewer specializing in {language}. Analyze the following code and provide a comprehensive review.

CODE METRICS:
- Total Lines: {metrics.get('total_lines', 0)}
- Code Lines: {metrics.get('code_lines', 0)}
- Comment Lines: {metrics.get('comment_lines', 0)}
- Functions/Methods: {metrics.get('functions', 0) + metrics.get('methods', 0)}
- Classes: {metrics.get('classes', 0)}

CODE:
```{language}
{code}
```

Provide your review in the following JSON format:
{{
    "quality_score": <1-10>,
    "bugs": ["list of potential bugs with specific line references"],
    "security_issues": ["list of security concerns"],
    "improvements": ["list of suggested improvements"],
    "best_practices": ["list of best practice violations"],
    "summary": "brief summary of the code quality and main concerns"
}}

Focus on:
1. Potential bugs and logical errors
2. Security vulnerabilities
3. Performance issues
4. Code maintainability
5. Best practices for {language}

Be specific, actionable, and reference line numbers when possible."""
    
    def _call_model(self, prompt: str) -> str:
        """Call GitHub Models API"""
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert code reviewer with deep knowledge of software engineering best practices, security, and performance optimization across multiple programming languages. Provide detailed, actionable feedback."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        try:
            response = requests.post(
                self.API_BASE_URL,
                headers=self.headers,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"API call failed: {str(e)}")
    
    def _parse_review_response(self, response: str) -> ReviewResult:
        """Parse the model's response into structured data"""
        try:
            # Extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response
            
            data = json.loads(json_str)
            
            return ReviewResult(
                quality_score=data.get('quality_score', 0),
                bugs=data.get('bugs', []),
                security_issues=data.get('security_issues', []),
                improvements=data.get('improvements', []),
                best_practices=data.get('best_practices', []),
                summary=data.get('summary', ''),
                complexity_metrics={},
                language='',
                file_path=''
            )
        
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback if parsing fails
            return ReviewResult(
                quality_score=0,
                bugs=[],
                security_issues=[],
                improvements=[],
                best_practices=[],
                summary=f"Failed to parse review. Raw response: {response[:200]}...",
                complexity_metrics={},
                language='',
                file_path=''
            )