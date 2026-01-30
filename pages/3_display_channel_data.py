import streamlit as st
import pandas as pd
from database import execute_query

st.title("View Stored YouTube Channel Data")

# Check database connection
conn = st.session_state.get("db_connection")
if not conn:
    st.error("Database connection is missing. Please run 'Initialization' first.")
    st.stop()

# Step 1: Load available channels
channels = execute_query(conn, "SELECT channel_id, channel_name FROM Channel")
if not channels:
    st.warning("No channels found in database. Please fetch and store channel data first.")
    st.stop()

channel_options = {f"{c['channel_name']} ({c['channel_id']})": c["channel_id"] for c in channels}
selected_display = st.selectbox("Select a Channel to Display:", list(channel_options.keys()))
selected_channel_id = channel_options[selected_display]

# Step 2: Show button to display data
if st.button("Display"):
    with st.spinner("Fetching stored data from database..."):

        # Channel Info
        st.subheader("Channel Info")
        channel_info = pd.DataFrame(execute_query(conn, f"""
            SELECT * FROM Channel WHERE channel_id = '{selected_channel_id}'
        """))
        st.dataframe(channel_info)

        # Playlists
        st.subheader("Playlists")
        playlist_data = pd.DataFrame(execute_query(conn, f"""
            SELECT * FROM Playlist WHERE channel_id = '{selected_channel_id}'
        """))
        st.dataframe(playlist_data)

        # Videos
        st.subheader("Videos")
        video_data = pd.DataFrame(execute_query(conn, f"""
            SELECT * FROM Video
            WHERE playlist_id IN (
                SELECT playlist_id FROM Playlist WHERE channel_id = '{selected_channel_id}'
            )
        """))
        st.dataframe(video_data)

        # Comments (limit to 100 for performance)
        st.subheader("Comments")
        comment_data = pd.DataFrame(execute_query(conn, f"""
            SELECT * FROM Comment
            WHERE video_id IN (
                SELECT video_id FROM Video
                WHERE playlist_id IN (
                    SELECT playlist_id FROM Playlist WHERE channel_id = '{selected_channel_id}'
                )
            )
            LIMIT 100
        """))
        st.dataframe(comment_data)

        st.success("Data successfully loaded from database.")
