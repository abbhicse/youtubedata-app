import streamlit as st
from database import create_tables, connect_to_db
from fetch import initialize_youtube_api

# Read API key securely from Streamlit Secrets
API_KEY = st.secrets["YOUTUBE_API_KEY"]

# Page title
st.title("App Initialization: API and Database Setup")

# Optional debug info
with st.expander("Show Loaded Configuration"):
    if API_KEY:
        st.write("API Key (masked):", f"{API_KEY[:4]}****")
    else:
        st.warning("API Key is not loaded.")
    st.write("Using SQLite database: youtube_data.db")

# Initialization logic
if st.button("Initialize API and Database"):
    # Initialize YouTube API
    if not API_KEY:
        st.error("API Key is missing. Please check your secrets configuration.")
        st.stop()

    try:
        youtube = initialize_youtube_api(API_KEY)
        st.session_state["API_KEY"] = API_KEY
        st.session_state["youtube_api"] = youtube
        st.success("YouTube API initialized successfully.")
    except Exception as e:
        st.error(f"Failed to initialize YouTube API: {e}")
        st.stop()

    # Connect to SQLite and create tables
    try:
        conn = connect_to_db()
        create_tables(conn)
        st.session_state["conn"] = conn
        st.success("SQLite database connected and tables created.")
    except Exception as e:
        st.error(f"Database setup failed: {e}")
        st.stop()

    st.success("Initialization complete. You can now proceed to the next step.")
