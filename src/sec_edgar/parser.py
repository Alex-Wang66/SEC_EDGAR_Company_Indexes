"""
Parser module for SEC EDGAR company.idx files.
Extracts structured data from SEC index files.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class SECIndexParser:
    """
    Parses SEC EDGAR company.idx files.

    The idx file format (tab-separated, fixed structure):
    - Header: Company Name | Form Type | CIK | Date Filed | Filename
    """

    HEADER_ROWS = 10  # Number of header rows to skip
    COLUMN_NAMES = [
        "Company Name",
        "Form Type",
        "CIK",
        "Date Filed",
        "Filename"
    ]

    @staticmethod
    def parse_line(line: str) -> Optional[Dict[str, str]]:
        """
        Parse a single line from company.idx file.

        The format uses variable spacing but fixed column positions.
        Company name can contain spaces, so we split from the right.

        Args:
            line: A single line from the idx file

        Returns:
            Dictionary with parsed data, or None if parsing fails
        """
        parts = line.split()
        if len(parts) <= 4:
            return None

        # Split from the right: filename, date, cik, form_type, rest=company_name
        filename = parts[-1]
        date_filed = parts[-2]
        cik = parts[-3]
        form_type = parts[-4]
        company_name = " ".join(parts[:-4])

        return {
            "Company Name": company_name,
            "Form Type": form_type,
            "CIK": cik,
            "Date Filed": date_filed,
            "Filename": filename,
        }

    @staticmethod
    def parse_file(file_path: Path) -> pd.DataFrame:
        """
        Parse a company.idx file and return as DataFrame.

        Args:
            file_path: Path to company.idx file

        Returns:
            pandas DataFrame with parsed data
        """
        records = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Skip header rows
            for line in lines[SECIndexParser.HEADER_ROWS:]:
                line = line.strip()
                if not line:
                    continue

                parsed = SECIndexParser.parse_line(line)
                if parsed:
                    records.append(parsed)

            df = pd.DataFrame(records)
            logger.info(f"Parsed {len(df)} records from {file_path.name}")
            return df

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            raise

    @staticmethod
    def parse_directory(directory: Path) -> pd.DataFrame:
        """
        Parse all company.idx files in a directory.

        Args:
            directory: Path to directory containing .idx files

        Returns:
            Concatenated DataFrame from all files
        """
        idx_files = list(directory.glob("*.idx"))

        if not idx_files:
            logger.warning(f"No .idx files found in {directory}")
            return pd.DataFrame()

        dataframes = []
        for idx_file in sorted(idx_files):
            df = SECIndexParser.parse_file(idx_file)
            if not df.empty:
                dataframes.append(df)

        if not dataframes:
            logger.warning(f"No valid data found in {directory}")
            return pd.DataFrame()

        result = pd.concat(dataframes, ignore_index=True)
        logger.info(f"Total records from {len(idx_files)} files: {len(result)}")
        return result


def process_company_idx(
    file_path: Optional[Path] = None,
    directory: Optional[Path] = None
) -> pd.DataFrame:
    """
    Parse SEC company.idx file(s).

    Args:
        file_path: Path to a single .idx file
        directory: Path to directory containing .idx files

    Returns:
        pandas DataFrame with parsed company filing data

    Raises:
        ValueError: If neither file_path nor directory is provided
    """
    if file_path and file_path.exists():
        return SECIndexParser.parse_file(file_path)
    elif directory and directory.exists():
        return SECIndexParser.parse_directory(directory)
    else:
        raise ValueError("Must provide either file_path or directory")
