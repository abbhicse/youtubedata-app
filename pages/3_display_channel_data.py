import streamlit as st
import pandas as pd
from database import execute_query

# Page title
st.title("View Stored YouTube Channel Data")

# Get database connection
conn = st.session_state.get("conn")  # Use consistent session key
if not conn:
    st.error("Database connection is missing. Please run 'Initialization' first.")
    st.stop()

# Step 1: Load available channels
channels = execute_query(conn, "SELECT channel_id, channel_name FROM Channel")

if not channels:
    st.warning("No channels found in the database. Please fetch and store channel data first.")
    st.stop()

# Channel selection
channel_options = {f"{c['channel_name']} ({c['channel_id']})": c["channel_id"] for c in channels}
selected_display = st.selectbox("Select a Channel to Display:", list(channel_options.keys()))
selected_channel_id = channel_options[selected_display]

# Step 2: Display data on button click
if st.button("Display"):
    with st.spinner("Fetching stored data from the database..."):

        def display_query_result(title, query):
            result = pd.DataFrame(execute_query(conn, query))
            st.subheader(title)
            if result.empty:
                st.write("No data available.")
            else:
                st.dataframe(result)

        display_query_result("Channel Info", f"""
            SELECT * FROM Channel WHERE channel_id = %s
        """, )

        display_query_result("Playlists", f"""
            SELECT * FROM Playlist WHERE channel_id = %s
        """)

        display_query_result("Videos", f"""
            SELECT * FROM Video
            WHERE playlist_id IN (
                SELECT playlist_id FROM Playlist WHERE channel_id = %s
            )
        """)

        display_query_result("Comments (limited to 100)", f"""
            SELECT * FROM Comment
            WHERE video_id IN (
                SELECT video_id FROM Video
                WHERE playlist_id IN (
                    SELECT playlist_id FROM Playlist WHERE channel_id = %s
                )
            )
            LIMIT 100
        """)

        st.success("Data successfully loaded.")

