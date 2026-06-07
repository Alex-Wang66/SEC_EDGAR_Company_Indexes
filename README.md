# SEC EDGAR Company Filing Indexes

<div align="center">

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data Source: SEC EDGAR](https://img.shields.io/badge/Data-SEC%20EDGAR-green)](https://www.sec.gov/cgi-bin/browse-edgar)

A comprehensive data engineering solution for fetching, parsing, and processing SEC EDGAR company filing index data.

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Architecture](#architecture)

</div>

---

## Overview

This project provides a **production-ready data pipeline** for collecting and processing SEC EDGAR company filing indexes from the [SEC's official database](https://www.sec.gov/Archives/edgar/full-index/).

**What it does:**
- 📥 Automatically downloads quarterly company filing indexes from SEC
- 🔍 Parses structured data from SEC index files (tab-separated format)
- 🧹 Cleans, deduplicates, and processes the data
- 💾 Exports to multiple formats (Parquet, CSV, JSON)
- 📊 Generates comprehensive statistics and metadata

**Key Characteristics:**
- **Real Data**: Uses authentic SEC EDGAR data
- **Scalable**: Handles 10,000+ company records
- **Modular**: Clean separation of download, parse, and process logic
- **Configurable**: YAML/environment-based configuration
- **Resumable**: Can skip download and process existing files
- **Well-Documented**: Comprehensive code and usage documentation

---

## Features

### ✨ Core Capabilities

| Feature | Description |
|---------|-------------|
| **Automated Download** | Fetches company.idx files from SEC servers with rate limiting |
| **Format Parsing** | Handles variable-width SEC index file format |
| **Data Cleaning** | Removes duplicates, handles missing values, normalizes whitespace |
| **Deduplication** | Keeps latest filing per company based on filing date |
| **Multi-Format Export** | Saves as Parquet (efficient), CSV (universal), or JSON |
| **Logging & Monitoring** | Structured logging for pipeline transparency |
| **CLI Interface** | Command-line tools for batch processing |

### 📈 Data Processing Pipeline

```
SEC EDGAR Website
       ↓
   Download (company.idx files per quarter)
       ↓
   Parse (structured extraction from index format)
       ↓
   Clean (whitespace, empty rows, date conversion)
       ↓
   Deduplicate (latest filing per company)
       ↓
   Export (Parquet/CSV/JSON)
```

---

## Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Alex-Wang66/SEC_EDGAR_Company_Indexes.git
   cd SEC_EDGAR_Company_Indexes
   ```

2. **Create a Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

#### Via Command Line

```bash
# Download 2023-2024 data and save as Parquet
python run_pipeline.py --start-year 2023 --end-year 2024

# Process existing files only (skip download)
python run_pipeline.py --skip-download --format csv

# Download with verbose logging
python run_pipeline.py --start-year 2023 --verbose
```

#### Via Python Code

```python
from src.sec_edgar.main import SECEDGARPipeline

# Create and run pipeline
pipeline = SECEDGARPipeline()
results = pipeline.run(
    start_year=2023,
    end_year=2024,
    download=True,
    output_format="parquet"
)

print(f"Output: {results['output_file']}")
print(f"Records: {results['stages']['process']['records']:,}")
```

### Output Example

```
SEC EDGAR Data Pipeline Started
============================================================

[Stage 1/3] Downloading SEC EDGAR index files...
✓ Downloaded 8 files

[Stage 2/3] Parsing company index files...
✓ Parsed 47,233 records

[Stage 3/3] Processing and cleaning data...
✓ Processed 12,456 final records

Saving results as PARQUET...
✓ Saved to: data/processed/company_files_20240607_154523.parquet

============================================================
SEC EDGAR Data Pipeline Completed Successfully

Pipeline Summary:
  Output: data/processed/company_files_20240607_154523.parquet
  Total records: 12,456
  Unique companies: 5,234
  Form types: 42
```

---

## Architecture

### Project Structure

```
SEC_EDGAR_Company_Indexes/
├── src/sec_edgar/              # Main package
│   ├── __init__.py             # Package initialization
│   ├── config.py               # Configuration management
│   ├── downloader.py           # SEC EDGAR downloader (SECDownloader class)
│   ├── parser.py               # Index file parser (SECIndexParser class)
│   ├── processor.py            # Data processor (DataProcessor class)
│   └── main.py                 # Pipeline orchestrator (SECEDGARPipeline class)
├── data/
│   ├── raw/                    # Downloaded .idx files
│   └── processed/              # Output files (Parquet/CSV/JSON)
├── logs/                       # Pipeline logs
├── tests/                      # Unit tests
├── run_pipeline.py             # CLI entry point
├── setup.py                    # Package setup
├── requirements.txt            # Dependencies
├── README.md                   # This file
├── USAGE.md                    # Detailed usage guide
├── DATA_FORMAT.md              # Data format specification
├── CHANGELOG.md                # Version history
└── LICENSE                     # MIT License
```

### Core Components

#### 1. **SECDownloader** (`downloader.py`)
Downloads quarterly company.idx files from SEC
- Respects SEC's rate limiting guidelines (0.2s between requests)
- Handles network errors gracefully
- Returns download statistics

#### 2. **SECIndexParser** (`parser.py`)
Parses SEC's fixed-width index file format
- Skips header rows (first 10 lines)
- Extracts: Company Name, Form Type, CIK, Date, Filename
- Handles variable-length company names

#### 3. **DataProcessor** (`processor.py`)
Cleans and transforms raw data
- Removes duplicates by keeping latest filing date
- Normalizes whitespace
- Converts date strings to datetime objects
- Generates statistics

#### 4. **SECEDGARPipeline** (`main.py`)
Orchestrates the complete workflow
- Manages logging and error handling
- Saves results in multiple formats
- Provides progress reporting

---

## Usage Guide

### Command Line Options

```
usage: run_pipeline.py [-h] [--start-year START_YEAR] 
                       [--end-year END_YEAR] [--skip-download]
                       [--format {parquet,csv,json}] [--verbose]

options:
  --start-year START_YEAR    Starting year (default: 2023)
  --end-year END_YEAR        Ending year (default: current year)
  --skip-download            Skip download, process existing files
  --format {parquet,csv,json}  Output format (default: parquet)
  --verbose                  Enable debug logging
```

### Configuration

Edit `src/sec_edgar/config.py` to customize:
- SEC EDGAR base URL
- Default year range
- Request delay and timeout
- Output directory paths
- Logging settings

See [USAGE.md](USAGE.md) for detailed examples.

---

## Data Format

The output files contain the following fields:

| Column | Type | Description |
|--------|------|-------------|
| Company Name | str | Official company name as filed with SEC |
| Form Type | str | SEC form type (e.g., 10-K, 10-Q, 8-K) |
| CIK | str | Central Index Key - unique company identifier |
| Date Filed | datetime | Filing submission date |
| Filename | str | Path to filing document on SEC servers |

**Example Record:**
```json
{
  "Company Name": "Apple Inc.",
  "Form Type": "10-Q",
  "CIK": "0000320193",
  "Date Filed": "2024-05-03",
  "Filename": "edgar/data/320193/0000320193-24-000066.txt"
}
```

See [DATA_FORMAT.md](DATA_FORMAT.md) for complete specification.

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| **Download Speed** | ~2 files/min (respects SEC rate limits) |
| **Parse Speed** | ~10,000 records/sec |
| **Memory Usage** | ~500MB for 50,000 records |
| **File Sizes** | Parquet (~15MB), CSV (~60MB) for 50,000 records |

---

## Development

### Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

### Code Quality

```bash
# Type checking
mypy src/

# Linting
flake8 src/ --max-line-length=100

# Code formatting
black src/
```

### Building Package

```bash
# Build distribution
python setup.py sdist bdist_wheel

# Install locally in development mode
pip install -e .
```

---

## API Reference

For detailed API documentation, see individual module docstrings:

```python
from src.sec_edgar.downloader import SECDownloader
from src.sec_edgar.parser import SECIndexParser
from src.sec_edgar.processor import DataProcessor
```

Comprehensive API docs available in [USAGE.md](USAGE.md#api-reference).

---

## Legal & Data Source

- **Data Source**: [SEC EDGAR Database](https://www.sec.gov/cgi-bin/browse-edgar)
- **User Agreement**: This tool complies with SEC's robots.txt and rate limiting guidelines
- **Rate Limiting**: Default 0.2 second delay between requests
- **User-Agent**: Clearly identifies this educational tool

The SEC EDGAR database is public and free to use. Filings are official SEC documents.

---

## Troubleshooting

### Common Issues

**Issue**: Network timeout errors
- **Solution**: Increase timeout in config.py or check SEC service status

**Issue**: File already exists
- **Solution**: Output files are timestamped; previous files are preserved

**Issue**: Memory error with large datasets
- **Solution**: Process year-by-year; use CSV instead of loading all in memory

See [USAGE.md](USAGE.md#troubleshooting) for more solutions.

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## Citation

If you use this data in research or publication, please cite the SEC EDGAR source:

```bibtex
@dataset{sec_edgar_2024,
  title={SEC EDGAR Company Indexes},
  author={U.S. Securities and Exchange Commission},
  year={2024},
  url={https://www.sec.gov/Archives/edgar/full-index/}
}
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

## Contact

**Author**: Alex Wang  
**Email**: wangjle9@mail2.sysu.edu.cn  
**GitHub**: [@Alex-Wang66](https://github.com/Alex-Wang66)

---

<div align="center">

Made with ❤️ for financial data enthusiasts

⭐ If you found this useful, please consider starring this repository!

</div>
