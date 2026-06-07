"""
Setup configuration for SEC EDGAR Company Indexes project.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sec-edgar-company-indexes",
    version="1.0.0",
    author="Alex Wang",
    author_email="wangjle9@mail2.sysu.edu.cn",
    description="Fetch and process SEC EDGAR company filing indexes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Alex-Wang66/SEC_EDGAR_Company_Indexes",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "pyarrow>=12.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "sec-edgar-pipeline=sec_edgar.main:run_pipeline",
        ],
    },
)
