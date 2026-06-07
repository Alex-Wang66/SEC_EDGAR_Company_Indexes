# Data Format Specification - SEC EDGAR Company Indexes

## Overview

This document specifies the format of data processed and output by the SEC EDGAR Company Indexes pipeline.

---

## Input Format: SEC company.idx Files

### Source

- **URL**: `https://www.sec.gov/Archives/edgar/full-index/{YEAR}/{QUARTER}/company.idx`
- **Type**: Tab-separated text file
- **Encoding**: UTF-8
- **Update Frequency**: Quarterly

### File Structure

```
CIK|Company Name|IRS Number|State of Incorporation|SIC|Business Address|Mail Address|Former Name|Changed|Accession Number|...
[... header lines ...]
[... 10 header rows total ...]
Company A|10-K|0000000001|2024-03-15|edgar/data/1/000000000124000001.txt
Company B|10-Q|0000000002|2024-05-14|edgar/data/2/000000000124000002.txt
```

### Header

The first 10 lines contain metadata and header information:
- Lines 1-9: Company metadata fields description
- Line 10: Column headers

### Data Rows

Starting from line 11, each row contains:
- Variable-width fields separated by `|` (pipe character)
- No escaping; company names can contain spaces
- Variable number of fields (some trailing fields may be empty)

---

## Parsed Data Format

### DataFrame Schema

After parsing, data is stored as a pandas DataFrame with these columns:

| Column | Type | Example | Notes |
|--------|------|---------|-------|
| **Company Name** | str | Apple Inc. | Official registered company name |
| **Form Type** | str | 10-K | SEC form type designation |
| **CIK** | str | 0000320193 | Central Index Key (10-digit, zero-padded) |
| **Date Filed** | str | 2024-03-15 | Filing date (YYYY-MM-DD format) |
| **Filename** | str | edgar/data/320193/... | Relative path on SEC servers |

### Data Quality Notes

- **Company Name**: 
  - May contain special characters
  - May have alternative names or trade names
  - Length: 1-200 characters

- **Form Type**:
  - Common types: 10-K (annual), 10-Q (quarterly), 8-K (events), S-1 (IPO)
  - Full list: [SEC Form Types](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=&dateb=&owner=exclude&count=100)
  - Length: 1-10 characters

- **CIK**:
  - Always 10 digits (zero-padded on left)
  - Unique identifier for each entity
  - Never changes for a company

- **Date Filed**:
  - Format: YYYY-MM-DD
  - In chronological order within quarterly files
  - Some historical dates may be in different formats (converted to ISO)

- **Filename**:
  - Relative path: `edgar/data/{CIK}/{ACCESSION}/0{ACCESSION}.txt`
  - Can be used to construct full URL: `https://www.sec.gov/cgi-bin/viewer?action=view&cik={CIK}&accession_number={ACCESSION}`
  - All filings are publicly accessible

---

## Processed Output Formats

### Parquet Format (Default)

**File Extension**: `.parquet`

**Advantages**:
- Columnar storage (efficient for analytics)
- ~75% smaller than CSV
- Preserves data types (dates, numbers)
- Fast reading/writing
- Supports compression

**Column Types in Parquet**:
```python
Company Name    object (string)
Form Type       object (string)
CIK             object (string, maintains leading zeros)
Date Filed      datetime64[ns] (converted from string)
Filename        object (string)
```

**Reading in Python**:
```python
import pandas as pd
df = pd.read_parquet("company_files.parquet")
```

**Size Example**:
- 50,000 records → ~15-20 MB

---

### CSV Format

**File Extension**: `.csv`

**Format**: Comma-separated values (RFC 4180)

**Advantages**:
- Universal compatibility
- Human-readable
- Opens in Excel
- Simple to parse

**Disadvantages**:
- Larger file size (~4x Parquet)
- Date column stored as string
- No data type information
- Slower to read/write

**Sample Output**:
```csv
Company Name,Form Type,CIK,Date Filed,Filename
Apple Inc.,10-K,0000320193,2024-03-15,edgar/data/320193/0000320193-24-000015.txt
Apple Inc.,10-Q,0000320193,2024-05-03,edgar/data/320193/0000320193-24-000066.txt
Microsoft Corporation,10-K,0000789019,2024-04-22,edgar/data/789019/0000789019-24-000018.txt
```

**Size Example**:
- 50,000 records → ~60-75 MB

**Reading in Python**:
```python
import pandas as pd
df = pd.read_csv("company_files.csv")
```

---

### JSON Format

**File Extension**: `.json`

**Format**: JSON Lines (one JSON object per line) or standard JSON array

**Advantages**:
- Nested data support (if expanded)
- Metadata can be included
- Web-friendly format

**Sample Output**:
```json
[
  {
    "Company Name": "Apple Inc.",
    "Form Type": "10-K",
    "CIK": "0000320193",
    "Date Filed": "2024-03-15",
    "Filename": "edgar/data/320193/0000320193-24-000015.txt"
  },
  {
    "Company Name": "Apple Inc.",
    "Form Type": "10-Q",
    "CIK": "0000320193",
    "Date Filed": "2024-05-03",
    "Filename": "edgar/data/320193/0000320193-24-000066.txt"
  }
]
```

