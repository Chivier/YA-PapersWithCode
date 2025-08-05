# PapersWithCode Data Downloader

This module downloads datasets from the [PapersWithCode Data Repository](https://github.com/paperswithcode/paperswithcode-data).

## Features

- Downloads all 5 main datasets from PapersWithCode
- Progress tracking with visual progress bars
- Resume capability for interrupted downloads
- Automatic decompression of gzipped files
- Download history logging with metadata
- GitHub repository version tracking

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Download all datasets
```bash
python download.py
```

### Download a specific dataset
```bash
python download.py --dataset papers
```

Available datasets:
- `papers` - All papers with abstracts
- `links` - Links between papers and code
- `evaluations` - Evaluation tables
- `methods` - Methods
- `datasets` - Datasets

### Other options
```bash
# List available datasets
python download.py --list

# Show download history
python download.py --history

# Download without decompressing
python download.py --no-decompress

# Specify custom download directory
python download.py --download-dir /path/to/directory
```

## Download Log

The script maintains a `download_log.json` file that tracks:
- Download timestamps
- File sizes and checksums
- GitHub repository information
- Download duration
- Success/failure status
- Error messages (if any)

## Data Structure

Downloaded files are saved to `../ya-paperswithcode-database/` by default:
```
ya-paperswithcode-database/
├── papers-with-abstracts.json
├── links-between-papers-and-code.json
├── evaluation-tables.json
├── methods.json
└── datasets.json
```

## License

The downloaded data is licensed under CC-BY-SA as specified by PapersWithCode.
