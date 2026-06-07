# Usage Guide - SEC EDGAR Company Indexes

## Table of Contents

1. [Installation](#installation)
2. [Command Line Usage](#command-line-usage)
3. [Python API](#python-api)
4. [Configuration](#configuration)
5. [Examples](#examples)
6. [Troubleshooting](#troubleshooting)

---

## Installation

### Requirements

- Python 3.8 or higher
- pip (Python package manager)
- 500MB+ disk space for data

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/Alex-Wang66/SEC_EDGAR_Company_Indexes.git
cd SEC_EDGAR_Company_Indexes

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. (Optional) Install in development mode
pip install -e .
```

---

## Command Line Usage

### Basic Command

```bash
python run_pipeline.py [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--start-year` | int | 2023 | Starting year for data collection |
| `--end-year` | int | current year | Ending year for data collection |
| `--skip-download` | flag | False | Skip download, process existing files |
| `--format` | str | parquet | Output format: parquet, csv, or json |
| `--verbose` | flag | False | Enable detailed logging |
| `-h, --help` | flag | | Show help message |

### Examples

#### Example 1: Download Latest Data
```bash
python run_pipeline.py --start-year 2024
```
Downloads 2024 data to current date and saves as Parquet.

#### Example 2: Download Range with CSV Output
```bash
python run_pipeline.py --start-year 2023 --end-year 2024 --format csv
```
Downloads 2023-2024 data and exports as CSV format.

#### Example 3: Process Existing Files
```bash
python run_pipeline.py --skip-download --format json
```
Parses existing idx files without downloading, exports as JSON.

#### Example 4: Debug Mode
```bash
python run_pipeline.py --start-year 2024 --verbose
```
Shows detailed debug information during execution.

---

## Python API

### Quick Start

```python
from src.sec_edgar.main import SECEDGARPipeline

# Create pipeline
pipeline = SECEDGARPipeline()

# Run complete workflow
results = pipeline.run(
    start_year=2023,
    end_year=2024,
    download=True,
    output_format="parquet"
)

# Check results
print(f"Status: {results['status']}")
print(f"Output: {results['output_file']}")
```

### Module-Level Functions

#### `run_pipeline()`

Convenience function to run complete pipeline.

```python
from src.sec_edgar.main import run_pipeline

results = run_pipeline(
    start_year=2023,
    end_year=2024,
    download=True,
    output_format="parquet"
)
```

---

### Downloader API

#### `SECDownloader` Class

```python
from src.sec_edgar.downloader import SECDownloader
from pathlib import Path

# Create downloader
downloader = SECDownloader(
    output_dir=Path("data/raw")
)

# Download specific quarter
downloader.download_file(year=2024, quarter=0)  # 2024 Q1

# Download range
stats = downloader.download_range(
    start_year=2023,
    end_year=2024
)

print(f"Downloaded: {stats['successful']}/{stats['total_files']}")
```

**Parameters:**
- `base_url` (str): SEC EDGAR base URL
- `request_delay` (float): Delay between requests (seconds)
- `output_dir` (Path): Directory for downloaded files

**Methods:**
- `download_file(year, quarter)` → bool
- `download_range(start_year, end_year)` → dict

---

### Parser API

#### `SECIndexParser` Class

```python
from src.sec_edgar.parser import SECIndexParser
from pathlib import Path

# Parse single file
df = SECIndexParser.parse_file(
    Path("data/raw/2024/company_2024_QTR1.idx")
)

# Parse all files in directory
df = SECIndexParser.parse_directory(
    Path("data/raw/2024")
)

print(f"Parsed {len(df)} records")
print(df.head())
```

**Methods:**
- `parse_line(line)` → dict | None
- `parse_file(file_path)` → pd.DataFrame
- `parse_directory(directory)` → pd.DataFrame

---

### Processor API

#### `DataProcessor` Class

```python
from src.sec_edgar.processor import DataProcessor
import pandas as pd

# Load data
df = pd.read_parquet("data/processed/company_files.parquet")

# Clean whitespace
df = DataProcessor.clean_whitespace(df)

# Remove empty rows
df = DataProcessor.remove_empty_rows(df)

# Deduplicate by latest data
df = DataProcessor.deduplicate_by_latest_data(df)

# Get statistics
stats = DataProcessor.get_statistics(df)
print(stats)
```

**Methods:**
- `convert_date_column(df, date_column, errors)` → pd.DataFrame
- `deduplicate(df, subset, keep, sort_by, ascending)` → pd.DataFrame
- `clean_whitespace(df)` → pd.DataFrame
- `remove_empty_rows(df)` → pd.DataFrame
- `get_statistics(df)` → dict

---

## Configuration

### Config File Location

`src/sec_edgar/config.py`

### Key Settings

```python
SEC_CONFIG = {
    "base_url": "https://www.sec.gov/Archives/edgar/full-index",
    "start_year": 2023,
    "request_delay": 0.2,  # seconds between requests
    "timeout": 30,  # request timeout
    "headers": {
        "User-Agent": "...",  # Customize if needed
    }
}

PROCESSING_CONFIG = {
    "output_format": "parquet",  # parquet, csv, or json
    "deduplicate_on": ["Company Name"],
    "date_column": "Date Filed",
}
```

### Custom Configuration

Edit `src/sec_edgar/config.py`:

```python
# Example: Change request delay for faster downloads (use cautiously)
SEC_CONFIG["request_delay"] = 0.5

# Example: Change default output directory
from pathlib import Path
DATA_PROCESSED_DIR = Path("my_custom_output")
```

### Environment Variables

Create `.env` file:

```
SEC_BASE_URL=https://www.sec.gov/Archives/edgar/full-index
SEC_REQUEST_DELAY=0.2
SEC_TIMEOUT=30
DATA_RAW_DIR=data/raw
DATA_PROCESSED_DIR=data/processed
```

Load with:

```python
from dotenv import load_dotenv
import os

load_dotenv()
base_url = os.getenv("SEC_BASE_URL")
```

---

## Examples

### Example 1: Complete Pipeline Workflow

```python
from src.sec_edgar.main import SECEDGARPipeline
from pathlib import Path

# Initialize pipeline
pipeline = SECEDGARPipeline(
    raw_data_dir=Path("data/raw"),
    processed_data_dir=Path("data/processed")
)

# Run with all stages
results = pipeline.run(
    start_year=2023,
    end_year=2024,
    download=True,
    output_format="parquet"
)

# Display results
if results["status"] == "success":
    stats = results["stages"]["process"]["statistics"]
    print(f"Total Companies: {stats['total_companies']:,}")
    print(f"Total Records: {stats['total_records']:,}")
    print(f"Date Range: {stats['date_range']}")
```

### Example 2: Download Only

```python
from src.sec_edgar.downloader import SECDownloader

downloader = SECDownloader()
stats = downloader.download_range(start_year=2023, end_year=2024)

for download in stats['successful_downloads']:
    print(f"✓ {download['year']} {download['quarter']}: {download['file']}")
```

### Example 3: Parse Existing Files

```python
from src.sec_edgar.parser import SECIndexParser
from pathlib import Path

# Parse all idx files in directory
df = SECIndexParser.parse_directory(Path("data/raw"))

# Show summary
print(f"Total records: {len(df)}")
print(f"Form types: {df['Form Type'].value_counts()}")
print(f"Date range: {df['Date Filed'].min()} to {df['Date Filed'].max()}")
```

### Example 4: Data Processing & Analysis

```python
from src.sec_edgar.processor import DataProcessor
import pandas as pd

# Load raw data
df = pd.read_parquet("data/processed/company_files.parquet")

# Process
df_clean = DataProcessor.clean_whitespace(df)
df_dedup = DataProcessor.deduplicate_by_latest_data(df_clean)

# Analyze
stats = DataProcessor.get_statistics(df_dedup)
print(f"Companies with filings: {stats['total_companies']}")

# Export
df_dedup.to_csv("output.csv", index=False)
```

### Example 5: Integration with Pandas

```python
import pandas as pd
from src.sec_edgar.main import SECEDGARPipeline

# Run pipeline
pipeline = SECEDGARPipeline()
results = pipeline.run(start_year=2024, download=False)

# Load and analyze results
df = pd.read_parquet(results['output_file'])

# Filter by form type
ten_ks = df[df['Form Type'] == '10-K']

# Group analysis
by_company = df.groupby('Company Name').size().sort_values(ascending=False)
print(f"Most active companies:\n{by_company.head()}")

# Date analysis
df['Date Filed'] = pd.to_datetime(df['Date Filed'])
by_month = df.set_index('Date Filed').resample('M').size()
print(f"Filings per month:\n{by_month}")
```

---

## Troubleshooting

### Issue: Connection Timeout

**Error Message:**
```
requests.exceptions.ConnectTimeout: HTTPConnectionPool(...) Read timed out
```

**Solutions:**
1. Increase timeout in config:
   ```python
   SEC_CONFIG["timeout"] = 60  # Increase from 30
   ```

2. Check SEC service status at https://www.sec.gov/

3. Try again later (SEC servers have scheduled maintenance)

### Issue: "No .idx files found"

**Error Message:**
```
WARNING - No .idx files found in data/raw
```

**Solutions:**
1. Run download first:
   ```bash
   python run_pipeline.py --start-year 2024
   ```

2. Check directory exists:
   ```bash
   ls -la data/raw/
   ```

### Issue: Memory Error

**Error Message:**
```
MemoryError: Unable to allocate ... MiB for an array
```

**Solutions:**
1. Process smaller year ranges:
   ```bash
   python run_pipeline.py --start-year 2024 --end-year 2024
   ```

2. Use CSV instead of loading all in memory:
   ```python
   df = pd.read_csv("file.csv", chunksize=10000)
   ```

3. Filter data:
   ```python
   df = df[df['Form Type'] == '10-K']  # Only annual reports
   ```

### Issue: "Permission Denied" Writing Files

**Solutions:**
1. Check directory permissions:
   ```bash
   chmod 755 data/processed/
   ```

2. Change output directory:
   ```python
   from pathlib import Path
   pipeline = SECEDGARPipeline(processed_data_dir=Path("/tmp/output"))
   ```

### Issue: Duplicate Records After Processing

**Troubleshooting:**
1. Check deduplication logic:
   ```python
   stats_before = len(df)
   df_dedup = DataProcessor.deduplicate_by_latest_data(df)
   print(f"Removed: {stats_before - len(df_dedup)}")
   ```

2. Verify date column format:
   ```python
   print(df['Date Filed'].dtype)
   print(df['Date Filed'].head())
   ```

### Getting Help

1. Check [README.md](README.md) for overview
2. Review log files in `logs/` directory
3. Run with `--verbose` flag for debug information
4. Open issue on GitHub with error details

---

## Performance Tips

### Optimization 1: Faster Processing

```python
# Use Parquet instead of CSV (faster I/O)
pipeline.run(output_format="parquet")  # ~100x faster than CSV

# Disable logging for batch runs
import logging
logging.getLogger("sec_edgar").setLevel(logging.WARNING)
```

### Optimization 2: Parallel Processing

For multiple years, process in parallel:

```python
from concurrent.futures import ThreadPoolExecutor
from src.sec_edgar.downloader import SECDownloader

downloader = SECDownloader()

def download_year(year):
    return downloader.download_range(year, year)

with ThreadPoolExecutor(max_workers=4) as executor:
    years = range(2020, 2024)
    results = executor.map(download_year, years)
```

### Optimization 3: Caching

```python
import pandas as pd
from pathlib import Path

cache_file = Path("data/processed/cache.parquet")

if cache_file.exists():
    df = pd.read_parquet(cache_file)
else:
    # Run pipeline and save
    ...
    df.to_parquet(cache_file)
```

---

## Advanced Usage

### Custom Parsing Logic

```python
from src.sec_edgar.parser import SECIndexParser
import pandas as pd

class CustomParser(SECIndexParser):
    @staticmethod
    def parse_line(line):
        # Custom parsing logic
        parsed = SECIndexParser.parse_line(line)
        if parsed:
            # Add custom field
            parsed['custom_field'] = "value"
        return parsed
```

### Custom Processing Pipeline

```python
from src.sec_edgar.main import SECEDGARPipeline
from src.sec_edgar.processor import DataProcessor

class CustomPipeline(SECEDGARPipeline):
    def run(self, *args, **kwargs):
        # Add custom processing steps
        results = super().run(*args, **kwargs)
        
        # Custom post-processing
        df = pd.read_parquet(results['output_file'])
        df['custom_field'] = df['Company Name'].str.upper()
        
        return results
```

---

## Additional Resources

- [SEC EDGAR Official Site](https://www.sec.gov/cgi-bin/browse-edgar)
- [SEC Index File Format](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- [Python pandas Documentation](https://pandas.pydata.org/docs/)
- [requests Library Guide](https://docs.python-requests.org/)
