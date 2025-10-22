"""
GitHub Actions integration
"""

from pathlib import Path


class GitHubActionIntegration:
    """GitHub Action workflow generator"""
    
    @staticmethod
    def generate_workflow(output_file: str = ".github/workflows/code-review.yml"):
        """
        Generate a GitHub Action workflow file
        
        Args:
            output_file: Path where workflow file should be created
        """
        workflow = """name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests
      
      - name: Get changed files
        id: changed-files
        uses: tj-actions/changed-files@v40
        with:
          files: |
            **.py
            **.js
            **.ts
            **.java
            **.cpp
            **.go
            **.rs
      
      - name: Download code reviewer
        run: |
          # Download the code reviewer from your repo
          # Assuming code_reviewer.py is in the root
          ls -la
      
      - name: Run AI Code Review
        if: steps.changed-files.outputs.any_changed == 'true'
        env:
          GITHUB_TOKEN: ${{ secrets.MODELS_GITHUB_TOKEN }}
        run: |
          mkdir -p review-results changed-files
          
          # Review each changed file
          for file in ${{ steps.changed-files.outputs.all_changed_files }}; do
            echo "Reviewing $file..."
            python code_reviewer.py review "$file" --format json --output "review-results/$(basename $file).json" || true
            cp "$file" "changed-files/$(basename $file)"
          done
          
          # Generate combined markdown report
          python code_reviewer.py review changed-files/ --recursive --format markdown --output review-results/summary.md || true

          # Delete changed-files directory
          rm -rf changed-files
      
      - name: Comment on PR
        if: steps.changed-files.outputs.any_changed == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const path = require('path');
            
            // Read the summary report
            let comment = '## 🤖 AI Code Review Results\\n\\n';
            
            try {
              const summary = fs.readFileSync('review-results/summary.md', 'utf8');
              comment += summary;
            } catch (error) {
              comment += 'Unable to generate review summary.\\n';
              console.error(error);
            }
            
            // Post comment
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
      
      - name: Upload review results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: code-review-results
          path: review-results/
          retention-days: 30
"""
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(workflow)
        
        print(f"✅ GitHub Action workflow created: {output_file}")
    
    @staticmethod
    def generate_pre_commit_hook():
        """Generate a pre-commit hook for local reviews"""
        hook_content = """#!/bin/bash
# Pre-commit hook for AI code review

echo "🔍 Running AI code review on staged files..."

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\\.(py|js|ts|java|cpp|go|rs))

if [ -z "$STAGED_FILES" ]; then
    echo "✅ No code files to review"
    exit 0
fi

# Review staged files
for file in $STAGED_FILES; do
    echo "Reviewing $file..."
    python code_reviewer.py review "$file" --format console
done

echo "✅ Code review complete!"
"""
        
        hook_path = Path(".git/hooks/pre-commit")
        
        if not hook_path.parent.exists():
            print("❌ Not a git repository")
            return
        
        with open(hook_path, 'w') as f:
            f.write(hook_content)
        
        # Make executable
        import os
        os.chmod(hook_path, 0o755)
        
        print(f"✅ Pre-commit hook installed: {hook_path}")
        print("Now your code will be reviewed before each commit!")