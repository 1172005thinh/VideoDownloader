# Video Downloader

A robust Python script for downloading and converting media files from various streaming platforms using `yt-dlp` and `ffmpeg`.

## Features

- Download videos from YouTube and other platforms supported by yt-dlp
- Custom video naming via `videoname:url` format
- Multiple format options (audio-only, video-only, or combined)
- Flexible output extensions (mp4, mkv, webm, mp3, m4a, aac, opus, wav, flac)
- Automatic retry mechanism on download failures
- Configurable delay between downloads
- Input file format validation
- URL validation before downloading
- Dry-run mode for testing
- Dependency checking

## Requirements

### Dependencies

- **Python 3.6+**
- **yt-dlp** - A youtube-dl fork with additional features
- **ffmpeg** - Required for merging audio and video streams

### Installation

1. **Install Python packages:**

   ```bash
   pip install yt-dlp
   ```

2. **Install ffmpeg:**

   **Windows:**
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Extract and add to system PATH
   - Or use chocolatey: `choco install ffmpeg`

   **Linux:**

   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

   **macOS:**

   ```bash
   brew install ffmpeg
   ```

3. **Verify installation:**

   ```bash
   python downloader.py --test dep
   ```

## Usage

### Input File Format

Create a text file (e.g., `urls.txt`) with the following format:

```plaintext
videoname:url_to_video
another_video:url_to_another_video
```

Example:

```plaintext
intro_tutorial:https://youtube.com/watch?v=abc123
lesson_01:https://youtube.com/watch?v=def456
background_music:https://youtube.com/watch?v=ghi789

# Comments start with #
# Empty lines are ignored
```

### Basic Usage

Download videos from `urls.txt` to `output/` directory:

```bash
python downloader.py
```

### Command-Line Options

```bash
python downloader.py [OPTIONS]
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--input` | `-i` | Path to input text file | `urls.txt` |
| `--output` | `-o` | Output directory | `output` |
| `--format` | `-f` | Format code (see below) | `ba+bv` |
| `--ext` | `-e` | Output file extension | `mp4` |
| `--retry` | `-r` | Number of retry attempts | `3` |
| `--delay` | `-d` | Delay between downloads (seconds) | `1` |
| `--num` | `-n` | Download only first N videos | All |
| `--test` | `-t` | Run tests (url/dep/all) | - |
| `--dry-run` | | Simulate without downloading | - |
| `--help` | `-h` | Show help message | - |
| `--version` | `-v` | Show version | - |
| `--example` | `-x` | Show usage examples | - |

### Format Options

- `ba` or `bestaudio` - Best audio only
- `bv` or `bestvideo` - Best video only
- `ba+bv` or `bestaudio+bestvideo` - Best audio and video merged (default)

### Extension Options

**For video formats (`bv` or `ba+bv`):**

- `mp4` (default), `mkv`, `webm`

**For audio formats (`ba`):**

- `mp3`, `m4a`, `aac`, `opus`, `wav`, `flac`

## Examples

### Download best video+audio as MP4

```bash
python downloader.py --input urls.txt --output videos/
```

### Download audio only as MP3

```bash
python downloader.py --format ba --ext mp3 --output music/
```

### Download with custom settings

```bash
python downloader.py -i my_urls.txt -o downloads/ -f ba+bv -e mkv -r 5 -d 3
```

### Download only first 10 videos

```bash
python downloader.py --num 10
```

### Test URLs before downloading

```bash
python downloader.py --test url
```

### Check if dependencies are installed

```bash
python downloader.py --test dep
```

### Run all tests

```bash
python downloader.py --test all
```

### Dry run (simulate without downloading)

```bash
python downloader.py --dry-run
```

## Output

Downloaded files are saved as:

```plaintext
<output_directory>/<videoname>.<ext>
```

Example: If your `urls.txt` contains:

```plaintext
intro:https://youtube.com/watch?v=abc123
```

The output will be: `output/intro.mp4`

## Error Handling

- The script validates input file format before processing
- Invalid URLs are detected and reported
- Failed downloads are retried based on `--retry` setting
- Missing dependencies are checked before execution
- Incompatible format/extension combinations are rejected

## Troubleshooting

**"Missing dependencies" error:**

- Run `python downloader.py --test dep` to check what's missing
- Install yt-dlp: `pip install yt-dlp`
- Install ffmpeg and add to PATH

**"Invalid format" error in input file:**

- Ensure each line follows `videoname:url` format
- Check for missing colon `:` separator
- Run `python downloader.py --test url` to validate

**Download fails:**

- Verify URL is accessible
- Check internet connection
- Increase retry attempts: `--retry 5`
- Some videos may have restrictions

## License

MIT License - See [LICENSE](LICENSE) file for details

## Author

1172005thinh (QuickComp.)

## Version

1.1.0