**Size Example**:
- 50,000 records → ~85-100 MB

**Reading in Python**:
```python
import pandas as pd
df = pd.read_json("company_files.json", orient="records")
```

---

## Field Descriptions

### Company Name

The official registered name of the company with the SEC.

**Examples**:
- Apple Inc.
- Microsoft Corporation
- Tesla Inc.
- NVIDIA Corporation

**Variations**:
- May include legal suffixes (Inc., Ltd., Corporation, etc.)
- May contain special characters (& - / .)
- Not always the same as ticker symbol name
- May have changed name (see "Former Name" in source)

### Form Type

Standard SEC form designation for the filing type.

**Common Form Types**:
- **10-K**: Annual report
- **10-Q**: Quarterly report
- **8-K**: Current report (significant events)
- **S-1**: Registration statement (IPO)
- **4**: Insider trading
- **13F**: Institutional investment manager holdings
- **SC 13D**: Beneficial ownership notification
- **DEF 14A**: Proxy statement

**Full List**: [SEC Form Types Reference](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)

### CIK (Central Index Key)

A unique 10-digit identifier assigned to each entity filing with the SEC.

**Format**: `0000320193` (always 10 digits, zero-padded)

**Characteristics**:
- Unique and permanent (never reused)
- Assigned upon first SEC filing
- Used to access all filings for a company
- Can look up company: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={CIK}`

**Example CIKs**:
- Apple: 0000320193
- Microsoft: 0000789019
- Tesla: 0001018724

### Date Filed

The date when the filing was submitted to the SEC.

**Format**: `YYYY-MM-DD` (ISO 8601)

**Characteristics**:
- Filing date, not the report period end date
- In chronological order within source files
- No time component in this dataset
- May have multiple filings on same date

### Filename

Relative path to access the filing on SEC servers.

**Format**: `edgar/data/{CIK}/{ACCESSION}/{FILENAME}`

**Example**: `edgar/data/320193/0000320193-24-000066.txt`

**To Access Filing**:
```
https://www.sec.gov/Archives/{filename}
https://www.sec.gov/cgi-bin/viewer?action=view&cik={CIK}&accession_number={ACCESSION}
```

---

## Data Statistics

### Record Counts

**Historical Range**:
- Q1 2023: ~11,000 records
- Q2 2023: ~11,500 records
- Q3 2023: ~12,000 records
- Q4 2023: ~12,500 records
- Q1 2024: ~13,000 records

**Deduplication Impact**:
- Before dedup: ~47,000 total quarterly records
- After keeping latest: ~12,000 unique companies
- Reduction: ~74% (companies file multiple times per quarter)

### Form Type Distribution

```
10-K          ~30%
10-Q          ~25%
8-K           ~20%
Other         ~25%
```

### Date Range

- **Earliest**: 2023-01-01
- **Latest**: Current quarter (see timestamp in filename)
- **Completeness**: Full coverage of all filings in SEC database for indexed quarters

---

## Data Validation

### Column Checks

```python
# Required fields
assert not df['Company Name'].isnull().any()
assert not df['Form Type'].isnull().any()
assert not df['CIK'].isnull().any()

# CIK format check
assert df['CIK'].str.len().eq(10).all()
assert df['CIK'].str.match(r'^\d{10}$').all()

# Date format check
assert pd.to_datetime(df['Date Filed']).notna().all()
```

### Expected Row Counts

```python
# Parquet/CSV row count
assert len(df) >= 10000  # Minimum expected

# Unique companies
assert df['Company Name'].nunique() >= 5000

# Form types
assert df['Form Type'].nunique() >= 40
```

---

## Common Use Cases

### 1. Find All Filings for a Company

```python
df_apple = df[df['Company Name'].str.contains('Apple', case=False)]
print(f"Apple filings: {len(df_apple)}")
```

### 2. Filter by Form Type

```python
annual_reports = df[df['Form Type'] == '10-K']
print(f"Annual reports: {len(annual_reports)}")
```

### 3. Time Series Analysis

```python
df['Date Filed'] = pd.to_datetime(df['Date Filed'])
filings_by_month = df.set_index('Date Filed').resample('M').size()
```

### 4. Company Statistics

```python
top_filers = df.groupby('Company Name').size().sort_values(ascending=False)
print(top_filers.head(10))
```

---

## Changelog

### Version 1.0.0
- Initial data format specification
- Support for Parquet, CSV, JSON outputs
- Data range: 2023 Q1 - Present

---

## References

- [SEC EDGAR Database](https://www.sec.gov/cgi-bin/browse-edgar)
- [SEC Form Types](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=&dateb=&owner=exclude&count=100)
- [Pandas Data Types](https://pandas.pydata.org/docs/user_guide/basics.html#dtypes)
- [Parquet Format](https://parquet.apache.org/)
