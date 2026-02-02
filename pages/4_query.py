import streamlit as st
import pandas as pd
from database import get_query_results

# Page title
st.title("Database Query Interface")

# Get DB connection
conn = st.session_state.get("conn")
if not conn:
    st.error("Database is not connected. Please run 'App Initialization' first.")
    st.stop()

# Available queries
query_options = {
    "What are the names of all the videos and their corresponding channels?": "video_channel_names",
    "Which channels have the most number of videos, and how many?": "most_videos_channels",
    "What are the top 10 most viewed videos and their respective channels?": "top_viewed_videos",
    "How many comments were made on each video, and what are their names?": "video_comment_counts",
    "Which videos have the highest likes, and what are their channel names?": "most_liked_videos",
    "What is the total number of likes and dislikes for each video?": "video_likes_dislikes",
    "What is the total number of views for each channel?": "channel_total_views",
    "Which channels have published videos in 2022?": "channels_published_2022",
    "What is the average duration of all videos in each channel?": "average_video_duration",
    "Which videos have the highest number of comments, and what are their channels?": "most_commented_videos"
}

# Query selector
query_label = st.selectbox("Select a query to execute", list(query_options.keys()))
query_type = query_options[query_label]

# Execute on click
if st.button("Run Query"):
    with st.spinner("Running the selected query..."):
        try:
            results = get_query_results(conn, query_type)

            st.subheader(f"Results for: {query_label}")

            if results:
                df = pd.DataFrame(results)
                st.write(f"Total rows returned: {len(df)}")
                st.dataframe(df)

                # CSV export
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name=f"{query_type}_results.csv",
                    mime="text/csv"
                )
            else:
                st.info("No results found.")

        except Exception as e:
            st.error(f"An error occurred while executing the query: {e}")
