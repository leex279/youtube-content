# YouTube MCP Server

> **DISCLAIMER**: This MCP server is for educational purposes only and is not production-ready. It is intended as a learning resource and demonstration of the Model Context Protocol integration with YouTube's API.

A Model Context Protocol (MCP) server that facilitates interaction with YouTube's data through a standardized interface. This server provides a suite of methods categorized under videos, channels, playlists, and transcripts, enabling comprehensive access to YouTube content.

## Features

### 📺 Video Management
- **getVideo**: Retrieve detailed information about a specific YouTube video
- **searchVideos**: Search for YouTube videos based on a query string
- **listVideos**: List videos uploaded by a specific YouTube channel
- **getVideoStatistics**: Get statistics for a specific YouTube video
- **getVideoComments**: Retrieve comments for a specific YouTube video

### 📄 Transcript Management
- **getTranscript**: Retrieve the transcript of a YouTube video
- **getTimestampedCaptions**: Retrieve timestamped captions for a YouTube video
- **searchTranscripts**: Search for specific terms within a YouTube video's transcript

### 📺 Channel Management
- **getChannel**: Retrieve detailed information about a YouTube channel
- **listPlaylists**: List playlists created by a specific YouTube channel
- **getChannelStatistics**: Get statistics for a specific YouTube channel
- **searchChannelContent**: Search for content within a specific YouTube channel

### 📂 Playlist Management
- **getPlaylistItems**: Retrieve videos contained within a specific YouTube playlist
- **getPlaylist**: Retrieve detailed information about a YouTube playlist
- **searchPlaylists**: Search for YouTube playlists based on a query string
- **getPlaylistTranscripts**: Retrieve transcripts for all videos within a YouTube playlist

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd youtube-mcp-server
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the root directory with the following content:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key
   HOST=0.0.0.0  # Optional, default is 0.0.0.0
   PORT=8050     # Optional, default is 8050
   TRANSPORT=sse # Optional, can be 'sse' or 'stdio', default is 'sse'
   ```

2. Obtain a YouTube API key:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the YouTube Data API v3
   - Create an API key and add it to your `.env` file

## Usage

### Starting the Server

Run the server with the following command:

```bash
python main.py
```

The server will start and listen for connections based on the configured transport method (SSE or STDIO).

### Connecting to the Server

You can connect to the server using any MCP client. The server will be available at:

- SSE transport: `http://<HOST>:<PORT>/sse`
- STDIO transport: Standard input/output streams

### Example Tool Calls

#### Get Video Details

```json
{
  "name": "getVideo",
  "params": {
    "videoId": "dQw4w9WgXcQ"
  }
}
```

#### Search Videos

```json
{
  "name": "searchVideos",
  "params": {
    "query": "machine learning tutorial",
    "maxResults": 5
  }
}
```

#### Get Video Transcript

```json
{
  "name": "getTranscript",
  "params": {
    "videoId": "dQw4w9WgXcQ",
    "language": "en"
  }
}
```

## Dependencies

- MCP Python SDK
- FastAPI
- Uvicorn
- aiohttp
- youtube-transcript-api
- python-dotenv

## License

This project is licensed under the MIT License - see the LICENSE file for details.