"""
Smart Code Reviewer using GitHub Models
Professional code review tool with CLI, PR automation, and comprehensive analysis
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re


@dataclass
class ReviewResult:
    """Structure for code review results"""
    quality_score: int
    bugs: List[str]
    security_issues: List[str]
    improvements: List[str]
    best_practices: List[str]
    summary: str
    complexity_metrics: Dict[str, int]
    language: str
    file_path: str


class ComplexityAnalyzer:
    """Analyze code complexity metrics"""
    
    @staticmethod
    def analyze(code: str, language: str) -> Dict[str, int]:
        """Calculate basic complexity metrics"""
        lines = code.split('\n')
        
        metrics = {
            'total_lines': len(lines),
            'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            'comment_lines': len([l for l in lines if l.strip().startswith('#')]),
            'blank_lines': len([l for l in lines if not l.strip()]),
        }
        
        # Language-specific metrics
        if language == 'python':
            metrics['functions'] = len(re.findall(r'\bdef\s+\w+', code))
            metrics['classes'] = len(re.findall(r'\bclass\s+\w+', code))
            metrics['imports'] = len(re.findall(r'^\s*(?:import|from)\s+', code, re.MULTILINE))
        elif language in ['javascript', 'typescript']:
            metrics['functions'] = len(re.findall(r'\bfunction\s+\w+', code))
            metrics['arrow_functions'] = len(re.findall(r'=>', code))
            metrics['classes'] = len(re.findall(r'\bclass\s+\w+', code))
        elif language == 'java':
            metrics['methods'] = len(re.findall(r'(?:public|private|protected)\s+\w+\s+\w+\s*\(', code))
            metrics['classes'] = len(re.findall(r'\bclass\s+\w+', code))
        
        return metrics


class ConfigManager:
    """Manage configuration and API tokens"""
    
    CONFIG_FILE = '.code_reviewer_config'
    
    @staticmethod
    def load_config() -> Dict:
        """Load configuration from file"""
        config_path = Path(__file__).parent / ConfigManager.CONFIG_FILE
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def save_config(config: Dict):
        """Save configuration to file"""
        config_path = Path.home() / ConfigManager.CONFIG_FILE
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        os.chmod(config_path, 0o600)  # Secure the file
    
    @staticmethod
    def get_token() -> Optional[str]:
        """Get GitHub token from config or environment"""
        # Try environment variable first
        token = os.getenv('GITHUB_TOKEN')
        if token:
            return token
        
        # Try config file
        config = ConfigManager.load_config()
        return config.get('github_token')
    
    @staticmethod
    def set_token(token: str):
        """Save GitHub token to config"""
        config = ConfigManager.load_config()
        config['github_token'] = token
        ConfigManager.save_config(config)


class GitHubModelsCodeReviewer:
    """Code reviewer powered by GitHub Models API"""
    
    SUPPORTED_LANGUAGES = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.cs': 'csharp',
    }
    
    def __init__(self, github_token: str, model: str = "gpt-4o"):
        self.token = github_token
        self.model = model
        self.base_url = "https://models.inference.ai.azure.com/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
    
    def review_code(self, code: str, language: str, file_path: str = "") -> ReviewResult:
        """Review code and provide detailed feedback"""
        complexity = ComplexityAnalyzer.analyze(code, language)
        prompt = self._create_review_prompt(code, language, complexity)
        response = self._call_model(prompt)
        result = self._parse_review_response(response)
        
        result.complexity_metrics = complexity
        result.language = language
        result.file_path = file_path
        
        return result
    
    def review_file(self, file_path: Path) -> Optional[ReviewResult]:
        """Review a single file"""
        ext = file_path.suffix.lower()
        if ext not in self.SUPPORTED_LANGUAGES:
            print(f"⚠️  Skipping {file_path}: Unsupported file type")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            language = self.SUPPORTED_LANGUAGES[ext]
            return self.review_code(code, language, str(file_path))
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return None
    
    def review_directory(self, directory: Path, recursive: bool = True) -> List[ReviewResult]:
        """Review all supported files in a directory"""
        results = []
        pattern = '**/*' if recursive else '*'
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix in self.SUPPORTED_LANGUAGES:
                print(f"🔍 Reviewing {file_path}...")
                result = self.review_file(file_path)
                if result:
                    results.append(result)
        
        return results
    
    def _create_review_prompt(self, code: str, language: str, metrics: Dict) -> str:
        """Create a structured prompt for code review"""
        return f"""You are an expert code reviewer. Analyze the following {language} code and provide a comprehensive review.

CODE METRICS:
- Total Lines: {metrics.get('total_lines', 0)}
- Code Lines: {metrics.get('code_lines', 0)}
- Functions/Methods: {metrics.get('functions', 0) + metrics.get('methods', 0)}

CODE:
```{language}
{code}
```

