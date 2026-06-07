"""
Unit tests for sec_edgar package.
"""

import unittest
from pathlib import Path
import tempfile
import pandas as pd
from datetime import datetime

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sec_edgar.parser import SECIndexParser
from sec_edgar.processor import DataProcessor
from sec_edgar.config import SEC_CONFIG


class TestSECIndexParser(unittest.TestCase):
    """Test cases for SECIndexParser."""

    def test_parse_line_valid(self):
        """Test parsing a valid index file line."""
        line = "Apple Inc.\t10-K\t0000320193\t2024-03-15\tedgar/data/320193/0000320193-24-000015.txt"
        result = SECIndexParser.parse_line(line)

        self.assertIsNotNone(result)
        self.assertEqual(result["Company Name"], "Apple Inc.")
        self.assertEqual(result["Form Type"], "10-K")
        self.assertEqual(result["CIK"], "0000320193")
        self.assertEqual(result["Date Filed"], "2024-03-15")

    def test_parse_line_company_with_spaces(self):
        """Test parsing company name with spaces."""
        line = "Microsoft Corporation Inc.\t10-Q\t0000789019\t2024-05-14\tedgar/data/789019/file.txt"
        result = SECIndexParser.parse_line(line)

        self.assertEqual(result["Company Name"], "Microsoft Corporation Inc.")

    def test_parse_line_invalid_short(self):
        """Test parsing invalid line (too short)."""
        line = "Apple\t10-K"
        result = SECIndexParser.parse_line(line)

        self.assertIsNone(result)

    def test_parse_line_empty(self):
        """Test parsing empty line."""
        result = SECIndexParser.parse_line("")
        self.assertIsNone(result)


class TestDataProcessor(unittest.TestCase):
    """Test cases for DataProcessor."""

    def setUp(self):
        """Set up test data."""
        self.test_df = pd.DataFrame({
            "Company Name": ["Apple Inc.", "Apple Inc.", "Microsoft Corp.", "Tesla Inc."],
            "Form Type": ["10-K", "10-Q", "10-K", "8-K"],
            "CIK": ["0000320193", "0000320193", "0000789019", "0001018724"],
            "Date Filed": ["2024-03-15", "2024-05-14", "2024-04-22", "2024-06-01"],
            "Filename": ["file1.txt", "file2.txt", "file3.txt", "file4.txt"],
        })

    def test_clean_whitespace(self):
        """Test whitespace cleaning."""
        df = pd.DataFrame({
            "name": ["  Apple  ", "  Microsoft  "],
            "type": ["10-K", "10-Q"]
        })

        df_clean = DataProcessor.clean_whitespace(df)

        self.assertEqual(df_clean["name"].iloc[0], "Apple")
        self.assertEqual(df_clean["name"].iloc[1], "Microsoft")

    def test_remove_empty_rows(self):
        """Test removing completely empty rows."""
        df = pd.DataFrame({
            "A": [1, None, 3],
            "B": [4, None, 6],
            "C": [7, 8, 9],
        })

        df_clean = DataProcessor.remove_empty_rows(df)

        # Row with all nulls removed
        self.assertEqual(len(df_clean), 2)

    def test_convert_date_column(self):
        """Test date column conversion."""
        df = pd.DataFrame({
            "Date": ["2024-03-15", "2024-05-14", "invalid-date"],
        })

        df_converted = DataProcessor.convert_date_column(
            df,
            date_column="Date",
            errors='coerce'
        )

        self.assertEqual(df_converted["Date"].dtype, 'datetime64[ns]')
        self.assertIsNotNone(df_converted["Date"].iloc[0])
        self.assertTrue(pd.isna(df_converted["Date"].iloc[2]))

    def test_deduplicate_keep_first(self):
        """Test deduplication keeping first record."""
        df_dedup = DataProcessor.deduplicate(
            self.test_df,
            subset=["Company Name"],
            keep="first"
        )

        # Should keep 3 unique companies
        self.assertEqual(len(df_dedup), 3)
        self.assertTrue(df_dedup[df_dedup["Company Name"] == "Apple Inc."]["Form Type"].iloc[0] == "10-K")

    def test_deduplicate_keep_last(self):
        """Test deduplication keeping last record."""
        df_dedup = DataProcessor.deduplicate(
            self.test_df,
            subset=["Company Name"],
            keep="last"
        )

        # Should keep 3 unique companies
        self.assertEqual(len(df_dedup), 3)

    def test_deduplicate_by_latest_data(self):
        """Test deduplication by latest date."""
        df_dedup = DataProcessor.deduplicate_by_latest_data(self.test_df)

        # Should have unique companies
        self.assertEqual(len(df_dedup), self.test_df["Company Name"].nunique())

    def test_get_statistics(self):
        """Test statistics generation."""
        stats = DataProcessor.get_statistics(self.test_df)

        self.assertEqual(stats["total_records"], 4)
        self.assertGreaterEqual(stats["total_companies"], 3)
        self.assertGreaterEqual(stats["form_types"], 3)


