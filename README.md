# 🤖 AI Code Reviewer

A powerful CLI tool that uses GitHub Models to perform comprehensive code reviews with AI.

## ✨ Features

- ✅ Multi-language support (Python, JavaScript, Java, C++, Go, Rust, and more)
- 📊 Code complexity metrics analysis
- 🐛 Bug detection
- 🔒 Security vulnerability scanning
- 💡 Improvement suggestions
- 📚 Best practices validation
- 📝 Markdown & JSON report generation
- 🤖 GitHub Actions integration for PR reviews
- 📁 Single file or directory review
- 🔄 Recursive directory scanning

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure GitHub token
python code_reviewer.py config --token YOUR_GITHUB_TOKEN

# Review a file
python code_reviewer.py review examples/sample.py

# Review a directory with markdown report
python code_reviewer.py review examples/ --recursive --format markdown --output report.md

# Use different AI model
python code_reviewer.py review mycode.py --model gpt-4o-mini

# Generate GitHub Action
python code_reviewer.py generate-action

# Show configuration
python code_reviewer.py config --show
```

## 📖 Usage

### Commands

```bash
# Review single file
python code_reviewer.py review mycode.py

# Review directory recursively
python code_reviewer.py review ./src --recursive

# Generate reports
python code_reviewer.py review ./src --format markdown --output report.md
python code_reviewer.py review ./src --format json --output report.json

# Use different models
python code_reviewer.py review mycode.py --model gpt-4o-mini

# Configuration
python code_reviewer.py config --token YOUR_TOKEN
python code_reviewer.py config --show

# Generate GitHub Action
python code_reviewer.py generate-action
```

## 🎯 Supported Languages

Python, JavaScript, TypeScript, Java, C++, C, Go, Rust, Ruby, PHP, Swift, Kotlin, C#

## 📝 Example Output

```
======================================================================
📁 FILE: src/main.py
🔤 LANGUAGE: Python
📊 QUALITY SCORE: 7/10
======================================================================

📈 COMPLEXITY METRICS:
  • Total Lines: 50
  • Code Lines: 35
  • Functions: 3
  • Classes: 1

📝 SUMMARY:
Good code structure with clear separation of concerns...

🐛 POTENTIAL BUGS:
  1. Division by zero not handled in calculate_average function
  2. Potential KeyError if 'name' key doesn't exist in dictionary

🔒 SECURITY ISSUES:
  1. User input not sanitized before database query

💡 IMPROVEMENTS:
  1. Add docstrings to all functions
  2. Implement proper exception handling
  3. Use type hints for function parameters
```

## 🤖 GitHub Actions

Generate a workflow to automatically review PRs:

```bash
python code_reviewer.py generate-action
```

Add `GITHUB_MODELS_TOKEN` to your repository secrets, then push the generated workflow file.

## 🎣 Pre-commit Hook

Automate code reviews before every commit to catch issues early.

### Installation

To install the pre-commit hook, run:

```bash
python code_reviewer.py install-hook
```

This will create a `pre-commit` file in your `.git/hooks/` directory. The hook will automatically run `python code_reviewer.py review` on your staged files before each commit.

### Usage

1.  **Stage your changes:**
    ```bash
    git add .
    ```
2.  **Commit your changes:**
    ```bash
    git commit -m "Your commit message"
    ```
    The AI code review will run, and any findings will be displayed in your console. If the review process encounters an error or if you have not configured your `GITHUB_TOKEN`, the commit might be aborted.

### Using with `pre-commit` framework (Optional)

If you are using the `pre-commit` framework, you can integrate the AI Code Reviewer by adding the following to your `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: ai-code-review
      name: AI Code Review
      entry: python code_reviewer.py review
      language: system
      files: \.(py|js|ts|java|cpp|go|rs)$
      pass_filenames: true
      always_run: true
```

Remember to configure your GitHub token using `python code_reviewer.py config --token YOUR_GITHUB_TOKEN` or by setting the `GITHUB_TOKEN` environment variable.

## 📄 License

MIT License
