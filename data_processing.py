from isodate import parse_duration
from datetime import datetime
import streamlit as st  # For optional warnings

def transform_channel_data(raw_data):
    """
    Transforms raw YouTube API data into structured records:
    - channel
    - playlists
    - videos
    - comments
    """
    # Extract channel metadata
    channel_meta = next(
        (v for k, v in raw_data.items() if isinstance(v, dict) and "Channel_Id" in v), None
    )
    if not channel_meta:
        st.warning("Channel metadata not found.")
        return {"channel": {}, "playlists": [], "videos": [], "comments": []}

    channel = {
        "channel_id": channel_meta["Channel_Id"],
        "channel_name": channel_meta["Channel_Name"],
        "channel_type": "N/A",
        "channel_views": channel_meta["Channel_Views"],
        "channel_description": channel_meta.get("Channel_Description", ""),
        "channel_status": "Active"
    }

    # Playlists
    playlists_raw = raw_data.get("Playlists", [])
    playlists = []
    playlist_lookup = {}  # Map to match video->playlist relationship

    for p in playlists_raw:
        pid = p.get("Playlist_Id")
        playlists.append({
            "playlist_id": pid,
            "channel_id": p.get("Channel_Id", channel["channel_id"]),
            "playlist_name": p.get("Playlist_Name", "Untitled Playlist")
        })
        playlist_lookup[pid] = True

    # Videos and Comments
    videos = []
    comments = []

    for key, value in raw_data.items():
        if key == "Playlists" or value == channel_meta:
            continue  # Skip non-video entries

        try:
            video_id = value["Video_Id"]
            published_str = value.get("PublishedAt", "").replace("Z", "")
            published_dt = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%S")

            # If the API didn't return playlist ID per video, fall back or skip
            playlist_id = value.get("Playlist_Id") or channel_meta.get("Playlist_Id")
            if not playlist_id:
                st.warning(f"Skipping video {video_id}: missing Playlist_Id")
                continue

            video = {
                "video_id": video_id,
                "playlist_id": playlist_id,
                "video_name": value.get("Video_Name", ""),
                "video_description": value.get("Video_Description", ""),
                "published_date": published_dt,
                "view_count": value.get("View_Count", 0),
                "like_count": value.get("Like_Count", 0),
                "dislike_count": value.get("Dislike_Count", 0),
                "favorite_count": value.get("Favorite_Count", 0),
                "comment_count": value.get("Comment_Count", 0),
                "duration": int(parse_duration(value.get("Duration", "PT0S")).total_seconds()),
                "thumbnail": value.get("Thumbnail", ""),
                "caption": value.get("Caption_Status", "")
            }
            videos.append(video)

            for cid, cdata in value.get("Comments", {}).items():
                try:
                    comment = {
                        "comment_id": cid,
                        "video_id": video_id,
                        "comment_text": cdata.get("Comment_Text", ""),
                        "comment_author": cdata.get("Comment_Author", ""),
                        "comment_published_date": datetime.strptime(
                            cdata["Comment_PublishedAt"].replace("Z", ""),
                            "%Y-%m-%dT%H:%M:%S"
                        )
                    }
                    comments.append(comment)
                except Exception as ce:
                    st.warning(f"Skipping malformed comment on video {video_id}: {ce}")

        except Exception as e:
            st.warning(f"Error processing video entry {key}: {e}")

    return {
        "channel": channel,
        "playlists": playlists,
        "videos": videos,
        "comments": comments
    }
