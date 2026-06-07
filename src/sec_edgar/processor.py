"""
Data processor module for SEC EDGAR company filing data.
Handles cleaning, deduplication, and transformation.
"""

import logging
from typing import List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes and cleans SEC EDGAR company filing data.
    """

    @staticmethod
    def convert_date_column(
        df: pd.DataFrame,
        date_column: str = "Date Filed",
        errors: str = 'coerce'
    ) -> pd.DataFrame:
        """
        Convert date column to datetime format.

        Args:
            df: Input DataFrame
            date_column: Name of the date column
            errors: How to handle parsing errors ('coerce', 'raise', 'ignore')

        Returns:
            DataFrame with converted date column
        """
        if date_column not in df.columns:
            logger.warning(f"Column '{date_column}' not found in DataFrame")
            return df

        df_copy = df.copy()
        df_copy[date_column] = pd.to_datetime(
            df_copy[date_column],
            errors=errors,
            format='%Y-%m-%d'
        )
        logger.info(f"Converted '{date_column}' to datetime")
        return df_copy

    @staticmethod
    def deduplicate(
        df: pd.DataFrame,
        subset: List[str],
        keep: str = 'first',
        sort_by: Optional[str] = None,
        ascending: bool = False
    ) -> pd.DataFrame:
        """
        Deduplicate records based on specified columns.

        Args:
            df: Input DataFrame
            subset: Columns to consider for deduplication
            keep: Which duplicate to keep ('first', 'last')
            sort_by: Column to sort by before deduplication
            ascending: Sort direction

        Returns:
            Deduplicated DataFrame
        """
        df_copy = df.copy()

        if sort_by and sort_by in df_copy.columns:
            df_copy = df_copy.sort_values(
                sort_by,
                ascending=ascending,
                na_position='last'
            )

        duplicates_before = len(df_copy)
        df_copy = df_copy.drop_duplicates(subset=subset, keep=keep)
        duplicates_removed = duplicates_before - len(df_copy)

        logger.info(
            f"Deduplication: Removed {duplicates_removed} duplicates "
            f"({duplicates_before} → {len(df_copy)} records)"
        )
        return df_copy

    @staticmethod
    def deduplicate_by_latest_data(
        df: pd.DataFrame,
        date_column: str = "Date Filed"
    ) -> pd.DataFrame:
        """
        Deduplicate by keeping the latest filing for each company.

        Args:
            df: Input DataFrame
            date_column: Column containing filing dates

        Returns:
            Deduplicated DataFrame with latest records only
        """
        df_copy = DataProcessor.convert_date_column(df, date_column)
        df_dedup = DataProcessor.deduplicate(
            df_copy,
            subset=["Company Name"],
            keep="first",
            sort_by=date_column,
            ascending=False
        )
        return df_dedup

    @staticmethod
    def clean_whitespace(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean leading/trailing whitespace from string columns.

        Args:
            df: Input DataFrame

        Returns:
            Cleaned DataFrame
        """
        df_copy = df.copy()
        string_cols = df_copy.select_dtypes(include=['object']).columns
        for col in string_cols:
            df_copy[col] = df_copy[col].str.strip()
        logger.info(f"Cleaned whitespace from {len(string_cols)} columns")
        return df_copy

    @staticmethod
    def remove_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove rows where all values are null.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with empty rows removed
        """
        rows_before = len(df)
        df_copy = df.dropna(how='all')
        rows_removed = rows_before - len(df_copy)
        logger.info(f"Removed {rows_removed} empty rows")
        return df_copy

    @staticmethod
    def get_statistics(df: pd.DataFrame) -> dict:
        """
        Generate summary statistics for the dataset.

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_records": len(df),
            "total_companies": df["Company Name"].nunique() if "Company Name" in df.columns else 0,
            "form_types": df["Form Type"].nunique() if "Form Type" in df.columns else 0,
            "date_range": None,
        }

        if "Date Filed" in df.columns:
            df_with_date = pd.to_datetime(
                df["Date Filed"],
                errors='coerce'
            )
            valid_dates = df_with_date.dropna()
            if not valid_dates.empty:
                stats["date_range"] = {
                    "start": str(valid_dates.min()),
                    "end": str(valid_dates.max()),
                }

        return stats


def deduplicate_by_latest_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function for deduplicating by latest data.

    Args:
        df: Input DataFrame with company filing data

    Returns:
        Deduplicated DataFrame
    """
    return DataProcessor.deduplicate_by_latest_data(df)
