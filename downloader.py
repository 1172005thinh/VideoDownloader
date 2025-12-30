#!/usr/bin/env python3
"""
downloader.py - A robust media downloader using yt-dlp and ffmpeg

Version: 1.0.0
Author: 1172005thinh (QuickComp.)
License: MIT License
"""

import os
import sys
import argparse
import time
import subprocess
import shutil
from pathlib import Path
from typing import List, Tuple, Dict

# Program metadata
__version__ = "1.0.0"
__author__ = "1172005thinh (QuickComp.)"
__license__ = """MIT License

Copyright (c) 2025 1172005thinh (QuickComp.)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
__repository__ = "https"

# Format and extension mappings
AUDIO_FORMATS = ["ba", "bestaudio"]
VIDEO_FORMATS = ["bv", "bestvideo"]
COMBINED_FORMATS = ["ba+bv", "bestaudio+bestvideo"]
VIDEO_EXTENSIONS = ["mp4", "mkv", "webm"]
AUDIO_EXTENSIONS = ["mp3", "m4a", "aac", "opus", "wav", "flac"]

# Default values
DEFAULT_INPUT = "urls.txt"
DEFAULT_OUTPUT = "output"
DEFAULT_FORMAT = "ba+bv"
DEFAULT_EXT = "mp4"
DEFAULT_RETRY = 3
DEFAULT_DELAY = 1


def check_dependencies() -> Tuple[bool, str]:
    """Check if yt-dlp and ffmpeg are installed and accessible."""
    missing = []
    
    # Check yt-dlp
    if not shutil.which("yt-dlp"):
        missing.append("yt-dlp")
    
    # Check ffmpeg
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")
    
    if missing:
        return False, f"Missing dependencies: {', '.join(missing)}"
    return True, "All dependencies are installed"


def validate_format(format_code: str) -> Tuple[bool, str]:
    """Validate the format code."""
    valid_formats = AUDIO_FORMATS + VIDEO_FORMATS + COMBINED_FORMATS
    if format_code not in valid_formats:
        return False, f"Invalid format code: {format_code}. Valid formats: {', '.join(valid_formats)}"
    return True, ""


def validate_extension(ext: str, format_code: str) -> Tuple[bool, str]:
    """Validate extension compatibility with format."""
    # Determine format type
    is_audio_only = format_code in AUDIO_FORMATS
    is_video_only = format_code in VIDEO_FORMATS
    is_combined = format_code in COMBINED_FORMATS
    
    if is_audio_only:
        if ext not in AUDIO_EXTENSIONS:
            return False, f"Extension '{ext}' is incompatible with audio-only format. Valid extensions: {', '.join(AUDIO_EXTENSIONS)}"
    elif is_video_only or is_combined:
        if ext not in VIDEO_EXTENSIONS:
            return False, f"Extension '{ext}' is incompatible with video format. Valid extensions: {', '.join(VIDEO_EXTENSIONS)}"
    
    return True, ""


def validate_file_format(input_file: str) -> Tuple[bool, str]:
    """Validate that input file follows videoname:url format."""
    if not os.path.exists(input_file):
        return False, f"Input file '{input_file}' does not exist"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        
        if not lines:
            return False, "No entries found in input file"
        
        invalid_lines = []
        for i, line in enumerate(lines, 1):
            if ':' not in line:
                invalid_lines.append(f"Line {i}: Missing ':' separator")
            else:
                parts = line.split(':', 1)
                if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
                    invalid_lines.append(f"Line {i}: Invalid format")
        
        if invalid_lines:
            return False, f"Format errors found:\n  " + "\n  ".join(invalid_lines)
        
        return True, f"File format is valid ({len(lines)} entries)"
    except Exception as e:
        return False, f"Error reading file: {e}"


def validate_urls(entries: Dict[str, str]) -> Tuple[bool, str]:
    """Validate URLs using yt-dlp."""
    print(f"\nTesting {len(entries)} URL(s)...")
    invalid_entries = []
    
    for i, (video_name, url) in enumerate(entries.items(), 1):
        print(f"  [{i}/{len(entries)}] Testing '{video_name}': {url[:50]}...")
        try:
            result = subprocess.run(
                ["yt-dlp", "--simulate", "--no-warnings", url],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                invalid_entries.append(video_name)
                print(f"    [0] Invalid or inaccessible")
            else:
                print(f"    [1] Valid")
        except subprocess.TimeoutExpired:
            invalid_entries.append(video_name)
            print(f"    [0] Timeout")
        except Exception as e:
            invalid_entries.append(video_name)
            print(f"    [0] Error: {e}")
    
    if invalid_entries:
        return False, f"Found {len(invalid_entries)} invalid URL(s)"
    return True, "All URLs are valid"


def read_urls(input_file: str) -> Dict[str, str]:
    """Read video names and URLs from input file in format videoname:url."""
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    try:
        entries = {}
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                
                # Parse videoname:url format
                if ':' not in line:
                    print(f"Error: Line {line_num} missing ':' separator")
                    sys.exit(1)
                
                parts = line.split(':', 1)
                video_name = parts[0].strip()
                url = parts[1].strip()
                
                if not video_name or not url:
                    print(f"Error: Line {line_num} has empty video name or URL")
                    sys.exit(1)
                
                entries[video_name] = url
        
        return entries
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)


def ensure_output_directory(output_dir: str) -> bool:
    """Ensure output directory exists, ask user if it should be created."""
    if os.path.exists(output_dir):
        return True
    
    response = input(f"Output directory '{output_dir}' does not exist. Create it? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created directory: {output_dir}")
            return True
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False
    else:
        print("Operation cancelled.")
        return False


def download_media(video_name: str, url: str, output_dir: str, format_code: str, ext: str, retry: int, dry_run: bool) -> bool:
    """Download media from URL using yt-dlp with custom filename."""
    # Determine if audio-only format
    is_audio_only = format_code in ["ba", "bestaudio"]
    
    # Normalize format code
    if format_code in ["ba+bv", "bestaudio+bestvideo"]:
        ytdlp_format = "bestvideo+bestaudio/best"
    elif format_code in ["ba", "bestaudio"]:
        ytdlp_format = "bestaudio/best"
    elif format_code in ["bv", "bestvideo"]:
        ytdlp_format = "bestvideo/best"
    else:
        ytdlp_format = "best"
    
    # Build yt-dlp command with custom filename
    output_template = os.path.join(output_dir, f"{video_name}.%(ext)s")
    cmd = [
        "yt-dlp",
        "-f", ytdlp_format,
    ]
    
    # For audio-only, use extract-audio and audio-format
    if is_audio_only:
        cmd.extend([
            "--extract-audio",
            "--audio-format", ext,
        ])
    else:
        # For video formats, use merge-output-format
        cmd.extend([
            "--merge-output-format", ext,
        ])
    
    cmd.extend([
        "-o", output_template,
    ])
    
    if dry_run:
        cmd.append("--simulate")
    
    cmd.append(url)
    
    # Attempt download with retries
    for attempt in range(1, retry + 1):
        try:
            print(f"  Attempt {attempt}/{retry}...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  [1] Success")
                return True
            else:
                print(f"  [0] Failed: {result.stderr[:100]}")
                if attempt < retry:
                    print(f"  Retrying in 2 seconds...")
                    time.sleep(2)
        except Exception as e:
            print(f"  [0] Error: {e}")
            if attempt < retry:
                print(f"  Retrying in 2 seconds...")
                time.sleep(2)
    
    return False


def show_examples():
    """Show usage examples."""
    examples = """
