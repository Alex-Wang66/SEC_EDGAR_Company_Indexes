"""
Main module for SEC EDGAR data pipeline.
Orchestrates the complete workflow: download → parse → process → save.
"""

import logging
import logging.config
from pathlib import Path
from typing import Optional, Dict

import pandas as pd

from .config import LOGGING_CONFIG, DATA_RAW_DIR, DATA_PROCESSED_DIR, PROCESSING_CONFIG
from .downloader import SECDownloader
from .parser import SECIndexParser
from .processor import DataProcessor

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class SECEDGARPipeline:
    """
    Complete pipeline for SEC EDGAR company filing data.

    Workflow:
    1. Download company.idx files from SEC website
    2. Parse idx files into structured data
    3. Process and clean the data
    4. Save to output format (parquet, csv, etc.)
    """

    def __init__(
        self,
        raw_data_dir: Path = DATA_RAW_DIR,
        processed_data_dir: Path = DATA_PROCESSED_DIR,
    ):
        """
        Initialize the pipeline.

        Args:
            raw_data_dir: Directory for raw downloaded files
            processed_data_dir: Directory for processed output
        """
        self.raw_data_dir = raw_data_dir
        self.processed_data_dir = processed_data_dir
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        start_year: int,
        end_year: Optional[int] = None,
        download: bool = True,
        output_format: str = "parquet"
    ) -> Dict:
        """
        Run the complete pipeline.

        Args:
            start_year: Starting year for data collection
            end_year: Ending year for data collection (None = current year)
            download: Whether to download files (True) or use existing (False)
            output_format: Output format ('parquet', 'csv', 'json')

        Returns:
            Dictionary with pipeline results and statistics
        """
        logger.info("="*60)
        logger.info("SEC EDGAR Data Pipeline Started")
        logger.info("="*60)

        results = {
            "status": "pending",
            "stages": {},
        }

        # Stage 1: Download
        if download:
            logger.info("\n[Stage 1/3] Downloading SEC EDGAR index files...")
            try:
                downloader = SECDownloader(output_dir=self.raw_data_dir)
                download_stats = downloader.download_range(start_year, end_year)
                results["stages"]["download"] = {
                    "status": "success",
                    "statistics": download_stats,
                }
                logger.info(f"✓ Downloaded {download_stats['successful']} files")
            except Exception as e:
                logger.error(f"✗ Download failed: {e}")
                results["status"] = "failed"
                results["stages"]["download"] = {"status": "failed", "error": str(e)}
                return results
        else:
            logger.info("\n[Stage 1/3] Skipping download (using existing files)")

        # Stage 2: Parse
        logger.info("\n[Stage 2/3] Parsing company index files...")
        try:
            df = SECIndexParser.parse_directory(self.raw_data_dir)
            if df.empty:
                raise ValueError("No data parsed from index files")

            results["stages"]["parse"] = {
                "status": "success",
                "records": len(df),
            }
            logger.info(f"✓ Parsed {len(df)} records")
        except Exception as e:
            logger.error(f"✗ Parsing failed: {e}")
            results["status"] = "failed"
            results["stages"]["parse"] = {"status": "failed", "error": str(e)}
            return results

        # Stage 3: Process
        logger.info("\n[Stage 3/3] Processing and cleaning data...")
        try:
            # Clean whitespace
            df = DataProcessor.clean_whitespace(df)

            # Remove empty rows
            df = DataProcessor.remove_empty_rows(df)

            # Deduplicate by latest data
            df = DataProcessor.deduplicate_by_latest_data(df)

            # Get statistics
            stats = DataProcessor.get_statistics(df)

            results["stages"]["process"] = {
                "status": "success",
                "records": len(df),
                "statistics": stats,
            }
            logger.info(f"✓ Processed {len(df)} final records")
        except Exception as e:
            logger.error(f"✗ Processing failed: {e}")
            results["status"] = "failed"
            results["stages"]["process"] = {"status": "failed", "error": str(e)}
            return results

        # Save results
        logger.info(f"\nSaving results as {output_format.upper()}...")
        try:
            output_file = self._save_data(df, output_format)
            results["output_file"] = str(output_file)
            logger.info(f"✓ Saved to: {output_file}")
        except Exception as e:
            logger.error(f"✗ Save failed: {e}")
            results["status"] = "failed"
            results["save"] = {"status": "failed", "error": str(e)}
            return results

        results["status"] = "success"
        logger.info("\n" + "="*60)
        logger.info("SEC EDGAR Data Pipeline Completed Successfully")
        logger.info("="*60)

        return results

    def _save_data(self, df: pd.DataFrame, format: str) -> Path:
        """
        Save processed data to specified format.

        Args:
            df: DataFrame to save
            format: Output format ('parquet', 'csv', 'json')

        Returns:
            Path to saved file
        """
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"company_files_{timestamp}.{format}"
        output_path = self.processed_data_dir / filename

        if format == "parquet":
            df.to_parquet(output_path, index=False)
        elif format == "csv":
            df.to_csv(output_path, index=False)
        elif format == "json":
            df.to_json(output_path, orient="records", date_format="iso")
        else:
            raise ValueError(f"Unsupported format: {format}")

        return output_path


def run_pipeline(
    start_year: int,
    end_year: Optional[int] = None,
    download: bool = True,
    output_format: str = PROCESSING_CONFIG["output_format"]
) -> Dict:
    """
    Convenience function to run the complete pipeline.

    Args:
        start_year: Starting year for data collection
        end_year: Ending year (None = current year)
        download: Whether to download files
        output_format: Output format ('parquet', 'csv', 'json')

    Returns:
        Pipeline results
    """
    pipeline = SECEDGARPipeline()
    return pipeline.run(start_year, end_year, download, output_format)
