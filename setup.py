from setuptools import setup

setup(
    name="ai-code-reviewer",
    version="1.0.0",
    description="AI-powered code reviewer using GitHub Models",
    py_modules=["code_reviewer"],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "code-reviewer=code_reviewer:main",
        ],
    },
)