class TestConfiguration(unittest.TestCase):
    """Test cases for configuration."""

    def test_sec_config_exists(self):
        """Test that SEC configuration exists."""
        self.assertIn("base_url", SEC_CONFIG)
        self.assertIn("request_delay", SEC_CONFIG)
        self.assertIn("timeout", SEC_CONFIG)
        self.assertIn("headers", SEC_CONFIG)

    def test_sec_config_values(self):
        """Test SEC configuration values."""
        self.assertEqual(
            SEC_CONFIG["base_url"],
            "https://www.sec.gov/Archives/edgar/full-index"
        )
        self.assertGreaterEqual(SEC_CONFIG["request_delay"], 0)
        self.assertGreater(SEC_CONFIG["timeout"], 0)

    def test_headers_user_agent(self):
        """Test that User-Agent is set."""
        self.assertIn("User-Agent", SEC_CONFIG["headers"])
        user_agent = SEC_CONFIG["headers"]["User-Agent"]
        self.assertIn("SEC", user_agent)


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    def test_full_processing_pipeline(self):
        """Test complete data processing pipeline."""
        # Create sample data
        df = pd.DataFrame({
            "Company Name": ["  Apple Inc.  ", "  Apple Inc.  ", "Microsoft Corp.", "Tesla Inc."],
            "Form Type": ["10-K", "10-Q", "10-K", "8-K"],
            "CIK": ["0000320193", "0000320193", "0000789019", "0001018724"],
            "Date Filed": ["2024-03-15", "2024-05-14", "2024-04-22", "2024-06-01"],
            "Filename": ["file1.txt", "file2.txt", "file3.txt", "file4.txt"],
        })

        # Apply processing pipeline
        df = DataProcessor.clean_whitespace(df)
        df = DataProcessor.remove_empty_rows(df)
        df = DataProcessor.deduplicate_by_latest_data(df)

        # Verify results
        self.assertEqual(df["Company Name"].iloc[0], "Apple Inc.")
        self.assertGreaterEqual(len(df), 3)

    def test_data_quality(self):
        """Test data quality checks."""
        df = pd.DataFrame({
            "Company Name": ["Apple Inc.", "Microsoft Corp."],
            "Form Type": ["10-K", "10-Q"],
            "CIK": ["0000320193", "0000789019"],
            "Date Filed": ["2024-03-15", "2024-05-14"],
            "Filename": ["file1.txt", "file2.txt"],
        })

        # CIK should be 10 digits
        self.assertTrue(df["CIK"].str.len().eq(10).all())

        # Should have no null values in key columns
        self.assertTrue(df["Company Name"].notna().all())
        self.assertTrue(df["CIK"].notna().all())

        # Get statistics
        stats = DataProcessor.get_statistics(df)
        self.assertEqual(stats["total_records"], 2)


def run_tests():
    """Run all unit tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestSECIndexParser))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys
    sys.exit(run_tests())
