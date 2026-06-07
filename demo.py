#!/usr/bin/env python3
"""
Demo script for SEC EDGAR Company Indexes pipeline.
Shows practical examples of using the library.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from sec_edgar.main import SECEDGARPipeline
from sec_edgar.downloader import SECDownloader
from sec_edgar.parser import SECIndexParser
from sec_edgar.processor import DataProcessor


def demo_1_basic_pipeline():
    """Demo 1: Run complete pipeline with default settings."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Pipeline Execution")
    print("="*70)

    pipeline = SECEDGARPipeline()

    # For demo, skip download to save time
    results = pipeline.run(
        start_year=2024,
        end_year=2024,
        download=False,
        output_format="parquet"
    )

    if results["status"] == "success":
        print(f"\n✓ Pipeline completed successfully")
        print(f"Output file: {results.get('output_file')}")

        # Load and display results
        if "output_file" in results:
            try:
                df = pd.read_parquet(results["output_file"])
                print(f"\nDataset Summary:")
                print(f"  Total records: {len(df):,}")
                print(f"  Columns: {', '.join(df.columns.tolist())}")
                print(f"\nFirst 5 records:")
                print(df.head())
            except FileNotFoundError:
                print("  (Output file not found - check if download was skipped)")
    else:
        print(f"✗ Pipeline failed: {results['status']}")


def demo_2_custom_processing():
    """Demo 2: Custom data processing."""
    print("\n" + "="*70)
    print("DEMO 2: Custom Data Processing")
    print("="*70)

    print("\nLoading existing parquet file...")

    # Try to find existing parquet file
    data_dir = Path("data/processed")
    if not data_dir.exists():
        print("  (No processed data directory found)")
        return

    parquet_files = list(data_dir.glob("*.parquet"))
    if not parquet_files:
        print("  (No parquet files found in data/processed/)")
        return

    df = pd.read_parquet(parquet_files[0])
    print(f"Loaded {len(df):,} records from {parquet_files[0].name}")

    # Example 1: Statistics
    print("\n--- Dataset Statistics ---")
    stats = DataProcessor.get_statistics(df)
    print(f"Total companies: {stats['total_companies']:,}")
    print(f"Total records: {stats['total_records']:,}")
    print(f"Form types: {stats['form_types']}")
    if stats.get('date_range'):
        print(f"Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")

    # Example 2: Form type distribution
    print("\n--- Form Type Distribution ---")
    form_dist = df['Form Type'].value_counts().head(10)
    for form_type, count in form_dist.items():
        pct = count / len(df) * 100
        print(f"  {form_type:10s}: {count:6,d} ({pct:5.1f}%)")

    # Example 3: Top filing companies
    print("\n--- Top 10 Filing Companies ---")
    top_companies = df['Company Name'].value_counts().head(10)
    for i, (company, count) in enumerate(top_companies.items(), 1):
        print(f"  {i:2d}. {company:40s} ({count:d} filings)")

    # Example 4: Filter by form type
    print("\n--- Annual Reports (10-K) Only ---")
    annual_reports = df[df['Form Type'] == '10-K']
    print(f"Found {len(annual_reports):,} annual reports")
    if len(annual_reports) > 0:
        print(f"Unique companies: {annual_reports['Company Name'].nunique():,}")


def demo_3_api_usage():
    """Demo 3: Using the Python API directly."""
    print("\n" + "="*70)
    print("DEMO 3: Python API Usage Examples")
    print("="*70)

    # Example 1: Parser
    print("\n--- Parser Example ---")
    idx_files = list(Path("data/raw").glob("*.idx"))
    if idx_files:
        print(f"Found {len(idx_files)} .idx files")
        try:
            df = SECIndexParser.parse_file(idx_files[0])
            print(f"Parsed {len(df)} records from {idx_files[0].name}")
            print(f"Columns: {df.columns.tolist()}")
        except Exception as e:
            print(f"  (Could not parse file: {e})")
    else:
        print("  (No .idx files found in data/raw/)")

    # Example 2: DataProcessor
    print("\n--- Data Processor Example ---")
    print("Processor provides several cleaning functions:")
    print("  - clean_whitespace(df)")
    print("  - remove_empty_rows(df)")
    print("  - deduplicate(df, subset, keep, sort_by)")
    print("  - deduplicate_by_latest_data(df)")
    print("  - get_statistics(df)")

    # Example 3: Configuration
    print("\n--- Configuration Example ---")
    from sec_edgar.config import SEC_CONFIG, PROCESSING_CONFIG
    print("SEC Configuration:")
    print(f"  Base URL: {SEC_CONFIG['base_url']}")
    print(f"  Request delay: {SEC_CONFIG['request_delay']}s")
    print(f"  Timeout: {SEC_CONFIG['timeout']}s")
    print("\nProcessing Configuration:")
    print(f"  Default format: {PROCESSING_CONFIG['output_format']}")
    print(f"  Date column: {PROCESSING_CONFIG['date_column']}")


