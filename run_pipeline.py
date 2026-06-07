#!/usr/bin/env python3
"""
Command-line interface for SEC EDGAR data pipeline.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sec_edgar.main import SECEDGARPipeline
from sec_edgar.config import LOGGING_CONFIG
import logging.config

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="SEC EDGAR Company Filing Data Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --start-year 2023                     # Download 2023 to current year
  %(prog)s --start-year 2023 --end-year 2024    # Download 2023-2024
  %(prog)s --skip-download                       # Process existing files
  %(prog)s --start-year 2023 --format csv        # Output as CSV
        """
    )

    parser.add_argument(
        "--start-year",
        type=int,
        default=2023,
        help="Starting year for data collection (default: 2023)"
    )

    parser.add_argument(
        "--end-year",
        type=int,
        default=None,
        help="Ending year for data collection (default: current year)"
    )

    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip download stage and use existing files"
    )

    parser.add_argument(
        "--format",
        choices=["parquet", "csv", "json"],
        default="parquet",
        help="Output format (default: parquet)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger("sec_edgar").setLevel(logging.DEBUG)

    # Create and run pipeline
    pipeline = SECEDGARPipeline()
    results = pipeline.run(
        start_year=args.start_year,
        end_year=args.end_year,
        download=not args.skip_download,
        output_format=args.format
    )

    # Print results summary
    if results["status"] == "success":
        logger.info("\nPipeline Summary:")
        logger.info(f"  Output: {results.get('output_file', 'N/A')}")
        if "process" in results["stages"]:
            stats = results["stages"]["process"].get("statistics", {})
            logger.info(f"  Total records: {stats.get('total_records', 0):,}")
            logger.info(f"  Unique companies: {stats.get('total_companies', 0):,}")
            logger.info(f"  Form types: {stats.get('form_types', 0)}")
        return 0
    else:
        logger.error(f"Pipeline failed: {results.get('status')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
