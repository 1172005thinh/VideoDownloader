# PROMPT

This file contains instructions and guidelines for building our Python script. Do not modify this file unless you have my permission.

## PROGRAM OVERVIEW

Name: `downloader.py`
Version: `1.0.0`
Author: `1172005thinh (QuickComp.)`
Description: A robust python script using `yt-dlp`, `ffmpeg` to download, merge and convert media files from various streaming platforms, especially Youtube.
License: `MIT License`
Repository: `https`

## USAGE

To run with default settings:

```bash
python downloader.py
```

This will download videos from default input sources `/urls.txt` with default format `bestvideo+bestaudio`, saving to `/output` directory with extension `.mp4`.

To customize settings, use command-line arguments:

```bash
python downloader.py --input /path/to/urls.txt --output /path/to/output --format ba+bv --ext mp4 --retry 5 --delay 2
```

Available arguments:

- `--input` or `-i`: Path to input text file with URLs (default: `/urls.txt`)
  - Accepts local file TXT only. If the file does not exist, returns an error.
- `--output` or `-o`: Path to output directory (default: `/output`)
  - Accepts local directory only. If the directory does not exist, asks if user wants to create it, yes then creates it.
- `--format` or `-f`: Video format code (default: `ba+bv`)
  - Accepts format: `ba` or `bestaudio` for best audio only, `bv` or `bestvideo` for best video only, `ba+bv` or `bestaudio+bestvideo` for best audio and best video merged. Do not accept other format codes, if other format codes provided, returns an error.
- `--ext` or `-e`: Output file extension (default: `mp4`)
  - Accepts extensions: `mp4`, `mkv`, `webm` for format `ba+bv`, `bv` only; `mp3`, `m4a`, `aac`, `opus`, `wav`, `flac` for format `ba` only. If incompatible extension provided for the selected format, returns an error.
- `--retry` or `-r`: Number of retry attempts on failure (default: `3`)
  - Accepts integer >= 0. If invalid value provided, returns an error.
- `--delay` or `-d`: Delay in seconds between downloads (default: `1`)
  - Accepts integer >= 0. If invalid value provided, returns an error.
- `--help` or `-h`: Show help message and exit
- `--version` or `-v`: Show program version and exit
- `--license` or `-l`: Show license information and exit
- `--repo` or `-R`: Show repository URL and exit
- `--example` or `-x`: Show usage and command examples and exit
- `--test` or `-t`: Run test download to verify setup and dependencies
  - Accepted: `url` to test valid urls listed in the input file, `dep` to test if `yt-dlp`, `ffmpeg` are installed and accessible, `all` to run both tests. If any test fails, returns an error.
- `--dry-run` or `-r`: Perform a dry run without actual downloading
  - Simulates the download process, showing what would be downloaded without saving any files.
