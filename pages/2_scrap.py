import streamlit as st
import pandas as pd
from data_processing import transform_channel_data
from fetch import fetch_channel_data
from database import insert_channel, insert_playlist, insert_videos, insert_comments

# Page title
st.title("Fetch and Store YouTube Data")

# Retrieve session state variables
youtube = st.session_state.get("youtube_api")
conn = st.session_state.get("conn")

# Validate initialization
if not youtube:
    st.error("YouTube API is not initialized. Please run 'App Initialization' first.")
    st.stop()

if not conn:
    st.error("Database connection is missing. Please run 'App Initialization' first.")
    st.stop()

st.success("YouTube API and database connection are ready.")

# User input for channel ID
channel_id = st.text_input("Enter YouTube Channel ID")

def fetch_and_store_data(youtube, conn, channel_id):
    try:
        st.info("Fetching channel data...")
        channel_data = fetch_channel_data(youtube, channel_id)

        if not channel_data:
            st.error("No data found. Please check the Channel ID.")
            return

        # Transform and clean data
        cleaned_data = transform_channel_data(channel_data)

        # Debug counts (very important)
        st.write("Total Playlists:", len(cleaned_data["playlists"]))
        st.write("Total Videos:", len(cleaned_data["videos"]))
        st.write("Total Comments:", len(cleaned_data["comments"]))

        if not cleaned_data["videos"]:
            st.warning("No videos were extracted. Queries will return empty results.")
            return

        # Insert into database
        insert_channel(conn, cleaned_data["channel"])

        for playlist in cleaned_data["playlists"]:
            insert_playlist(conn, playlist)

        insert_videos(conn, cleaned_data["videos"])
        insert_comments(conn, cleaned_data["comments"])

        # REQUIRED for SQLite persistence
        conn.commit()

        # Verify insert (debug safety)
        video_check = pd.read_sql("SELECT COUNT(*) AS total FROM Video", conn)
        st.write("Videos currently in DB:", video_check["total"].iloc[0])

        st.success("Data fetched and stored successfully. You can now proceed to querying.")

        # Display results
        st.subheader("Channel Info")
        st.json(cleaned_data["channel"])

        st.subheader("Playlists")
        st.dataframe(pd.DataFrame(cleaned_data["playlists"]))

        st.subheader("Videos")
        st.dataframe(pd.DataFrame(cleaned_data["videos"]))

        st.subheader("Comments (showing up to 50)")
        st.dataframe(pd.DataFrame(cleaned_data["comments"]).head(50))

    except Exception as e:
        st.error(f"Error while processing data: {e}")

# Run when user clicks the button
if st.button("Fetch and Store Data"):
    if not channel_id.strip():
        st.warning("Please enter a valid YouTube Channel ID.")
    else:
        with st.spinner("Processing..."):
            fetch_and_store_data(youtube, conn, channel_id)