Usage Examples:
==============

1. Basic usage (download from urls.txt to output/ folder):
   python downloader.py

2. Custom input and output paths:
   python downloader.py --input my_urls.txt --output downloads/

3. Download best audio only as MP3:
   python downloader.py --format ba --ext mp3

4. Download best video+audio as MKV with 5 retries:
   python downloader.py --format ba+bv --ext mkv --retry 5

5. Add 3 second delay between downloads:
   python downloader.py --delay 3

6. Test URLs before downloading:
   python downloader.py --test url

7. Check dependencies:
   python downloader.py --test dep

8. Dry run (simulate without downloading):
   python downloader.py --dry-run

9. Complete custom configuration:
   python downloader.py -i urls.txt -o videos/ -f ba+bv -e mp4 -r 5 -d 2

Format Options:
- ba, bestaudio: Best audio only
- bv, bestvideo: Best video only
- ba+bv, bestaudio+bestvideo: Best audio and video merged

Extension Options:
- Video formats: mp4, mkv, webm
- Audio formats: mp3, m4a, aac, opus, wav, flac
"""
    print(examples)


def create_argument_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="A robust media downloader using yt-dlp and ffmpeg",
        add_help=False
    )
    
    # Main arguments
    parser.add_argument('-i', '--input', type=str, default=DEFAULT_INPUT,
                        help=f'Path to input text file with URLs (default: {DEFAULT_INPUT})')
    parser.add_argument('-o', '--output', type=str, default=DEFAULT_OUTPUT,
                        help=f'Path to output directory (default: {DEFAULT_OUTPUT})')
    parser.add_argument('-f', '--format', type=str, default=DEFAULT_FORMAT,
                        help=f'Video format code (default: {DEFAULT_FORMAT})')
    parser.add_argument('-e', '--ext', type=str, default=DEFAULT_EXT,
                        help=f'Output file extension (default: {DEFAULT_EXT})')
    parser.add_argument('-r', '--retry', type=int, default=DEFAULT_RETRY,
                        help=f'Number of retry attempts (default: {DEFAULT_RETRY})')
    parser.add_argument('-d', '--delay', type=int, default=DEFAULT_DELAY,
                        help=f'Delay in seconds between downloads (default: {DEFAULT_DELAY})')
    
    # Information arguments
    parser.add_argument('-h', '--help', action='store_true',
                        help='Show help message and exit')
    parser.add_argument('-v', '--version', action='store_true',
                        help='Show program version and exit')
    parser.add_argument('-l', '--license', action='store_true',
                        help='Show license information and exit')
    parser.add_argument('-R', '--repo', action='store_true',
                        help='Show repository URL and exit')
    parser.add_argument('-x', '--example', action='store_true',
                        help='Show usage and command examples and exit')
    
    # Testing and dry-run
    parser.add_argument('-t', '--test', type=str, choices=['url', 'dep', 'all'],
                        help='Run tests (url: test URLs, dep: test dependencies, all: both)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Perform a dry run without actual downloading')
    
    return parser


def main():
    """Main program entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Handle information arguments
    if args.help:
        parser.print_help()
        sys.exit(0)
    
    if args.version:
        print(f"downloader.py version {__version__}")
        print(f"Author: {__author__}")
        sys.exit(0)
    
    if args.license:
        print(__license__)
        sys.exit(0)
    
    if args.repo:
        print(f"Repository: {__repository__}")
        sys.exit(0)
    
    if args.example:
        show_examples()
        sys.exit(0)
    
    # Handle test mode
    if args.test:
        print("=" * 60)
        print("Running Tests")
        print("=" * 60)
        
        if args.test in ['dep', 'all']:
            print("\n[1] Checking dependencies...")
            success, msg = check_dependencies()
            print(f"  {msg}")
            if not success:
                print("\nTest failed. Please install missing dependencies:")
                print("  - yt-dlp: pip install yt-dlp")
                print("  - ffmpeg: Download from https://ffmpeg.org/")
                sys.exit(1)
        
        if args.test in ['url', 'all']:
            print("\n[2] Validating file format...")
            success, msg = validate_file_format(args.input)
            print(f"  {msg}")
            if not success:
                sys.exit(1)
            
            print("\n[3] Validating URLs...")
            entries = read_urls(args.input)
            if not entries:
                print("  No entries found in input file")
                sys.exit(1)
            success, msg = validate_urls(entries)
            print(f"\n  Result: {msg}")
            if not success:
                sys.exit(1)
        
        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
        sys.exit(0)
    
    # Validate arguments
    if args.retry < 0:
        print(f"Error: Retry value must be >= 0")
        sys.exit(1)
    
    if args.delay < 0:
        print(f"Error: Delay value must be >= 0")
        sys.exit(1)
    
    # Validate format
    valid, msg = validate_format(args.format)
    if not valid:
        print(f"Error: {msg}")
        sys.exit(1)
    
    # Validate extension compatibility
    valid, msg = validate_extension(args.ext, args.format)
    if not valid:
        print(f"Error: {msg}")
        sys.exit(1)
    
    # Check dependencies
    dep_ok, dep_msg = check_dependencies()
    if not dep_ok:
        print(f"Error: {dep_msg}")
        print("Please install missing dependencies and try again.")
        sys.exit(1)
    
    # Read video entries
    entries = read_urls(args.input)
    if not entries:
        print(f"No entries found in {args.input}")
        sys.exit(0)
    
    # Ensure output directory exists
    if not args.dry_run:
        if not ensure_output_directory(args.output):
            sys.exit(1)
    
    # Start downloading
    print("=" * 60)
    if args.dry_run:
        print("DRY RUN MODE - No files will be downloaded")
    print(f"Starting download of {len(entries)} video(s)")
    print("=" * 60)
    print(f"Format: {args.format}")
    print(f"Extension: {args.ext}")
    print(f"Output: {args.output}")
    print(f"Retry attempts: {args.retry}")
    print(f"Delay: {args.delay}s")
    print("=" * 60)
    
    # Download each video
    success_count = 0
    failed_count = 0
    
    for i, (video_name, url) in enumerate(entries.items(), 1):
        print(f"\n[{i}/{len(entries)}] Processing '{video_name}': {url}")
        
        if download_media(video_name, url, args.output, args.format, args.ext, args.retry, args.dry_run):
            success_count += 1
        else:
            failed_count += 1
        
        # Add delay between downloads (except after last one)
        if i < len(entries) and args.delay > 0:
            print(f"  Waiting {args.delay} second(s)...")
            time.sleep(args.delay)
    
    # Summary
    print("\n" + "=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"Total: {len(entries)}")
    print(f"Success: {success_count}")
    print(f"Failed: {failed_count}")
    print("=" * 60)
    
    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
