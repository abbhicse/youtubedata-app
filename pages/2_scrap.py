import streamlit as st
import pandas as pd
from data_processing import transform_channel_data
from fetch import dict_to_dataframe, fetch_channel_data
from database import insert_channel, insert_playlist, insert_videos, insert_comments 

st.title("Fetch & Store YouTube Data")

# Use stored API & DB from session state
youtube = st.session_state.get("youtube_api")
conn = st.session_state.get("db_connection")

# Explicitly check database connection
if conn:
    st.success("Database connection is active.")
else:
    st.error("Database connection is missing. Please run 'App Initialization' first.")

if not youtube:
    st.error("YouTube API is not initialized. Please run 'App Initialization' first.")

# User inputs channel ID
channel_id = st.text_input("Enter YouTube Channel ID")

def fetch_and_store_data(youtube, conn, channel_id):
    """Fetch, transform, store, and display YouTube channel data."""
    try:
        st.info("Fetching channel data...")
        channel_data = fetch_channel_data(youtube, channel_id)

        if not channel_data:
            st.error("No data found. Check the Channel ID.")
            return

        # Step 1: Transform data
        cleaned_data = transform_channel_data(channel_data)

        # Step 2: Store data in the database
        insert_channel(conn, cleaned_data["channel"])  # Store channel data
        for playlist in cleaned_data["playlists"]:
            insert_playlist(conn, playlist)  # Store playlist data
        insert_videos(conn, cleaned_data["videos"])  # Store video data
        insert_comments(conn, cleaned_data["comments"])  # Store comments data
        
        conn.commit()  # Commit changes to database
        
        # Step 3: Display the data in Streamlit UI
        st.success("Data fetched, stored in database, and transformed successfully. Now proceed to Query!")
        # Display channel info
        st.subheader("Channel Info")
        st.json(cleaned_data["channel"])
        # Display playlists
        st.subheader("Playlists")
        st.dataframe(pd.DataFrame(cleaned_data["playlists"]))
        # Display videos
        st.subheader("Videos")
        st.dataframe(pd.DataFrame(cleaned_data["videos"]))
        # Display comments (optional: limit rows for readability)
        st.subheader("Comments")
        st.dataframe(pd.DataFrame(cleaned_data["comments"]).head(50))

    except Exception as e:
        st.error(f"Error fetching and storing channel data: {e}")

if st.button("Fetch and Store Data"):
    if not channel_id:
        st.warning("Please enter a valid YouTube Channel ID.")
    elif not conn:
        st.error("Database connection is missing. Please run 'App Initialization' first.")
    else:
        fetch_and_store_data(youtube, conn, channel_id)
