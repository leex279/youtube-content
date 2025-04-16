from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
import asyncio
import json
import os
import logging

from utils import YouTubeClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('youtube-mcp-server')

load_dotenv()

# Create a dataclass for our application context
@dataclass
class YouTubeContext:
    """Context for the YouTube MCP server."""
    youtube_client: YouTubeClient

@asynccontextmanager
async def youtube_lifespan(server: FastMCP) -> AsyncIterator[YouTubeContext]:
    """
    Manages the YouTube client lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        YouTubeContext: The context containing the YouTube client
    """
    # Create and initialize the YouTube client
    youtube_client = YouTubeClient()
    
    try:
        yield YouTubeContext(youtube_client=youtube_client)
    finally:
        # No explicit cleanup needed for the YouTube client
        pass

# Initialize FastMCP server with the YouTube client as context
mcp = FastMCP(
    "youtube-mcp-server",
    description="MCP server for interacting with YouTube data including videos, channels, playlists, and transcripts",
    lifespan=youtube_lifespan,
    host=os.getenv("HOST", "0.0.0.0"),
    port=os.getenv("PORT", "8050")
)        

# Video Management Tools
@mcp.tool()
async def getVideo(ctx: Context, videoId: str) -> str:
    """
    Retrieve detailed information about a specific YouTube video.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        videoId: The unique identifier of the YouTube video
        
    Returns:
        JSON formatted string containing video details including title, description, duration, and more
    """
    logger.info(f"Tool called: getVideo - Parameters: videoId={videoId}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        video_details = await youtube_client.get_video(videoId)
        logger.info(f"Tool completed: getVideo - Success")
        return json.dumps(video_details, indent=2)
    except Exception as e:
        logger.error(f"Tool error: getVideo - Error: {str(e)}")
        return f"Error retrieving video details: {str(e)}"

@mcp.tool()
async def searchVideos(ctx: Context, query: str, maxResults: int = 10) -> str:
    """
    Search for YouTube videos based on a query string.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        query: The search query string
        maxResults: Maximum number of results to return (default: 10)
        
    Returns:
        JSON formatted string containing a list of videos matching the search query
    """
    logger.info(f"Tool called: searchVideos - Parameters: query='{query}', maxResults={maxResults}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        search_results = await youtube_client.search_videos(query, maxResults)
        logger.info(f"Tool completed: searchVideos - Success - Found {len(search_results)} results")
        return json.dumps(search_results, indent=2)
    except Exception as e:
        logger.error(f"Tool error: searchVideos - Error: {str(e)}")
        return f"Error searching videos: {str(e)}"

@mcp.tool()
async def listVideos(ctx: Context, channelId: str, maxResults: int = 10) -> str:
    """
    List videos uploaded by a specific YouTube channel.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        channelId: The unique identifier of the YouTube channel
        maxResults: Maximum number of results to return (default: 10)
        
    Returns:
        JSON formatted string containing a list of videos from the specified channel
    """
    logger.info(f"Tool called: listVideos - Parameters: channelId={channelId}, maxResults={maxResults}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        channel_videos = await youtube_client.list_videos(channelId, maxResults)
        logger.info(f"Tool completed: listVideos - Success - Found {len(channel_videos)} videos")
        return json.dumps(channel_videos, indent=2)
    except Exception as e:
        logger.error(f"Tool error: listVideos - Error: {str(e)}")
        return f"Error listing channel videos: {str(e)}"

@mcp.tool()
async def getVideoStatistics(ctx: Context, videoId: str) -> str:
    """
    Get statistics for a specific YouTube video.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        videoId: The unique identifier of the YouTube video
        
    Returns:
        JSON formatted string containing video statistics including view count, like count, and comment count
    """
    logger.info(f"Tool called: getVideoStatistics - Parameters: videoId={videoId}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        video_stats = await youtube_client.get_video_statistics(videoId)
        logger.info(f"Tool completed: getVideoStatistics - Success")
        return json.dumps(video_stats, indent=2)
    except Exception as e:
        logger.error(f"Tool error: getVideoStatistics - Error: {str(e)}")
        return f"Error retrieving video statistics: {str(e)}"

# Transcript Management Tools
@mcp.tool()
async def getTranscript(ctx: Context, videoId: str, language: str = None) -> str:
    """
    Retrieve the transcript of a YouTube video.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        videoId: The unique identifier of the YouTube video
        language: Optional language code for the transcript (default: None, which uses the default language)
        
    Returns:
        Text content of the video transcript
    """
    logger.info(f"Tool called: getTranscript - Parameters: videoId={videoId}, language={language}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        transcript = await youtube_client.get_transcript(videoId, language)
        logger.info(f"Tool completed: getTranscript - Success")
        return transcript
    except Exception as e:
        logger.error(f"Tool error: getTranscript - Error: {str(e)}")
        return f"Error retrieving transcript: {str(e)}"

@mcp.tool()
async def getTimestampedCaptions(ctx: Context, videoId: str, language: str = None) -> str:
    """
    Retrieve timestamped captions for a YouTube video.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        videoId: The unique identifier of the YouTube video
        language: Optional language code for the captions (default: None, which uses the default language)
        
    Returns:
        JSON formatted string containing timestamped captions
    """
    logger.info(f"Tool called: getTimestampedCaptions - Parameters: videoId={videoId}, language={language}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        captions = await youtube_client.get_timestamped_captions(videoId, language)
        logger.info(f"Tool completed: getTimestampedCaptions - Success")
        return json.dumps(captions, indent=2)
    except Exception as e:
        logger.error(f"Tool error: getTimestampedCaptions - Error: {str(e)}")
        return f"Error retrieving timestamped captions: {str(e)}"

@mcp.tool()
async def searchTranscripts(ctx: Context, query: str, videoId: str) -> str:
    """
    Search for specific terms within a YouTube video's transcript.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        query: The search query string
        videoId: The unique identifier of the YouTube video
        
    Returns:
        JSON formatted string containing transcript segments matching the search query
    """
    logger.info(f"Tool called: searchTranscripts - Parameters: query='{query}', videoId={videoId}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        search_results = await youtube_client.search_transcripts(query, videoId)
        logger.info(f"Tool completed: searchTranscripts - Success - Found {len(search_results)} matches")
        return json.dumps(search_results, indent=2)
    except Exception as e:
        logger.error(f"Tool error: searchTranscripts - Error: {str(e)}")
        return f"Error searching transcript: {str(e)}"

@mcp.tool()
async def getVideoComments(ctx: Context, videoId: str, maxResults: int = 100) -> str:
    """
    Retrieve comments for a specific YouTube video.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        videoId: The unique identifier of the YouTube video
        maxResults: Maximum number of comments to return (default: 100)
        
    Returns:
        JSON formatted string containing comment threads including top-level comments and their replies
    """
    logger.info(f"Tool called: getVideoComments - Parameters: videoId={videoId}, maxResults={maxResults}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        comments = await youtube_client.get_video_comments(videoId, maxResults)
        logger.info(f"Tool completed: getVideoComments - Success - Retrieved {len(comments) if isinstance(comments, list) else 'N/A'} comments")
        return json.dumps(comments, indent=2)
    except Exception as e:
        logger.error(f"Tool error: getVideoComments - Error: {str(e)}")
        return f"Error retrieving video comments: {str(e)}"

# Channel Management Tools
@mcp.tool()
async def getChannel(ctx: Context, channelId: str) -> str:
    """
    Retrieve detailed information about a YouTube channel.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        channelId: The unique identifier of the YouTube channel
        
    Returns:
        JSON formatted string containing channel details including title, description, and more
    """
    logger.info(f"Tool called: getChannel - Parameters: channelId={channelId}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        channel_details = await youtube_client.get_channel(channelId)
        logger.info(f"Tool completed: getChannel - Success")
        return json.dumps(channel_details, indent=2)
    except Exception as e:
        logger.error(f"Tool error: getChannel - Error: {str(e)}")
        return f"Error retrieving channel details: {str(e)}"

@mcp.tool()
async def listPlaylists(ctx: Context, channelId: str, maxResults: int = 10) -> str:
    """
    List playlists created by a specific YouTube channel.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        channelId: The unique identifier of the YouTube channel
        maxResults: Maximum number of results to return (default: 10)
        
    Returns:
        JSON formatted string containing a list of playlists from the specified channel
    """
    logger.info(f"Tool called: listPlaylists - Parameters: channelId={channelId}, maxResults={maxResults}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        channel_playlists = await youtube_client.list_playlists(channelId, maxResults)
        logger.info(f"Tool completed: listPlaylists - Success - Found {len(channel_playlists) if isinstance(channel_playlists, list) else 'N/A'} playlists")
        return json.dumps(channel_playlists, indent=2)
    except Exception as e:
        logger.error(f"Tool error: listPlaylists - Error: {str(e)}")
        return f"Error listing channel playlists: {str(e)}"

@mcp.tool()
async def getChannelStatistics(ctx: Context, channelId: str) -> str:
    """
    Get statistics for a specific YouTube channel.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        channelId: The unique identifier of the YouTube channel
        
    Returns:
        JSON formatted string containing channel statistics including subscriber count and total views
    """
    logger.info(f"Tool called: getChannelStatistics - Parameters: channelId={channelId}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        channel_stats = await youtube_client.get_channel_statistics(channelId)
        logger.info(f"Tool completed: getChannelStatistics - Success")
        return json.dumps(channel_stats, indent=2)
    except Exception as e:
        logger.error(f"Tool error: getChannelStatistics - Error: {str(e)}")
        return f"Error retrieving channel statistics: {str(e)}"

@mcp.tool()
async def searchChannelContent(ctx: Context, channelId: str, query: str, maxResults: int = 10) -> str:
    """
    Search for content within a specific YouTube channel.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        channelId: The unique identifier of the YouTube channel
        query: The search query string
        maxResults: Maximum number of results to return (default: 10)
        
    Returns:
        JSON formatted string containing channel content matching the search query
    """
    logger.info(f"Tool called: searchChannelContent - Parameters: channelId={channelId}, query='{query}', maxResults={maxResults}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        search_results = await youtube_client.search_channel_content(channelId, query, maxResults)
        logger.info(f"Tool completed: searchChannelContent - Success - Found {len(search_results) if isinstance(search_results, list) else 'N/A'} results")
        return json.dumps(search_results, indent=2)
    except Exception as e:
        logger.error(f"Tool error: searchChannelContent - Error: {str(e)}")
        return f"Error searching channel content: {str(e)}"

# Playlist Management Tools
@mcp.tool()
async def getPlaylistItems(ctx: Context, playlistId: str, maxResults: int = 10) -> str:
    """
    Retrieve videos contained within a specific YouTube playlist.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        playlistId: The unique identifier of the YouTube playlist
        maxResults: Maximum number of results to return (default: 10)
        
    Returns:
        JSON formatted string containing a list of videos in the specified playlist
    """
    logger.info(f"Tool called: getPlaylistItems - Parameters: playlistId={playlistId}, maxResults={maxResults}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        playlist_items = await youtube_client.get_playlist_items(playlistId, maxResults)
        logger.info(f"Tool completed: getPlaylistItems - Success - Retrieved {len(playlist_items) if isinstance(playlist_items, list) else 'N/A'} items")
        return json.dumps(playlist_items, indent=2)
    except Exception as e:
        logger.error(f"Tool error: getPlaylistItems - Error: {str(e)}")
        return f"Error retrieving playlist items: {str(e)}"

@mcp.tool()
async def getPlaylist(ctx: Context, playlistId: str) -> str:
    """
    Retrieve detailed information about a YouTube playlist.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        playlistId: The unique identifier of the YouTube playlist
        
    Returns:
        JSON formatted string containing playlist details including title and description
    """
    logger.info(f"Tool called: getPlaylist - Parameters: playlistId={playlistId}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        playlist_details = await youtube_client.get_playlist(playlistId)
        logger.info(f"Tool completed: getPlaylist - Success")
        return json.dumps(playlist_details, indent=2)
    except Exception as e:
        logger.error(f"Tool error: getPlaylist - Error: {str(e)}")
        return f"Error retrieving playlist details: {str(e)}"

@mcp.tool()
async def searchPlaylists(ctx: Context, query: str, maxResults: int = 10) -> str:
    """
    Search for YouTube playlists based on a query string.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        query: The search query string
        maxResults: Maximum number of results to return (default: 10)
        
    Returns:
        JSON formatted string containing a list of playlists matching the search query
    """
    logger.info(f"Tool called: searchPlaylists - Parameters: query='{query}', maxResults={maxResults}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        search_results = await youtube_client.search_playlists(query, maxResults)
        logger.info(f"Tool completed: searchPlaylists - Success - Found {len(search_results) if isinstance(search_results, list) else 'N/A'} playlists")
        return json.dumps(search_results, indent=2)
    except Exception as e:
        logger.error(f"Tool error: searchPlaylists - Error: {str(e)}")
        return f"Error searching playlists: {str(e)}"

@mcp.tool()
async def getPlaylistTranscripts(ctx: Context, playlistId: str, language: str = None) -> str:
    """
    Retrieve transcripts for all videos within a YouTube playlist.
    
    Args:
        ctx: The MCP server provided context which includes the YouTube client
        playlistId: The unique identifier of the YouTube playlist
        language: Optional language code for the transcripts (default: None, which uses the default language)
        
    Returns:
        JSON formatted string containing transcripts for all videos in the playlist
    """
    logger.info(f"Tool called: getPlaylistTranscripts - Parameters: playlistId={playlistId}, language={language}")
    try:
        youtube_client = ctx.request_context.lifespan_context.youtube_client
        playlist_transcripts = await youtube_client.get_playlist_transcripts(playlistId, language)
        logger.info(f"Tool completed: getPlaylistTranscripts - Success")
        return json.dumps(playlist_transcripts, indent=2)
    except Exception as e:
        logger.error(f"Tool error: getPlaylistTranscripts - Error: {str(e)}")
        return f"Error retrieving playlist transcripts: {str(e)}"

async def main():
    logger.info("Starting YouTube MCP Server")
    transport = os.getenv("TRANSPORT", "sse")
    if transport == 'sse':
        # Run the MCP server with sse transport
        logger.info("Using SSE transport")
        await mcp.run_sse_async()
    else:
        # Run the MCP server with stdio transport
        logger.info("Using STDIO transport")
        await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())