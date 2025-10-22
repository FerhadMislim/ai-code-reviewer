"""
Command-line interface for the code reviewer
"""

import argparse
import sys
from pathlib import Path

from .config import ConfigManager
from .reviewer import GitHubModelsCodeReviewer
from .reporter import ReportGenerator
from .github_action import GitHubActionIntegration
from .models import ReviewConfig


class CLI:
    """Command-line interface handler"""
    
    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """Create and configure argument parser"""
        parser = argparse.ArgumentParser(
            description='🤖 AI-Powered Code Reviewer using GitHub Models',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Review a single file
  code-reviewer review mycode.py
  
  # Review all files in a directory
  code-reviewer review ./src --recursive
  
  # Generate markdown report
  code-reviewer review ./src --format markdown --output report.md
  
  # Configure GitHub token
  code-reviewer config --token YOUR_GITHUB_TOKEN
  
  # Generate GitHub Action workflow
  code-reviewer generate-action
  
  # Install pre-commit hook
  code-reviewer install-hook
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Review command
        review_parser = subparsers.add_parser('review', help='Review code files')
        review_parser.add_argument('path', help='File or directory to review')
        review_parser.add_argument('--recursive', '-r', action='store_true',
                                  help='Review directory recursively')
        review_parser.add_argument('--format', '-f', 
                                  choices=['console', 'markdown', 'json', 'html'],
                                  default='console', help='Output format')
        review_parser.add_argument('--output', '-o', help='Output file for report')
        review_parser.add_argument('--model', '-m', default=None,
                                  help='Model to use (default: from config or gpt-4o)')
        review_parser.add_argument('--temperature', '-t', type=float, default=0.3,
                                  help='Model temperature (default: 0.3)')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Configure settings')
        config_parser.add_argument('--token', help='Set GitHub token')
        config_parser.add_argument('--model', help='Set default model')
        config_parser.add_argument('--show', action='store_true', help='Show current config')
        
        # Generate action command
        action_parser = subparsers.add_parser('generate-action', 
                                             help='Generate GitHub Action workflow')
        action_parser.add_argument('--output', '-o', 
                                  default='.github/workflows/code-review.yml',
                                  help='Output path for workflow file')
        
        # Install hook command
        subparsers.add_parser('install-hook', 
                            help='Install pre-commit hook for local reviews')
        
        # List models command
        subparsers.add_parser('list-models', 
                            help='List available models')
        
        return parser
    
    @staticmethod
    def handle_config(args):
        """Handle config command"""
        if args.token:
            ConfigManager.set_token(args.token)
            print("✅ GitHub token saved successfully!")
            print(f"📁 Config file: {ConfigManager.get_config_path()}")
        
        elif args.model:
            ConfigManager.set_model(args.model)
            print(f"✅ Default model set to: {args.model}")
        
        elif args.show:
            ConfigManager.show_config()
        
        else:
            print("Usage: code-reviewer config [--token TOKEN] [--model MODEL] [--show]")
    
    @staticmethod
    def handle_review(args):
        """Handle review command"""
        # Get token
        token = ConfigManager.get_token()
        if not token:
            print("❌ GitHub token not found!")
            print("\nSet it using one of these methods:")
            print("  1. code-reviewer config --token YOUR_TOKEN")
            print("  2. export GITHUB_TOKEN=YOUR_TOKEN")
            print("\nGet your token from: https://github.com/settings/tokens")
            return 1
        
        # Get model
        model = args.model or ConfigManager.get_model()
        
        # Create config
        config = ReviewConfig(
            model=model,
            temperature=args.temperature
        )
        
        # Initialize reviewer
        try:
            reviewer = GitHubModelsCodeReviewer(token, config)
            path = Path(args.path)
            
            # Review file or directory
            if path.is_file():
                print(f"🔍 Reviewing file: {path}")
                result = reviewer.review_file(path)
                if result:
                    results = [result]
                else:
                    print("⚠️  File could not be reviewed")
                    return 1
            
            elif path.is_dir():
                print(f"🔍 Reviewing directory: {path}")
                if args.recursive:
                    print("📂 Scanning recursively...")
                results = reviewer.review_directory(path, args.recursive)
            
            else:
                print(f"❌ Path not found: {path}")
                return 1
            
            if not results:
                print("⚠️  No files to review")
                return 0
            
            # Generate output
            if args.format == 'console':
                for result in results:
                    ReportGenerator.print_console(result)
                ReportGenerator.print_summary(results)
            
            elif args.format == 'markdown':
                output = args.output or 'code_review_report.md'
                ReportGenerator.generate_markdown(results, output)
                ReportGenerator.print_summary(results)
            
            elif args.format == 'json':
                output = args.output or 'code_review_report.json'
                ReportGenerator.generate_json(results, output)
                ReportGenerator.print_summary(results)
            
            elif args.format == 'html':
                output = args.output or 'code_review_report.html'
                ReportGenerator.generate_html(results, output)
                ReportGenerator.print_summary(results)
            
            return 0
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return 1
    
    @staticmethod
    def handle_generate_action(args):
        """Handle generate-action command"""
        GitHubActionIntegration.generate_workflow(args.output)
        return 0
    
    @staticmethod
    def handle_install_hook(args):
        """Handle install-hook command"""
        GitHubActionIntegration.generate_pre_commit_hook()
        return 0
    
    @staticmethod
    def handle_list_models(args):
        """Handle list-models command"""
        print("\n🤖 Available Models on GitHub Models:\n")
        
        models = [
            ("gpt-4o", "Most capable, best for complex analysis"),
            ("gpt-4o-mini", "Fast and efficient, good for most tasks"),
            ("Llama-3.2-90B-Vision-Instruct", "Open source, strong performance"),
            ("Phi-3-medium-128k-instruct", "Smaller, faster model"),
            ("Mistral-large", "Good balance of speed and quality"),
            ("Mistral-small", "Fast and efficient"),
        ]
        
        for model, description in models:
            print(f"  • {model:<35} - {description}")
        
        print(f"\n💡 Set default model: code-reviewer config --model MODEL_NAME")
        print(f"📖 More models: https://github.com/marketplace/models\n")
        return 0
    
    @staticmethod
    def run():
        """Main entry point for CLI"""
        parser = CLI.create_parser()
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return 0
        
        # Route to appropriate handler
        handlers = {
            'config': CLI.handle_config,
            'review': CLI.handle_review,
            'generate-action': CLI.handle_generate_action,
            'install-hook': CLI.handle_install_hook,
            'list-models': CLI.handle_list_models,
        }
        
        handler = handlers.get(args.command)
        if handler:
            return handler(args)
        else:
            parser.print_help()
            return 0


def main():
    """Entry point wrapper"""
    try:
        sys.exit(CLI.run())
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)