import os
import json
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, Union

# Import the YouTube Transcript API for transcript functionality
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
TRANSCRIPT_API_AVAILABLE = True

class YouTubeClient:
    """Client for interacting with YouTube APIs."""
    
    def __init__(self):
        """Initialize the YouTube client with API key from environment variables."""
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            print("Warning: YOUTUBE_API_KEY environment variable not set. API functionality will be limited.")
        
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.session = None
    
    async def _ensure_session(self):
        """Ensure an aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def _api_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the YouTube Data API.
        
        Args:
            endpoint: The API endpoint to call
            params: The query parameters for the request
            
        Returns:
            The JSON response from the API
        """
        await self._ensure_session()
        
        # Add API key to params
        if self.api_key:
            params['key'] = self.api_key
        
        url = f"{self.base_url}/{endpoint}"
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"YouTube API error: {response.status} - {error_text}")
            
            return await response.json()
    
    # Video Management Methods
    async def get_video(self, video_id: str) -> Dict[str, Any]:
        """Get details for a specific video."""
        params = {
            'part': 'snippet,contentDetails,statistics',
            'id': video_id
        }
        
        response = await self._api_request('videos', params)
        
        if not response.get('items'):
            raise Exception(f"Video not found with ID: {video_id}")
        
        return response['items'][0]
    
    async def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for videos based on a query."""
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': max_results
        }
        
        response = await self._api_request('search', params)
        
        return response.get('items', [])
    
    async def list_videos(self, channel_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """List videos from a specific channel."""
        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'type': 'video',
            'maxResults': max_results,
            'order': 'date'
        }
        
        response = await self._api_request('search', params)
        
        return response.get('items', [])
    
    async def get_video_statistics(self, video_id: str) -> Dict[str, Any]:
        """Get statistics for a specific video."""
        params = {
            'part': 'statistics',
            'id': video_id
        }
        
        response = await self._api_request('videos', params)
        
        if not response.get('items'):
            raise Exception(f"Video not found with ID: {video_id}")
        
        return response['items'][0]['statistics']
    
    # Transcript Management Methods
    async def get_transcript(self, video_id: str, language: Optional[str] = None) -> str:
        """Get the transcript for a specific video."""
        try:
            transcript_data = None
            
            if language:
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    transcript = transcript_list.find_transcript([language])
                    transcript_data = transcript.fetch()
                except Exception:
                    # If specified language fails, try to get any available transcript
                    transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            else:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine all transcript segments into a single text
            full_transcript = ' '.join([item['text'] for item in transcript_data])
            return full_transcript
        except TranscriptsDisabled:
            return "Transcripts are disabled for this video."
        except NoTranscriptFound:
            return "No transcript found for the specified language."
        except Exception as e:
            return f"Error retrieving transcript: {str(e)}"
    
    async def get_timestamped_captions(self, video_id: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get timestamped captions for a specific video."""
        try:
            transcript_data = None
            
            if language:
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    transcript = transcript_list.find_transcript([language])
                    transcript_data = transcript.fetch()
                except Exception:
                    # If specified language fails, try to get any available transcript
                    transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            else:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            
            return transcript_data
        except TranscriptsDisabled:
            return [{"text": "Transcripts are disabled for this video.", "start": 0, "duration": 0}]
        except NoTranscriptFound:
            return [{"text": "No transcript found for the specified language.", "start": 0, "duration": 0}]
        except Exception as e:
            return [{"text": f"Error retrieving timestamped captions: {str(e)}", "start": 0, "duration": 0}]
    
    async def search_transcripts(self, query: str, video_id: str) -> List[Dict[str, Any]]:
        """Search for terms within a video's transcript."""
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Simple search implementation - find segments containing the query
            query = query.lower()
            matching_segments = [segment for segment in transcript_data if query in segment['text'].lower()]
            
            if not matching_segments:
                return [{"text": f"No matches found for '{query}' in this transcript.", "start": 0, "duration": 0}]
                
            return matching_segments
        except TranscriptsDisabled:
            return [{"text": "Transcripts are disabled for this video.", "start": 0, "duration": 0}]
        except NoTranscriptFound:
            return [{"text": "No transcript found for this video.", "start": 0, "duration": 0}]
        except Exception as e:
            return [{"text": f"Error searching transcript: {str(e)}", "start": 0, "duration": 0}]
    
    # Channel Management Methods
    async def get_channel(self, channel_id: str) -> Dict[str, Any]:
        """Get details for a specific channel.
        
        Args:
            channel_id: The channel ID or handle (with @ prefix)
            
        Returns:
            Channel details
        """
        # Check if channel_id is a handle (starts with @)
        if channel_id.startswith('@'):
            try:
                channel_id = await self._resolve_channel_handle(channel_id)
            except Exception as e:
                raise Exception(f"Failed to resolve channel handle: {str(e)}")
        
        params = {
            'part': 'snippet,contentDetails,statistics',
            'id': channel_id
        }
        
        response = await self._api_request('channels', params)
        
        if not response.get('items'):
            raise Exception(f"Channel not found with ID: {channel_id}")
        
        return response['items'][0]
    
    async def list_playlists(self, channel_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """List playlists from a specific channel.
        
        Args:
            channel_id: The channel ID or handle (with @ prefix)
            max_results: Maximum number of results to return
            
        Returns:
            List of playlists from the channel
        """
        # Check if channel_id is a handle (starts with @)
        if channel_id.startswith('@'):
            try:
                channel_id = await self._resolve_channel_handle(channel_id)
            except Exception as e:
                raise Exception(f"Failed to resolve channel handle: {str(e)}")
        
        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'maxResults': max_results
        }
        
        response = await self._api_request('playlists', params)
        
        return response.get('items', [])
    
    async def get_channel_statistics(self, channel_id: str) -> Dict[str, Any]:
        """Get statistics for a specific channel.
        
        Args:
            channel_id: The channel ID or handle (with @ prefix)
            
        Returns:
            Channel statistics
        """
        # Check if channel_id is a handle (starts with @)
        if channel_id.startswith('@'):
            try:
                channel_id = await self._resolve_channel_handle(channel_id)
            except Exception as e:
                raise Exception(f"Failed to resolve channel handle: {str(e)}")
        
        params = {
            'part': 'statistics',
            'id': channel_id
        }
        
        response = await self._api_request('channels', params)
        
        if not response.get('items'):
            raise Exception(f"Channel not found with ID: {channel_id}")
        
        return response['items'][0]['statistics']
    
    async def search_channel_content(self, channel_id: str, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for content within a specific channel.
        
        Args:
            channel_id: The channel ID or handle (with @ prefix)
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of content items matching the query
        """
        # Check if channel_id is a handle (starts with @)
        if channel_id.startswith('@'):
            try:
                channel_id = await self._resolve_channel_handle(channel_id)
            except Exception as e:
                raise Exception(f"Failed to resolve channel handle: {str(e)}")
        
        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'q': query,
            'maxResults': max_results
        }
        
        response = await self._api_request('search', params)
        
        return response.get('items', [])
    
    # Playlist Management Methods
    async def get_playlist_items(self, playlist_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get items from a specific playlist."""
        params = {
            'part': 'snippet',
            'playlistId': playlist_id,
            'maxResults': max_results
        }
        
        response = await self._api_request('playlistItems', params)
        
        return response.get('items', [])
    
    async def get_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """Get details for a specific playlist."""
        params = {
            'part': 'snippet,contentDetails',
            'id': playlist_id
        }
        
        response = await self._api_request('playlists', params)
        
        if not response.get('items'):
            raise Exception(f"Playlist not found with ID: {playlist_id}")
        
        return response['items'][0]
    
    async def search_playlists(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for playlists based on a query."""
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'playlist',
            'maxResults': max_results
        }
        
        response = await self._api_request('search', params)
        
        return response.get('items', [])
    
    async def get_playlist_transcripts(self, playlist_id: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Get transcripts for all videos in a playlist."""
        # First, get all videos in the playlist
        playlist_items = await self.get_playlist_items(playlist_id, max_results=50)  # Increase max_results for playlists
        
        # Extract video IDs
        video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_items if 'resourceId' in item['snippet']]
        
        # Get transcripts for each video
        transcripts = {}
        for video_id in video_ids:
            try:
                video_details = await self.get_video(video_id)
                video_title = video_details['snippet']['title']
                
                try:
                    transcript_data = None
                    if language:
                        try:
                            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                            transcript = transcript_list.find_transcript([language])
                            transcript_data = transcript.fetch()
                        except Exception:
                            # If specified language fails, try to get any available transcript
                            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
                    else:
                        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
                    
                    # Combine all transcript segments into a single text
                    full_transcript = ' '.join([item['text'] for item in transcript_data])
                    transcripts[video_title] = full_transcript
                except TranscriptsDisabled:
                    transcripts[video_title] = "Transcripts are disabled for this video."
                except NoTranscriptFound:
                    transcripts[video_title] = "No transcript found for the specified language."
                except Exception as e:
                    transcripts[video_title] = f"Error retrieving transcript: {str(e)}"
            except Exception as e:
                # If we can't get video details, use the ID as the key
                transcripts[video_id] = f"Error retrieving video details: {str(e)}"
        
        return transcripts
    
    async def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get comments for a specific video.
        
        Args:
            video_id: The unique identifier of the YouTube video
            max_results: Maximum number of comments to return (default: 100)
            
        Returns:
            List of comment threads including top-level comments and their replies
        """
        comments = []
        page_token = None
        total_comments = 0
        
        try:
            # Continue fetching comments until we reach max_results or run out of pages
            while total_comments < max_results:
                # Set up parameters for the API request
                params = {
                    'part': 'snippet,replies',
                    'videoId': video_id,
                    'maxResults': min(100, max_results - total_comments),  # API allows max 100 per request
                    'textFormat': 'plainText'
                }
                
                # Add page token if we're not on the first page
                if page_token:
                    params['pageToken'] = page_token
                
                # Make the API request
                response = await self._api_request('commentThreads', params)
                
                # Get the items from the response
                items = response.get('items', [])
                if not items:
                    break
                
                # Add the items to our list of comments
                comments.extend(items)
                total_comments += len(items)
                
                # Get the next page token
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            return comments
        except Exception as e:
            # Handle common errors
            error_message = str(e)
            if "commentsDisabled" in error_message:
                return [{"error": "Comments are disabled for this video."}]
            elif "videoNotFound" in error_message:
                return [{"error": f"Video not found with ID: {video_id}"}]
            else:
                return [{"error": f"Error retrieving comments: {error_message}"}]
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()