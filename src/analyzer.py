"""
Code complexity and metrics analysis
"""

import re
from typing import Dict


class ComplexityAnalyzer:
    
    @staticmethod
    def analyze(code: str, language: str) -> Dict[str, int]:
        """
        Calculate complexity metrics for given code
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            Dictionary of metrics
        """
        lines = code.split('\n')
        
        metrics = {
            'total_lines': len(lines),
            'code_lines': ComplexityAnalyzer._count_code_lines(lines, language),
            'comment_lines': ComplexityAnalyzer._count_comment_lines(lines, language),
            'blank_lines': len([l for l in lines if not l.strip()]),
        }
        
        # Language-specific metrics
        language_metrics = ComplexityAnalyzer._get_language_metrics(code, language)
        metrics.update(language_metrics)
        
        return metrics
    
    @staticmethod
    def _count_code_lines(lines: list, language: str) -> int:
        """Count lines containing actual code"""
        comment_prefixes = {
            'python': '#',
            'javascript': '//',
            'typescript': '//',
            'java': '//',
            'cpp': '//',
            'c': '//',
            'go': '//',
            'rust': '//',
            'php': '//',
            'swift': '//',
            'kotlin': '//',
            'csharp': '//',
            'ruby': '#',
        }
        
        prefix = comment_prefixes.get(language, '#')
        return len([l for l in lines if l.strip() and not l.strip().startswith(prefix)])
    
    @staticmethod
    def _count_comment_lines(lines: list, language: str) -> int:
        """Count comment lines"""
        comment_prefixes = {
            'python': '#',
            'javascript': '//',
            'typescript': '//',
            'java': '//',
            'cpp': '//',
            'c': '//',
            'go': '//',
            'rust': '//',
            'php': '//',
            'swift': '//',
            'kotlin': '//',
            'csharp': '//',
            'ruby': '#',
        }
        
        prefix = comment_prefixes.get(language, '#')
        return len([l for l in lines if l.strip().startswith(prefix)])
    
    @staticmethod
    def _get_language_metrics(code: str, language: str) -> Dict[str, int]:

        if language == 'python':
            return {
                'functions': len(re.findall(r'\bdef\s+\w+', code)),
                'classes': len(re.findall(r'\bclass\s+\w+', code)),
                'imports': len(re.findall(r'^\s*(?:import|from)\s+', code, re.MULTILINE)),
            }
        
        elif language in ['javascript', 'typescript']:
            return {
                'functions': len(re.findall(r'\bfunction\s+\w+', code)),
                'arrow_functions': len(re.findall(r'=>', code)),
                'classes': len(re.findall(r'\bclass\s+\w+', code)),
                'imports': len(re.findall(r'^\s*(?:import|export)\s+', code, re.MULTILINE)),
            }
        
        elif language == 'java':
            return {
                'methods': len(re.findall(r'(?:public|private|protected)\s+\w+\s+\w+\s*\(', code)),
                'classes': len(re.findall(r'\bclass\s+\w+', code)),
                'interfaces': len(re.findall(r'\binterface\s+\w+', code)),
            }
        
        elif language in ['cpp', 'c']:
            return {
                'functions': len(re.findall(r'\w+\s+\w+\s*\([^)]*\)\s*{', code)),
                'classes': len(re.findall(r'\bclass\s+\w+', code)),
                'structs': len(re.findall(r'\bstruct\s+\w+', code)),
            }
        
        elif language == 'go':
            return {
                'functions': len(re.findall(r'\bfunc\s+\w+', code)),
                'structs': len(re.findall(r'\btype\s+\w+\s+struct', code)),
                'interfaces': len(re.findall(r'\btype\s+\w+\s+interface', code)),
            }
        
        elif language == 'rust':
            return {
                'functions': len(re.findall(r'\bfn\s+\w+', code)),
                'structs': len(re.findall(r'\bstruct\s+\w+', code)),
                'traits': len(re.findall(r'\btrait\s+\w+', code)),
            }
        
        return {}
    
    @staticmethod
    def calculate_cyclomatic_complexity(code: str, language: str) -> int:
        """
        Estimate cyclomatic complexity (simplified version)
        Counts decision points in the code
        """
        decision_keywords = {
            'python': ['if', 'elif', 'for', 'while', 'except', 'and', 'or'],
            'javascript': ['if', 'else if', 'for', 'while', 'switch', 'case', '&&', '||'],
            'java': ['if', 'else if', 'for', 'while', 'switch', 'case', '&&', '||'],
        }
        
        keywords = decision_keywords.get(language, ['if', 'for', 'while'])
        complexity = 1  # Base complexity
        
        for keyword in keywords:
            complexity += len(re.findall(r'\b' + keyword + r'\b', code))
        
        return complexity