from isodate import parse_duration
from datetime import datetime


def transform_channel_data(raw_data):
    """
    Transforms raw YouTube API data into structured components:
    - channel
    - playlists
    - videos
    - comments

    Args:
        raw_data (dict): The raw dictionary returned from fetch_channel_data()

    Returns:
        dict: {
            "channel": dict,
            "playlists": list,
            "videos": list,
            "comments": list
        }
    """
    # Extract top-level channel metadata
    channel_meta = next((v for k, v in raw_data.items() if isinstance(v, dict) and "Channel_Id" in v), None)
    if not channel_meta:
        return {"channel": {}, "playlists": [], "videos": [], "comments": []}

    # Prepare channel data
    channel = {
        "channel_id": channel_meta["Channel_Id"],
        "channel_name": channel_meta["Channel_Name"],
        "channel_type": "N/A",
        "channel_views": channel_meta["Channel_Views"],
        "channel_description": channel_meta.get("Channel_Description", ""),
        "channel_status": "Active"
    }

    # Playlists
   # Normalize playlist keys to match database schema
    playlists_raw = raw_data.get("Playlists", [])
    playlists = [
        {
            "playlist_id": p["Playlist_Id"],
            "channel_id": p["Channel_Id"],
            "playlist_name": p["Playlist_Name"]
        }
        for p in playlists_raw
    ]

    # Videos and Comments
    videos = []
    comments = []

    for key, value in raw_data.items():
        if key in ["Playlists"] or value == channel_meta:
            continue  # Skip meta

        # Video normalization
        try:
            published_str = value["PublishedAt"]
            published_dt = datetime.strptime(published_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")

            video = {
                "video_id": value["Video_Id"],
                "playlist_id": channel_meta["Playlist_Id"],
                "video_name": value["Video_Name"],
                "video_description": value.get("Video_Description", ""),
                "published_date": published_dt,
                "view_count": value["View_Count"],
                "like_count": value["Like_Count"],
                "dislike_count": value["Dislike_Count"],
                "favorite_count": value["Favorite_Count"],
                "comment_count": value["Comment_Count"],
                "duration": int(parse_duration(value["Duration"]).total_seconds()),
                "thumbnail": value["Thumbnail"],
                "caption": value["Caption_Status"]
            }
            videos.append(video)

            # Extract comments
            for cid, cdata in value.get("Comments", {}).items():
                comment = {
                    "comment_id": cid,
                    "video_id": value["Video_Id"],
                    "comment_text": cdata["Comment_Text"],
                    "comment_author": cdata["Comment_Author"],
                    "comment_published_date": datetime.strptime(cdata["Comment_PublishedAt"].replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
                }
                comments.append(comment)
        except Exception as e:
            print(f"Error processing video {key}: {e}")

    return {
        "channel": channel,
        "playlists": playlists,
        "videos": videos,
        "comments": comments
    }
