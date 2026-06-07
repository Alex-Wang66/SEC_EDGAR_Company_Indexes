"""
SEC EDGAR Company Indexes - Data Pipeline
A data engineering project for fetching and processing SEC EDGAR company filing indexes.
"""

__version__ = "1.0.0"
__author__ = "Alex Wang"
__email__ = "wangjle9@mail2.sysu.edu.cn"

from .downloader import download_sec_company_idx
from .parser import process_company_idx
from .processor import deduplicate_by_latest_data

__all__ = [
    "download_sec_company_idx",
    "process_company_idx",
    "deduplicate_by_latest_data",
]
