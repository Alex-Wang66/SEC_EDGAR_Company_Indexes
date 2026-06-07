"""
Downloader module for SEC EDGAR company filing index files.
Downloads company.idx files from SEC's EDGAR database.
"""

import time
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

import requests

from .config import SEC_CONFIG, DATA_RAW_DIR, LOGS_DIR

logger = logging.getLogger(__name__)


class SECDownloader:
    """
    Downloads SEC EDGAR company filing index files.

    The company.idx files contain quarterly indices of all company filings
    submitted to the SEC.
    """

    def __init__(self, base_url: str = SEC_CONFIG["base_url"],
                 request_delay: float = SEC_CONFIG["request_delay"],
                 output_dir: Optional[Path] = None):
        """
        Initialize the SEC downloader.

        Args:
            base_url: SEC EDGAR base URL
            request_delay: Delay between requests in seconds (SEC guidelines)
            output_dir: Directory to save downloaded files
        """
        self.base_url = base_url
        self.request_delay = request_delay
        self.output_dir = output_dir or DATA_RAW_DIR
        self.session = requests.Session()
        self.session.headers.update(SEC_CONFIG["headers"])
        self._successful_downloads = []
        self._failed_downloads = []

    def _get_latest_quarter(self) -> Dict[str, int]:
        """
        Determine the latest published quarter based on current date.

        Returns:
            Dict with 'year' and 'quarter' keys
        """
        current_year = datetime.now().year
        current_month = datetime.now().month

        if 1 <= current_month <= 3:
            latest_qtr = 0
        elif 4 <= current_month <= 6:
            latest_qtr = 1
        elif 7 <= current_month <= 9:
            latest_qtr = 2
        else:
            latest_qtr = 3

        return {"year": current_year, "quarter": latest_qtr}

    def download_file(self, year: int, quarter: int) -> bool:
        """
        Download a single company.idx file for a specific year and quarter.

        Args:
            year: Year (e.g., 2023)
            quarter: Quarter index (0-3 for QTR1-QTR4)

        Returns:
            True if successful, False otherwise
        """
        try:
            qtr_str = f"QTR{quarter + 1}"
            url = f"{self.base_url}/{year}/{qtr_str}/company.idx"

            logger.info(f"Downloading: {url}")

            response = self.session.get(
                url,
                timeout=SEC_CONFIG["timeout"]
            )
            response.raise_for_status()

            # Create output directory if needed
            year_dir = self.output_dir / str(year)
            year_dir.mkdir(parents=True, exist_ok=True)

            # Save file
            output_file = year_dir / f"company_{year}_{qtr_str}.idx"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response.text)

            logger.info(f"✓ Saved to: {output_file}")
            self._successful_downloads.append({
                "year": year,
                "quarter": qtr_str,
                "file": str(output_file)
            })

            time.sleep(self.request_delay)
            return True

        except requests.RequestException as e:
            logger.error(f"✗ Failed to download {year} {qtr_str}: {e}")
            self._failed_downloads.append({
                "year": year,
                "quarter": qtr_str,
                "error": str(e)
            })
            return False

    def download_range(self, start_year: int, end_year: Optional[int] = None) -> Dict:
        """
        Download company.idx files for a range of years.

        Args:
            start_year: Starting year (e.g., 2023)
            end_year: Ending year (inclusive). If None, uses current year

        Returns:
            Dict with download statistics
        """
        if end_year is None:
            end_year = datetime.now().year

        logger.info(f"Starting download for years {start_year}-{end_year}")

        total_files = 0
        successful = 0

        for year in range(start_year, end_year + 1):
            latest_qtr = self._get_latest_quarter()
            max_quarter = 4 if year < latest_qtr["year"] else latest_qtr["quarter"] + 1

            for qtr in range(max_quarter):
                total_files += 1
                if self.download_file(year, qtr):
                    successful += 1

        stats = {
            "total_files": total_files,
            "successful": successful,
            "failed": total_files - successful,
            "successful_downloads": self._successful_downloads,
            "failed_downloads": self._failed_downloads,
        }

        logger.info(f"Download complete: {successful}/{total_files} files successfully downloaded")
        return stats


def download_sec_company_idx(
    start_year: int = SEC_CONFIG["start_year"],
    end_year: Optional[int] = None,
    output_dir: Optional[Path] = None
) -> Dict:
    """
    Main function to download SEC EDGAR company index files.

    Args:
        start_year: Starting year for download
        end_year: Ending year for download (None = current year)
        output_dir: Directory to save files

    Returns:
        Dictionary with download statistics
    """
    downloader = SECDownloader(output_dir=output_dir)
    return downloader.download_range(start_year, end_year)
