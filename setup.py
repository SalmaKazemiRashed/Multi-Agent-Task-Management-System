"""
Setup configuration for the multi-agent system package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="multi-agent-system",
    version="1.0.0",
    author="Salma_KR",
    description="A Python-based multi-agent system for task management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SalmaKazemiRashed/Multi-Agent-Task-Management-System.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "asyncio>=3.4.3",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "pydantic>=2.0.0",
        "colorlog>=6.7.0",
        "networkx>=3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "viz": [
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
        ],
    },
)