def demo_4_export_formats():
    """Demo 4: Export to different formats."""
    print("\n" + "="*70)
    print("DEMO 4: Export Format Examples")
    print("="*70)

    # Find existing parquet file
    parquet_files = list(Path("data/processed").glob("*.parquet"))
    if not parquet_files:
        print("  (No parquet files found to export)")
        return

    df = pd.read_parquet(parquet_files[0])
    print(f"\nLoaded {len(df):,} records")

    # Create sample output directory
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)

    # Export to different formats
    formats = [
        ("csv", df.to_csv),
        ("json", lambda f: df.to_json(f, orient="records")),
    ]

    print("\nExporting to different formats:")
    for format_name, export_func in formats:
        output_file = output_dir / f"sample_export.{format_name}"
        try:
            export_func(output_file)
            size_mb = output_file.stat().st_size / 1024 / 1024
            print(f"  ✓ {format_name.upper():6s}: {output_file} ({size_mb:.1f} MB)")
        except Exception as e:
            print(f"  ✗ {format_name.upper():6s}: {e}")


def demo_5_analysis():
    """Demo 5: Data analysis examples."""
    print("\n" + "="*70)
    print("DEMO 5: Data Analysis Examples")
    print("="*70)

    parquet_files = list(Path("data/processed").glob("*.parquet"))
    if not parquet_files:
        print("  (No parquet files found for analysis)")
        return

    df = pd.read_parquet(parquet_files[0])

    # Ensure date column is datetime
    df['Date Filed'] = pd.to_datetime(df['Date Filed'], errors='coerce')

    # Analysis 1: Companies with multiple filings
    print("\n--- Companies with Most Filings ---")
    multi_filers = df['Company Name'].value_counts()
    for i, (company, count) in enumerate(multi_filers.head(5).items(), 1):
        pct = count / len(df) * 100
        print(f"  {i}. {company:40s} {count:3d} filings ({pct:.1f}%)")

    # Analysis 2: Filing trends
    print("\n--- Filing Trends (by month) ---")
    if df['Date Filed'].notna().any():
        monthly_filings = df.set_index('Date Filed').resample('M').size()
        for date, count in monthly_filings.tail(6).items():
            print(f"  {date.strftime('%Y-%m')}: {count:4d} filings")

    # Analysis 3: Company size by filings
    print("\n--- Filing Frequency Distribution ---")
    filing_counts = df['Company Name'].value_counts()
    print(f"  1 filing:   {(filing_counts == 1).sum():4d} companies")
    print(f"  2-5 filings: {((filing_counts > 1) & (filing_counts <= 5)).sum():4d} companies")
    print(f"  6+ filings: {(filing_counts > 5).sum():4d} companies")


def main():
    """Run all demos."""
    print("\n" + "#"*70)
    print("# SEC EDGAR Company Indexes - Demo Script")
    print("#"*70)
    print("\nThis demo script shows various use cases for the library.")
    print("Note: Some demos require existing data files.")

    try:
        demo_1_basic_pipeline()
    except Exception as e:
        print(f"Demo 1 error: {e}")

    try:
        demo_2_custom_processing()
    except Exception as e:
        print(f"Demo 2 error: {e}")

    try:
        demo_3_api_usage()
    except Exception as e:
        print(f"Demo 3 error: {e}")

    try:
        demo_4_export_formats()
    except Exception as e:
        print(f"Demo 4 error: {e}")

    try:
        demo_5_analysis()
    except Exception as e:
        print(f"Demo 5 error: {e}")

    print("\n" + "#"*70)
    print("# Demo completed!")
    print("#"*70)
    print("\nFor more information, see:")
    print("  - README.md: Project overview")
    print("  - USAGE.md: Detailed usage guide")
    print("  - DATA_FORMAT.md: Data format specification")


if __name__ == "__main__":
    main()
