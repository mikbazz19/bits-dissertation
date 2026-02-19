"""Setup configuration for the AI Resume Screening System"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="ai-resume-screening",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered system for automated resume screening and job matching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dissertation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "spacy>=3.7.0",
        "PyPDF2>=3.0.0",
        "python-docx>=1.1.0",
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        "streamlit>=1.28.0",
        "nltk>=3.8",
        "scikit-learn>=1.3.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.10.0",
            "flake8>=6.1.0",
        ],
        "viz": [
            "matplotlib>=3.8.0",
            "seaborn>=0.13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "resume-screening=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/*.json", "data/sample_resumes/*", "data/sample_jobs/*"],
    },
)
