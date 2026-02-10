"""
Adaptive Neuromodulation System for Parkinson's Disease
Setup configuration for package installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="adaptive-neuromodulation-dbs",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Closed-loop brain-computer interface for adaptive deep brain stimulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/adaptive-neuromodulation-dbs",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "pandas>=1.3.0",
        "tvb-library>=2.6",
        "python-control>=0.9.0",
        "scikit-learn>=1.0.0",
        "torch>=1.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "mypy>=0.950",
        ],
        "ml": [
            "stable-baselines3>=1.5.0",
            "gym>=0.21.0",
        ],
        "viz": [
            "plotly>=5.0.0",
            "dash>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "run-dbs-simulation=src.scripts.run_simulation:main",
            "launch-dashboard=src.visualization.dashboard:main",
        ],
    },
)
