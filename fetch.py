import googleapiclient.discovery
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime
import logging
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Logging configuration
logging.basicConfig(
    filename="logs/fetch.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def initialize_youtube_api(api_key):
    logging.info("Initializing YouTube API client")
    return googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)


def fetch_channel_data(youtube, channel_id, max_video_pages=2, max_comment_pages=2):
    logging.info(f"Fetching channel data for ID: {channel_id}")
    try:
        response = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id
        ).execute()

        if not response.get("items"):
            logging.warning("No channel found.")
            return {}

        info = response["items"][0]
        uploads_playlist_id = info["contentDetails"]["relatedPlaylists"]["uploads"]

        channel_data = {
            info["snippet"]["title"]: {
                "Channel_Name": info["snippet"]["title"],
                "Channel_Id": info["id"],
                "Subscription_Count": int(info["statistics"].get("subscriberCount", 0)),
                "Channel_Views": int(info["statistics"].get("viewCount", 0)),
                "Channel_Description": info["snippet"].get("description", ""),
                "Playlist_Id": uploads_playlist_id
            }
        }

        logging.info("Fetching playlists...")
        playlists = fetch_playlists(youtube, channel_id)
        playlists.append({
            "Playlist_Id": uploads_playlist_id,
            "Channel_Id": info["id"],
            "Playlist_Name": "Uploads"
        })
        channel_data["Playlists"] = playlists

        logging.info("Fetching videos...")
        videos = fetch_videos(youtube, uploads_playlist_id, max_pages=max_video_pages, comment_pages=max_comment_pages)
        for video_id, video_details in videos.items():
            channel_data[video_id] = video_details

        logging.info("Successfully fetched channel data.")
        return channel_data

    except HttpError as e:
        logging.error(f"HTTP error during channel fetch: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    return {}


def fetch_playlists(youtube, channel_id, max_pages=5):
    playlists = []
    try:
        request = youtube.playlists().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50
        )

        page_count = 0
        while request and page_count < max_pages:
            response = request.execute()
            for item in response.get("items", []):
                playlists.append({
                    "Playlist_Id": item["id"],
                    "Channel_Id": channel_id,
                    "Playlist_Name": item["snippet"]["title"]
                })
            request = youtube.playlists().list_next(request, response)
            page_count += 1

        logging.info(f"Fetched {len(playlists)} playlists.")
    except Exception as e:
        logging.error(f"Failed to fetch playlists: {e}")
    return playlists


def fetch_videos(youtube, playlist_id, max_pages=5, comment_pages=2):
    videos = {}
    try:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50
        )

        page_count = 0
        while request and page_count < max_pages:
            response = request.execute()
            logging.info(f"Fetching videos page {page_count + 1}")
            for item in response.get("items", []):
                video_id = item["snippet"]["resourceId"]["videoId"]
                video_data = fetch_video_details(youtube, video_id, comment_pages)
                if video_data:
                    video_data["Playlist_Id"] = playlist_id  
                    videos[video_id] = video_data
            request = youtube.playlistItems().list_next(request, response)
            page_count += 1

        logging.info(f"Total videos fetched: {len(videos)}")
    except Exception as e:
        logging.error(f"Failed to fetch videos: {e}")
    return videos


def fetch_video_details(youtube, video_id, comment_pages=2):
    try:
        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        ).execute()

        if not response.get("items"):
            logging.warning(f"No details for video {video_id}")
            return {}

        video = response["items"][0]
        thumbnail_url = video["snippet"]["thumbnails"].get("high", {}).get("url", "")

        data = {
            "Video_Id": video["id"],
            "Video_Name": video["snippet"]["title"],
            "Video_Description": video["snippet"].get("description", ""),
            "Tags": video["snippet"].get("tags", []),
            "PublishedAt": video["snippet"]["publishedAt"],
            "View_Count": int(video["statistics"].get("viewCount", 0)),
            "Like_Count": int(video["statistics"].get("likeCount", 0)),
            "Dislike_Count": int(video["statistics"].get("dislikeCount", 0) or 0),
            "Favorite_Count": int(video["statistics"].get("favoriteCount", 0)),
            "Comment_Count": int(video["statistics"].get("commentCount", 0)),
            "Duration": video["contentDetails"]["duration"],
            "Thumbnail": thumbnail_url,
            "Caption_Status": "Available" if video["contentDetails"].get("caption") == "true" else "Not Available",
            "Comments": fetch_video_comments(youtube, video_id, max_pages=comment_pages)
        }

        return data
    except Exception as e:
        logging.error(f"Error fetching video details for {video_id}: {e}")
        return {}


def fetch_video_comments(youtube, video_id, max_pages=5):
    comments = {}
    page_count = 0

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=50
        )

        while request and page_count < max_pages:
            response = request.execute()
            for item in response.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                comment_id = item["id"]
                comments[comment_id] = {
                    "Comment_Id": comment_id,
                    "Comment_Text": snippet.get("textDisplay", ""),
                    "Comment_Author": snippet.get("authorDisplayName", "Unknown"),
                    "Comment_PublishedAt": snippet.get("publishedAt", datetime.utcnow().isoformat())
                }
            request = youtube.commentThreads().list_next(request, response)
            page_count += 1

    except HttpError as e:
        if e.resp.status == 403 and "commentsDisabled" in str(e):
            logging.warning(f"Comments disabled for video {video_id}")
            fallback_id = f"{video_id}_NO_COMMENT"
            comments[fallback_id] = {
                "Comment_Id": fallback_id,
                "Comment_Text": "Comments disabled",
                "Comment_Author": "N/A",
                "Comment_PublishedAt": datetime.utcnow().isoformat()
            }
        else:
            logging.error(f"HTTP error while fetching comments for {video_id}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error for video {video_id} comments: {e}")

    return comments


def dict_to_dataframe(data_dict):
    """Converts a flat dictionary to a single-row pandas DataFrame."""
    return pd.DataFrame([data_dict])
