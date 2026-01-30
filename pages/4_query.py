import streamlit as st
from database import get_query_results

st.title("Database Query Interface")

# Use stored DB connection from session state
conn = st.session_state.get("db_connection")

if not conn:
    st.error("Database is not connected. Please run 'App Initialization' first.")

# Query Selection
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
query_label = st.selectbox("Select a query to execute", list(query_options.keys()))
query_type = query_options[query_label]

def execute_query(conn, query_type):
    """Execute the selected query and display results."""
    try:
        results = get_query_results(conn, query_type)
        st.write(f"Results for: *{query_type}*")
        if results:
            st.dataframe(results)
        else:
            st.info("No results found.")
    except Exception as e:
        st.error(f"Query execution error: {e}")

if st.button("Run Query"):
    execute_query(conn, query_type)
