#!/usr/bin/env python3
"""
PapersWithCode Data Downloader

Downloads datasets from the PapersWithCode repository and maintains a log of download history.
"""

import os
import sys
import json
import gzip
import hashlib
import argparse
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from tqdm import tqdm


class PapersWithCodeDownloader:
    """Handles downloading and managing PapersWithCode datasets."""
    
    DATASETS = {
        "papers": {
            "url": "https://production-media.paperswithcode.com/about/papers-with-abstracts.json.gz",
            "filename": "papers-with-abstracts.json.gz",
            "description": "All papers with abstracts"
        },
        "links": {
            "url": "https://production-media.paperswithcode.com/about/links-between-papers-and-code.json.gz",
            "filename": "links-between-papers-and-code.json.gz",
            "description": "Links between papers and code"
        },
        "evaluations": {
            "url": "https://production-media.paperswithcode.com/about/evaluation-tables.json.gz",
            "filename": "evaluation-tables.json.gz",
            "description": "Evaluation tables"
        },
        "methods": {
            "url": "https://production-media.paperswithcode.com/about/methods.json.gz",
            "filename": "methods.json.gz",
            "description": "Methods"
        },
        "datasets": {
            "url": "https://production-media.paperswithcode.com/about/datasets.json.gz",
            "filename": "datasets.json.gz",
            "description": "Datasets"
        }
    }
    
    def __init__(self, download_dir: str = "../ya-paperswithcode-database", 
                 log_file: str = "download_log.json"):
        """
        Initialize the downloader.
        
        Args:
            download_dir: Directory to save downloaded files
            log_file: Path to the download log file
        """
        self.download_dir = Path(download_dir)
        self.log_file = Path(log_file)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.log_data = self._load_log()
        
    def _load_log(self) -> Dict:
        """Load existing log data or create new."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {self.log_file}, creating new log")
        
        return {
            "downloads": [],
            "github_info": {
                "repository": "https://github.com/paperswithcode/paperswithcode-data",
                "last_checked": None,
                "branch": "master"
            }
        }
    
    def _save_log(self):
        """Save log data to file."""
        with open(self.log_file, 'w') as f:
            json.dump(self.log_data, f, indent=2, default=str)
    
    def _get_file_hash(self, filepath: Path, algorithm: str = 'sha256') -> str:
        """Calculate file hash."""
        hash_func = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    def _get_github_info(self) -> Dict:
        """Get latest GitHub repository information."""
        try:
            response = requests.get(
                "https://api.github.com/repos/paperswithcode/paperswithcode-data",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "last_commit": data.get("pushed_at"),
                    "default_branch": data.get("default_branch", "master"),
                    "description": data.get("description"),
                    "updated_at": data.get("updated_at")
                }
        except Exception as e:
            print(f"Warning: Could not fetch GitHub info: {e}")
        return {}
    
    def download_file(self, url: str, filepath: Path, 
                     chunk_size: int = 8192) -> Tuple[bool, Optional[str]]:
        """
        Download a file with progress bar and resume capability.
        
        Args:
            url: URL to download from
            filepath: Path to save the file
            chunk_size: Size of chunks to download
            
        Returns:
            Tuple of (success, error_message)
        """
        headers = {}
        mode = 'wb'
        resume_pos = 0
        
        # Check if file exists for resume
        if filepath.exists():
            resume_pos = filepath.stat().st_size
            headers['Range'] = f'bytes={resume_pos}-'
            mode = 'ab'
        
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            
            # Check if server supports resume
            if resume_pos > 0 and response.status_code == 416:
                print(f"File {filepath.name} already fully downloaded")
                return True, None
            
            response.raise_for_status()
            
            # Get total file size
            total_size = int(response.headers.get('content-length', 0))
            if response.status_code == 206:  # Partial content
                total_size += resume_pos
            
            # Download with progress bar
            with open(filepath, mode) as f:
                with tqdm(total=total_size, initial=resume_pos, 
                         unit='B', unit_scale=True, desc=filepath.name) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            return True, None
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Download failed: {str(e)}"
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            return False, error_msg
    
    def decompress_file(self, gz_filepath: Path) -> Tuple[bool, Optional[str]]:
        """
        Decompress a gzipped file.
        
        Args:
            gz_filepath: Path to the gzipped file
            
        Returns:
            Tuple of (success, error_message)
        """
        output_filepath = gz_filepath.with_suffix('')
        
        try:
            print(f"Decompressing {gz_filepath.name}...")
            with gzip.open(gz_filepath, 'rb') as f_in:
                with open(output_filepath, 'wb') as f_out:
                    f_out.write(f_in.read())
            print(f"Decompressed to {output_filepath.name}")
            return True, None
        except Exception as e:
            error_msg = f"Decompression failed: {str(e)}"
            return False, error_msg
    
    def download_dataset(self, dataset_key: str, decompress: bool = True) -> bool:
        """
        Download a specific dataset.
        
        Args:
            dataset_key: Key of the dataset to download
            decompress: Whether to decompress after download
            
        Returns:
            Success status
        """
        if dataset_key not in self.DATASETS:
            print(f"Unknown dataset: {dataset_key}")
            return False
        
        dataset_info = self.DATASETS[dataset_key]
        url = dataset_info["url"]
        filename = dataset_info["filename"]
        filepath = self.download_dir / filename
        
        print(f"\nDownloading {dataset_info['description']}...")
        start_time = datetime.now()
        
        # Create log entry
        log_entry = {
            "dataset": dataset_key,
            "url": url,
            "filename": filename,
            "start_time": start_time.isoformat(),
            "status": "started",
            "file_size": None,
            "checksum": None,
            "error": None
        }
        
        # Download the file
        success, error = self.download_file(url, filepath)
        
        if success:
            # Calculate file info
            file_stats = filepath.stat()
            log_entry["file_size"] = file_stats.st_size
            log_entry["checksum"] = self._get_file_hash(filepath)
            log_entry["status"] = "downloaded"
            
            # Decompress if requested
            if decompress and filename.endswith('.gz'):
                decomp_success, decomp_error = self.decompress_file(filepath)
                if not decomp_success:
                    log_entry["status"] = "decompression_failed"
                    log_entry["error"] = decomp_error
                else:
                    log_entry["status"] = "completed"
        else:
            log_entry["status"] = "failed"
            log_entry["error"] = error
        
        # Record completion time
        end_time = datetime.now()
        log_entry["end_time"] = end_time.isoformat()
        log_entry["duration_seconds"] = (end_time - start_time).total_seconds()
        
        # Update log
        self.log_data["downloads"].append(log_entry)
        self._save_log()
        
        return success
    
    def download_all(self, decompress: bool = True):
        """Download all available datasets."""
        # Update GitHub info
        github_info = self._get_github_info()
        if github_info:
            self.log_data["github_info"].update(github_info)
            self.log_data["github_info"]["last_checked"] = datetime.now().isoformat()
            self._save_log()
        
        success_count = 0
        for dataset_key in self.DATASETS:
            if self.download_dataset(dataset_key, decompress):
                success_count += 1
        
        print(f"\nDownloaded {success_count}/{len(self.DATASETS)} datasets successfully")
        
    def list_datasets(self):
        """List all available datasets."""
        print("\nAvailable datasets:")
        for key, info in self.DATASETS.items():
            print(f"  {key}: {info['description']}")
    
    def show_download_history(self):
        """Display download history from log."""
        if not self.log_data["downloads"]:
            print("No download history found")
            return
        
        print("\nDownload History:")
        print("-" * 80)
        
        for entry in self.log_data["downloads"][-10:]:  # Show last 10
            print(f"Dataset: {entry['dataset']}")
            print(f"  Time: {entry['start_time']}")
            print(f"  Status: {entry['status']}")
            if entry.get('file_size'):
                size_mb = entry['file_size'] / (1024 * 1024)
                print(f"  Size: {size_mb:.2f} MB")
            if entry.get('duration_seconds'):
                print(f"  Duration: {entry['duration_seconds']:.2f} seconds")
            if entry.get('error'):
                print(f"  Error: {entry['error']}")
            print("-" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Download PapersWithCode datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--download-dir', 
        default='../ya-paperswithcode-database',
        help='Directory to save downloaded files (default: ../ya-paperswithcode-database)'
    )
    
    parser.add_argument(
        '--dataset',
        choices=list(PapersWithCodeDownloader.DATASETS.keys()) + ['all'],
        default='all',
        help='Dataset to download (default: all)'
    )
    
    parser.add_argument(
        '--no-decompress',
        action='store_true',
        help='Skip decompression of downloaded files'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available datasets'
    )
    
    parser.add_argument(
        '--history',
        action='store_true',
        help='Show download history'
    )
    
    args = parser.parse_args()
    
    downloader = PapersWithCodeDownloader(download_dir=args.download_dir)
    
    if args.list:
        downloader.list_datasets()
    elif args.history:
        downloader.show_download_history()
    elif args.dataset == 'all':
        downloader.download_all(decompress=not args.no_decompress)
    else:
        downloader.download_dataset(args.dataset, decompress=not args.no_decompress)


if __name__ == "__main__":
    main()