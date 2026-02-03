import streamlit as st
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
from database import execute_query

# Page title
st.title("View Stored YouTube Channel Data")

# Get database connection
conn = st.session_state.get("conn")
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

# Display utility function
def display_query_result(title, query, params=None, allow_download=True):
    try:
        result = pd.DataFrame(execute_query(conn, query, params or ()))
        st.subheader(title)

        if result.empty:
            st.write("No data available.")
        else:
            st.dataframe(result)

            if allow_download:
                csv = result.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"Download {title} as CSV",
                    data=csv,
                    file_name=f"{title.replace(' ', '_').lower()}.csv",
                    mime="text/csv"
                )
        return result
    except Exception as e:
        st.error(f"Failed to load {title}: {e}")
        return pd.DataFrame()

# Store results for zip
results_for_zip = {}

# Display on button click
if st.button("Display"):
    with st.spinner("Fetching stored data from the database..."):

        # Channel Info
        df_channel = display_query_result("Channel Info", """
            SELECT * FROM Channel WHERE channel_id = ?
        """, (selected_channel_id,))
        results_for_zip["channel_info.csv"] = df_channel

        # Playlists
        df_playlist = display_query_result("Playlists", """
            SELECT * FROM Playlist WHERE channel_id = ?
        """, (selected_channel_id,))
        results_for_zip["playlists.csv"] = df_playlist

        # Videos (no filters)
        df_videos = display_query_result("Videos", """
            SELECT * FROM Video
            WHERE playlist_id IN (
                SELECT playlist_id FROM Playlist WHERE channel_id = ?
            )
        """, (selected_channel_id,))
        results_for_zip["videos.csv"] = df_videos

        # Comments (limited)
        df_comments = display_query_result("Comments (limited to 100)", """
            SELECT * FROM Comment
            WHERE video_id IN (
                SELECT video_id FROM Video
                WHERE playlist_id IN (
                    SELECT playlist_id FROM Playlist WHERE channel_id = ?
                )
            )
            LIMIT 100
        """, (selected_channel_id,))
        results_for_zip["comments.csv"] = df_comments

        # Export all as ZIP
        st.markdown("### Download All as ZIP")
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "w") as zip_file:
            for name, df in results_for_zip.items():
                if not df.empty:
                    csv_bytes = df.to_csv(index=False).encode("utf-8")
                    zip_file.writestr(name, csv_bytes)

        st.download_button(
            label="Download All Data as ZIP",
            data=zip_buffer.getvalue(),
            file_name="channel_data_export.zip",
            mime="application/zip"
        )

        st.success("Data successfully loaded and ready for export.")