Provide your review in the following JSON format:
{{
    "quality_score": <1-10>,
    "bugs": ["list of potential bugs with line references if possible"],
    "security_issues": ["list of security concerns"],
    "improvements": ["list of suggested improvements"],
    "best_practices": ["list of best practice violations"],
    "summary": "brief summary of the code quality"
}}

Be specific and actionable in your feedback."""
    
    def _call_model(self, prompt: str) -> str:
        """Call GitHub Models API"""
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert code reviewer with deep knowledge of software engineering best practices, security, and performance optimization across multiple programming languages."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": self.model,
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            raise Exception(f"API call failed: {str(e)}")
    
    def _parse_review_response(self, response: str) -> ReviewResult:
        """Parse the model's response into structured data"""
        try:
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
        except (json.JSONDecodeError, KeyError):
            return ReviewResult(
                quality_score=0,
                bugs=[],
                security_issues=[],
                improvements=[],
                best_practices=[],
                summary=f"Failed to parse review: {response[:200]}",
                complexity_metrics={},
                language='',
                file_path=''
            )


class ReportGenerator:
    """Generate review reports in various formats"""
    
    @staticmethod
    def generate_markdown(results: List[ReviewResult], output_file: str):
        """Generate a comprehensive Markdown report"""
        with open(output_file, 'w') as f:
            f.write("# Code Review Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Files Reviewed:** {len(results)}\n\n")
            
            # Summary statistics
            avg_score = sum(r.quality_score for r in results) / len(results) if results else 0
            total_bugs = sum(len(r.bugs) for r in results)
            total_security = sum(len(r.security_issues) for r in results)
            
            f.write("## Summary\n\n")
            f.write(f"- **Average Quality Score:** {avg_score:.1f}/10\n")
            f.write(f"- **Total Bugs Found:** {total_bugs}\n")
            f.write(f"- **Security Issues:** {total_security}\n\n")
            
            # Detailed reviews
            f.write("## Detailed Reviews\n\n")
            for result in results:
                f.write(f"### 📁 {result.file_path}\n\n")
                f.write(f"**Language:** {result.language.title()}  \n")
                f.write(f"**Quality Score:** {result.quality_score}/10\n\n")
                
                # Complexity metrics
                f.write("#### 📊 Complexity Metrics\n\n")
                for key, value in result.complexity_metrics.items():
                    f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")
                f.write("\n")
                
                f.write(f"#### 📝 Summary\n\n{result.summary}\n\n")
                
                if result.bugs:
                    f.write("#### 🐛 Potential Bugs\n\n")
                    for bug in result.bugs:
                        f.write(f"- {bug}\n")
                    f.write("\n")
                
                if result.security_issues:
                    f.write("#### 🔒 Security Issues\n\n")
                    for issue in result.security_issues:
                        f.write(f"- {issue}\n")
                    f.write("\n")
                
                if result.improvements:
                    f.write("#### 💡 Improvements\n\n")
                    for imp in result.improvements:
                        f.write(f"- {imp}\n")
                    f.write("\n")
                
                if result.best_practices:
                    f.write("#### 📚 Best Practices\n\n")
                    for bp in result.best_practices:
                        f.write(f"- {bp}\n")
                    f.write("\n")
                
                f.write("---\n\n")
        
        print(f"✅ Markdown report saved to: {output_file}")
    
    @staticmethod
    def generate_json(results: List[ReviewResult], output_file: str):
        """Generate a JSON report"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_files': len(results),
            'reviews': [asdict(r) for r in results]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ JSON report saved to: {output_file}")
    
    @staticmethod
    def print_console(result: ReviewResult):
        """Pretty print a single review to console"""
        print("\n" + "="*70)
        print(f"📁 FILE: {result.file_path}")
        print(f"🔤 LANGUAGE: {result.language.title()}")
        print(f"📊 QUALITY SCORE: {result.quality_score}/10")
        print("="*70)
        
        # Complexity metrics
        print("\n📈 COMPLEXITY METRICS:")
        for key, value in result.complexity_metrics.items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        print(f"\n📝 SUMMARY:\n{result.summary}\n")
        
        if result.bugs:
            print("🐛 POTENTIAL BUGS:")
            for i, bug in enumerate(result.bugs, 1):
                print(f"  {i}. {bug}")
            print()
        
        if result.security_issues:
            print("🔒 SECURITY ISSUES:")
            for i, issue in enumerate(result.security_issues, 1):
                print(f"  {i}. {issue}")
            print()
        
        if result.improvements:
            print("💡 IMPROVEMENTS:")
            for i, imp in enumerate(result.improvements, 1):
                print(f"  {i}. {imp}")
            print()
        
        if result.best_practices:
            print("📚 BEST PRACTICES:")
            for i, bp in enumerate(result.best_practices, 1):
                print(f"  {i}. {bp}")
            print()


class GitHubActionIntegration:
    """GitHub Action workflow generator"""
    
    @staticmethod
    def generate_workflow(output_file: str = ".github/workflows/code-review.yml"):
        """Generate a GitHub Action workflow file"""
        workflow = """name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install requests
      
      - name: Get changed files
        id: changed-files
        uses: tj-actions/changed-files@v39
        with:
          files: |
            **.py
            **.js
            **.ts
            **.java
            **.cpp
            **.go
      
      - name: Run AI Code Review
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_MODELS_TOKEN: ${{ secrets.GITHUB_MODELS_TOKEN }}
        run: |
          # Download the code reviewer script
          # Run review on changed files
          for file in ${{ steps.changed-files.outputs.all_changed_files }}; do
            python code_reviewer.py review "$file" --format markdown --output "review_$file.md"
          done
      
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const reviews = fs.readdirSync('.').filter(f => f.startsWith('review_'));
            let comment = '## 🤖 AI Code Review\\n\\n';
            
            for (const review of reviews) {
              comment += fs.readFileSync(review, 'utf8') + '\\n\\n';
            }
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
"""
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(workflow)
        
        print(f"✅ GitHub Action workflow created: {output_file}")
        print("📝 Don't forget to add GITHUB_MODELS_TOKEN to your repository secrets!")


def setup_cli():
    """Setup command-line interface"""
    parser = argparse.ArgumentParser(
        description='AI-Powered Code Reviewer using GitHub Models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Review a single file
  python code_reviewer.py review mycode.py
  
  # Review all files in a directory
  python code_reviewer.py review ./src --recursive
  
  # Generate markdown report
  python code_reviewer.py review ./src --format markdown --output report.md
  
  # Configure GitHub token
  python code_reviewer.py config --token YOUR_GITHUB_TOKEN
  
  # Generate GitHub Action workflow
  python code_reviewer.py generate-action
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Review command
    review_parser = subparsers.add_parser('review', help='Review code files')
    review_parser.add_argument('path', help='File or directory to review')
    review_parser.add_argument('--recursive', '-r', action='store_true', 
                              help='Review directory recursively')
    review_parser.add_argument('--format', '-f', choices=['console', 'markdown', 'json'],
                              default='console', help='Output format')
    review_parser.add_argument('--output', '-o', help='Output file for report')
    review_parser.add_argument('--model', '-m', default='gpt-4o',
                              help='Model to use (default: gpt-4o)')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure settings')
    config_parser.add_argument('--token', help='Set GitHub token')
    config_parser.add_argument('--show', action='store_true', help='Show current config')
    
    # Generate action command
    subparsers.add_parser('generate-action', help='Generate GitHub Action workflow')
    
    return parser


def main():
    """Main entry point"""
    parser = setup_cli()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle config command
    if args.command == 'config':
        if args.token:
            ConfigManager.set_token(args.token)
            print("✅ GitHub token saved successfully!")
            print(f"📁 Config file: {Path.home() / ConfigManager.CONFIG_FILE}")
        elif args.show:
            config = ConfigManager.load_config()
            token = config.get('github_token', 'Not set')
            if token != 'Not set':
                token = token[:10] + '...' + token[-4:]
            print(f"GitHub Token: {token}")
        else:
            print("Use --token to set or --show to display current config")
        return
    
    # Handle generate-action command
    if args.command == 'generate-action':
        GitHubActionIntegration.generate_workflow()
        return
    
    # Handle review command
    if args.command == 'review':
        token = ConfigManager.get_token()
        if not token:
            print("❌ GitHub token not found!")
            print("Set it using: python code_reviewer.py config --token YOUR_TOKEN")
            print("Or set GITHUB_TOKEN environment variable")
            return
        
        try:
            reviewer = GitHubModelsCodeReviewer(token, args.model)
            path = Path(args.path)
            
            # Review file or directory
            if path.is_file():
                result = reviewer.review_file(path)
                if result:
                    results = [result]
                else:
                    return
            elif path.is_dir():
                results = reviewer.review_directory(path, args.recursive)
            else:
                print(f"❌ Path not found: {path}")
                return
            
            if not results:
                print("⚠️  No files to review")
                return
            
            # Generate output
            if args.format == 'console':
                for result in results:
                    ReportGenerator.print_console(result)
            elif args.format == 'markdown':
                output = args.output or 'code_review_report.md'
                ReportGenerator.generate_markdown(results, output)
            elif args.format == 'json':
                output = args.output or 'code_review_report.json'
                ReportGenerator.generate_json(results, output)
            
            # Summary
            avg_score = sum(r.quality_score for r in results) / len(results)
            print(f"\n{'='*70}")
            print(f"✅ Reviewed {len(results)} file(s)")
            print(f"📊 Average Quality Score: {avg_score:.1f}/10")
            print(f"{'='*70}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return


if __name__ == "__main__":
    main()