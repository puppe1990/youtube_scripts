# YouTube Scripts

A collection of Python scripts and Jupyter notebooks for downloading YouTube videos and transcripts using various APIs.

## Features

- 📥 Download YouTube video transcripts using TranscriptAPI.com
- 🎬 Download YouTube videos using Tactiq API
- 📝 Organize transcripts into structured folders
- 🔄 Support for batch processing from file lists
- ⚙️ Configurable output formats (Markdown, JSON, Text)

## Requirements

- Python 3.7+
- See `requirements.txt` for dependencies

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd youtube-scripts
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your API keys:
```env
TRANSCRIPT_API_KEY=your_transcript_api_key_here
```

## Usage

### Download Transcripts

#### Using the Python Script

The `download_transcripts.py` script reads YouTube URLs from `list.txt` and downloads transcripts:

```bash
python download_transcripts.py
```

The script will:
- Read URLs from `list.txt` (one per line)
- Download transcripts using TranscriptAPI.com
- Save transcripts as Markdown files in a timestamped folder
- Display progress and summary statistics

#### Using Jupyter Notebooks

- `download_transcriptapi.ipynb` - Interactive transcript downloading
- `download_all_videos_youtube_tactiq_api.ipynb` - Download videos and transcripts using Tactiq API
- `download_all_videos_youtube_tactiq_api_by_list.ipynb` - Batch download from a list

### Input Files

- `list.txt` - Contains YouTube URLs (one per line)
- `links.csv` - Alternative input format for video links
- `proxies.txt` - Proxy configuration (if needed)

### Output

Transcripts are saved in the `transcripts/` directory, organized by channel/playlist structure. Each transcript is saved as a Markdown file with:
- Video title
- Original video link
- Video ID
- Detected language
- Full transcript text

## Project Structure

```
youtube-scripts/
├── download_transcripts.py          # Main Python script for transcript downloading
├── download_transcriptapi.ipynb     # Jupyter notebook for transcript API
├── download_all_videos_youtube_tactiq_api.ipynb  # Tactiq API notebook
├── download_all_videos_youtube_tactiq_api_by_list.ipynb  # Batch download notebook
├── transcript.ipynb                  # Additional transcript utilities
├── list.txt                         # Input file with YouTube URLs
├── links.csv                        # CSV input file
├── proxies.txt                      # Proxy configuration
├── requirements.txt                 # Python dependencies
├── transcripts/                     # Output directory for transcripts
│   ├── all_transcripts.txt          # Combined transcripts
│   └── [Channel/Playlist folders]/  # Organized by source
└── README.md                        # This file
```

## Configuration

### Environment Variables

Create a `.env` file with:
- `TRANSCRIPT_API_KEY` - Your TranscriptAPI.com API key

### File Formats

**list.txt** format:
```
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
# Comments start with #
```

## Dependencies

- `requests` - HTTP library for API calls
- `python-dotenv` - Environment variable management
- `beautifulsoup4` - HTML parsing
- `youtube-transcript-api` - YouTube transcript extraction
- `yt-dlp` - YouTube video downloading

## Notes

- The scripts include rate limiting and retry logic to handle API limits
- Transcripts are automatically formatted as Markdown files
- Video metadata (title, channel, etc.) is included when available
- Invalid characters in video titles are cleaned for safe filenames

## License

[Add your license here]

## Contributing

[Add contribution guidelines if applicable]

