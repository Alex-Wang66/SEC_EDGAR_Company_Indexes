"""
Configuration settings for SEC EDGAR data pipeline.
"""

from pathlib import Path
from typing import Dict

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Data directories
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_RAW_DIR, DATA_PROCESSED_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# SEC EDGAR Configuration
SEC_CONFIG = {
    "base_url": "https://www.sec.gov/Archives/edgar/full-index",
    "start_year": 2023,
    "request_delay": 0.2,  # seconds between requests
    "timeout": 30,  # request timeout in seconds
    "headers": {
        "User-Agent": "SEC EDGAR Data Pipeline - Educational Use (wangjle9@mail2.sysu.edu.cn)",
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov"
    }
}

# Data Processing Configuration
PROCESSING_CONFIG = {
    "deduplicate_on": ["Company Name"],  # columns to deduplicate on
    "date_column": "Date Filed",
    "output_format": "parquet",  # options: parquet, csv, json
}

# Logging Configuration
LOGGING_CONFIG: Dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "sec_edgar": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True
        }
    }
}
