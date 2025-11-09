"""
Data models and structures for code review
"""

from dataclasses import dataclass, asdict
from typing import Dict, List


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
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ReviewResult":
        return cls(
            quality_score=data.get('quality_score', 0),
            bugs=data.get('bugs', []),
            security_issues=data.get('security_issues', []),
            improvements=data.get('improvements', []),
            best_practices=data.get('best_practices', []),
            summary=data.get('summary', ''),
            complexity_metrics=data.get('complexity_metrics', {}),
            language=data.get('language', ''),
            file_path=data.get('file_path', '')
        )
    
    def has_issues(self) -> bool:
        """Check if there are any issues found"""
        return bool(self.bugs or self.security_issues or self.best_practices)
    
    def issue_count(self) -> int:
        """Get total number of issues"""
        return len(self.bugs) + len(self.security_issues) + len(self.best_practices)


@dataclass
class ReviewConfig:
    """Configuration for code review"""
    model: str = "gpt-4o"
    temperature: float = 0.3
    max_tokens: int = 2000
    timeout: int = 60
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)