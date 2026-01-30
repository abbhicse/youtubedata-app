import googleapiclient.discovery
import pandas as pd
from googleapiclient.errors import HttpError
from datetime import datetime
import logging
import os

# Create log directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    filename="logs/fetch.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def initialize_youtube_api(api_key):
    print("Initializing YouTube API client")
    logging.info("Initializing YouTube API client")
    return googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)


def fetch_channel_data(youtube, channel_id):
    print(f"Fetching data for channel ID: {channel_id}")
    logging.info(f"Fetching data for channel ID: {channel_id}")

    request = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        id=channel_id
    )
    response = request.execute()

    if not response.get("items"):
        print("No channel found.")
        logging.error("No channel found.")
        return {}

    channel_info = response["items"][0]

    channel_data = {
        channel_info["snippet"]["title"]: {
            "Channel_Name": channel_info["snippet"]["title"],
            "Channel_Id": channel_info["id"],
            "Subscription_Count": int(channel_info["statistics"].get("subscriberCount", 0)),
            "Channel_Views": int(channel_info["statistics"].get("viewCount", 0)),
            "Channel_Description": channel_info["snippet"].get("description", ""),
            "Playlist_Id": channel_info["contentDetails"]["relatedPlaylists"]["uploads"]
        }
    }

    print("Fetching playlists...")
    logging.info("Fetching playlists...")
    channel_data["Playlists"] = fetch_playlists(youtube, channel_id)
    # Add uploads playlist manually (needed for FK in videos)
    channel_data["Playlists"].append({
        "Playlist_Id": channel_info["contentDetails"]["relatedPlaylists"]["uploads"],
        "Channel_Id": channel_info["id"],
        "Playlist_Name": "Uploads"
    })

    print("Fetching videos...")
    logging.info("Fetching videos...")
    uploads_id = channel_data[channel_info["snippet"]["title"]]["Playlist_Id"]
    videos = fetch_videos(youtube, uploads_id)

    for video_id, video_details in videos.items():
        channel_data[video_id] = video_details

    print("Channel data successfully fetched.")
    logging.info("Channel data successfully fetched.")
    return channel_data


def fetch_playlists(youtube, channel_id):
    playlists = []
    request = youtube.playlists().list(
        part="snippet",
        channelId=channel_id,
        maxResults=50
    )

    page_count = 0
    max_pages = 5

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

    print(f"Playlists fetched: {len(playlists)}")
    logging.info(f"Playlists fetched: {len(playlists)}")
    return playlists


def fetch_videos(youtube, playlist_id):
    videos = {}
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )

    page_count = 0
    max_pages = 5

    while request and page_count < max_pages:
        response = request.execute()
        print(f"Fetching video page {page_count + 1}")
        logging.info(f"Fetching video page {page_count + 1}")
        for item in response.get("items", []):
            video_id = item["snippet"]["resourceId"]["videoId"]
            print(f"Fetching details for video ID: {video_id}")
            logging.info(f"Fetching details for video ID: {video_id}")
            videos[video_id] = fetch_video_details(youtube, video_id)
        request = youtube.playlistItems().list_next(request, response)
        page_count += 1

    print(f"Total videos fetched: {len(videos)}")
    logging.info(f"Total videos fetched: {len(videos)}")
    return videos


def fetch_video_details(youtube, video_id):
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=video_id
    )
    response = request.execute()

    if not response.get("items"):
        print(f"No details found for video {video_id}")
        logging.warning(f"No details found for video {video_id}")
        return {}

    video_info = response["items"][0]

    video_data = {
        "Video_Id": video_info["id"],
        "Video_Name": video_info["snippet"]["title"],
        "Video_Description": video_info["snippet"].get("description", ""),
        "Tags": video_info["snippet"].get("tags", []),
        "PublishedAt": video_info["snippet"]["publishedAt"],
        "View_Count": int(video_info["statistics"].get("viewCount", 0)),
        "Like_Count": int(video_info["statistics"].get("likeCount", 0)),
        "Dislike_Count": int(video_info["statistics"].get("dislikeCount", 0)),
        "Favorite_Count": int(video_info["statistics"].get("favoriteCount", 0)),
        "Comment_Count": int(video_info["statistics"].get("commentCount", 0)),
        "Duration": video_info["contentDetails"]["duration"],
        "Thumbnail": video_info["snippet"]["thumbnails"]["high"]["url"],
        "Caption_Status": "Available" if video_info["contentDetails"].get("caption") == "true" else "Not Available",
    }

    print(f"Fetching comments for video {video_id}")
    logging.info(f"Fetching comments for video {video_id}")
    video_data["Comments"] = fetch_video_comments(youtube, video_id)

    return video_data


def fetch_video_comments(youtube, video_id):
    comments = {}
    page_count = 0
    max_pages = 5

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=50
        )

        while request and page_count < max_pages:
            response = request.execute()
            for item in response.get("items", []):
                comment_info = item["snippet"]["topLevelComment"]["snippet"]
                comment_id = item["id"]
                comments[comment_id] = {
                    "Comment_Id": comment_id,
                    "Comment_Text": comment_info.get("textDisplay", ""),
                    "Comment_Author": comment_info.get("authorDisplayName", "Unknown"),
                    "Comment_PublishedAt": comment_info.get("publishedAt", datetime.utcnow().isoformat())
                }
            request = youtube.commentThreads().list_next(request, response)
            page_count += 1

    except HttpError as e:
        if e.resp.status == 403 and "commentsDisabled" in str(e):
            fallback_comment_id = f"{video_id}_NO_COMMENT"
            comments[fallback_comment_id] = {
                "Comment_Id": fallback_comment_id,
                "Comment_Text": "Comment is disabled",
                "Comment_Author": "Unknown",
                "Comment_PublishedAt": datetime.utcnow().isoformat()
            }
            print(f"Comments disabled for video {video_id}")
            logging.warning(f"Comments disabled for video {video_id}")
        else:
            print(f"HttpError while fetching comments for {video_id}: {e}")
            logging.error(f"HttpError while fetching comments for {video_id}: {e}")
    except Exception as e:
        print(f"Unexpected error for {video_id}: {e}")
        logging.error(f"Unexpected error for {video_id}: {e}")

    return comments


def dict_to_dataframe(data_dict):
    return pd.DataFrame([data_dict])
