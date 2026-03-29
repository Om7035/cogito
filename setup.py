from setuptools import setup, find_packages

setup(
    name="cogito",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "yfinance",
        "click",
        "python-dotenv",
        "pytest",
    ],
    entry_points={
        "console_scripts": [
            "cogito=cogito.cli:cli",
        ],
    },
)
