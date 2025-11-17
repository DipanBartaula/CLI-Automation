```python
"""Setup script for AgentOS."""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="agentos",
    version="0.1.0",
    description="Intelligent computer automation via CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/agentos",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "openai>=1.12.0",
        "chromadb>=0.4.22",
        "sentence-transformers>=2.3.1",
        "click>=8.1.7",
        "rich>=13.7.0",
        "prompt-toolkit>=3.0.43",
        "psutil>=5.9.8",
        "pyperclip>=1.8.2",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "pydantic>=2.5.3",
        "tenacity>=8.2.3",
        "structlog>=24.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentos=agentos.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
```