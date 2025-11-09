"""
Report generation in various formats
"""

import json
from datetime import datetime
from typing import List
from pathlib import Path

from .models import ReviewResult


class ReportGenerator:
    """Generate review reports in various formats"""
    
    @staticmethod
    def generate_markdown(results: List[ReviewResult], output_file: str):
        """Generate a comprehensive Markdown report"""
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("# 🤖 AI Code Review Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Files Reviewed:** {len(results)}\n\n")
            
            # Summary statistics
            if results:
                avg_score = sum(r.quality_score for r in results) / len(results)
                total_bugs = sum(len(r.bugs) for r in results)
                total_security = sum(len(r.security_issues) for r in results)
                total_improvements = sum(len(r.improvements) for r in results)
                
                f.write("## 📊 Summary\n\n")
                f.write(f"- **Average Quality Score:** {avg_score:.1f}/10\n")
                f.write(f"- **Total Bugs Found:** {total_bugs}\n")
                f.write(f"- **Security Issues:** {total_security}\n")
                f.write(f"- **Improvement Suggestions:** {total_improvements}\n\n")
                
                # Quality distribution
                high_quality = len([r for r in results if r.quality_score >= 8])
                medium_quality = len([r for r in results if 5 <= r.quality_score < 8])
                low_quality = len([r for r in results if r.quality_score < 5])
                
                f.write("### Quality Distribution\n\n")
                f.write(f"- 🟢 High Quality (8-10): {high_quality} files\n")
                f.write(f"- 🟡 Medium Quality (5-7): {medium_quality} files\n")
                f.write(f"- 🔴 Low Quality (1-4): {low_quality} files\n\n")
            
            # Detailed reviews
            f.write("## 📝 Detailed Reviews\n\n")
            
            for idx, result in enumerate(results, 1):
                f.write(f"### {idx}. 📁 {result.file_path}\n\n")
                
                # Score badge
                score_emoji = "🟢" if result.quality_score >= 8 else "🟡" if result.quality_score >= 5 else "🔴"
                f.write(f"{score_emoji} **Quality Score:** {result.quality_score}/10  \n")
                f.write(f"**Language:** {result.language.title()}  \n")
                f.write(f"**Issues Found:** {result.issue_count()}\n\n")
                
                # Complexity metrics
                f.write("#### 📊 Complexity Metrics\n\n")
                f.write("| Metric | Value |\n")
                f.write("|--------|-------|\n")
                for key, value in result.complexity_metrics.items():
                    metric_name = key.replace('_', ' ').title()
                    f.write(f"| {metric_name} | {value} |\n")
                f.write("\n")
                
                # Summary
                f.write(f"#### 📝 Summary\n\n{result.summary}\n\n")
                
                # Issues
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
                    f.write("#### 💡 Suggested Improvements\n\n")
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
            'summary': ReportGenerator._calculate_summary(results),
            'reviews': [r.to_dict() for r in results]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ JSON report saved to: {output_file}")
    
    @staticmethod
    def generate_html(results: List[ReviewResult], output_file: str):
        """Generate an HTML report"""
        html_content = ReportGenerator._create_html_report(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML report saved to: {output_file}")
    
    @staticmethod
    def print_console(result: ReviewResult):
        """Pretty print a single review to console"""
        print("\n" + "="*70)
        print(f"📁 FILE: {result.file_path}")
        print(f"🔤 LANGUAGE: {result.language.title()}")
        
        # Score with color
        score_emoji = "🟢" if result.quality_score >= 8 else "🟡" if result.quality_score >= 5 else "🔴"
        print(f"{score_emoji} QUALITY SCORE: {result.quality_score}/10")
        print("="*70)
        
        # Complexity metrics
        print("\n📈 COMPLEXITY METRICS:")
        for key, value in result.complexity_metrics.items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        print(f"\n📝 SUMMARY:\n{result.summary}\n")
        
        # Issues
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
    
    @staticmethod
    def print_summary(results: List[ReviewResult]):
        """Print summary statistics"""
        if not results:
            print("⚠️  No results to summarize")
            return
        
        print(f"\n{'='*70}")
        print("📊 REVIEW SUMMARY")
        print(f"{'='*70}")
        
        avg_score = sum(r.quality_score for r in results) / len(results)
        total_bugs = sum(len(r.bugs) for r in results)
        total_security = sum(len(r.security_issues) for r in results)
        
        print(f"\n✅ Files Reviewed: {len(results)}")
        print(f"📊 Average Quality Score: {avg_score:.1f}/10")
        print(f"🐛 Total Bugs Found: {total_bugs}")
        print(f"🔒 Security Issues: {total_security}")
        
        # Quality distribution
        high = len([r for r in results if r.quality_score >= 8])
        medium = len([r for r in results if 5 <= r.quality_score < 8])
        low = len([r for r in results if r.quality_score < 5])
        
        print(f"\n🟢 High Quality (8-10): {high} files")
        print(f"🟡 Medium Quality (5-7): {medium} files")
        print(f"🔴 Low Quality (1-4): {low} files")
        print(f"\n{'='*70}\n")
    
    @staticmethod
    def _calculate_summary(results: List[ReviewResult]) -> dict:
        """Calculate summary statistics"""
        if not results:
            return {}
        
        return {
            'average_score': sum(r.quality_score for r in results) / len(results),
            'total_bugs': sum(len(r.bugs) for r in results),
            'total_security_issues': sum(len(r.security_issues) for r in results),
            'total_improvements': sum(len(r.improvements) for r in results),
            'high_quality_files': len([r for r in results if r.quality_score >= 8]),
            'medium_quality_files': len([r for r in results if 5 <= r.quality_score < 8]),
            'low_quality_files': len([r for r in results if r.quality_score < 5]),
        }
    
    @staticmethod
    def _create_html_report(results: List[ReviewResult]) -> str:
        """Create HTML report content"""
        # Simplified HTML report
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Code Review Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .file {{ border: 1px solid #ddd; margin: 20px 0; padding: 15px; }}
        .score-high { color: green; font-weight: bold; }
        .score-medium { color: orange; font-weight: bold; }
        .score-low { color: red; font-weight: bold; }
        .metric { display: inline-block; margin: 5px 10px; }
        .issue { margin: 10px 0; padding: 10px; background: #f9f9f9; }
    </style>
</head>
<body>
    <h1>🤖 AI Code Review Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Files Reviewed: {len(results)}</p>
"""
        
        for result in results:
            score_class = 'score-high' if result.quality_score >= 8 else 'score-medium' if result.quality_score >= 5 else 'score-low'
            html += f"""
    <div class="file">
        <h2>📁 {result.file_path}</h2>
        <p class="{score_class}">Quality Score: {result.quality_score}/10</p>
        <h3>Summary</h3>
        <p>{result.summary}</p>
        {"<h3>🐛 Bugs</h3><ul>" + "".join(f"<li>{b}</li>" for b in result.bugs) + "</ul>" if result.bugs else ""}
        {"<h3>🔒 Security Issues</h3><ul>" + "".join(f"<li>{s}</li>" for s in result.security_issues) + "</ul>" if result.security_issues else ""}
    </div>
"""
        
        html += "</body></html>"
        return html