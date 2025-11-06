"""Setup configuration for Zendesk Help Center Copy Tool"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zdhelpcopy",
    version="0.1.0",
    author="Your Name",
    description="Interactive CLI tool to copy Zendesk Help Center content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "click>=8.1.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "zdhelpcopy=zdhelpcopy.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
