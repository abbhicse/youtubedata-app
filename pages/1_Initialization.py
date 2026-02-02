import streamlit as st
from database import create_database, create_tables, connect_to_db
from fetch import initialize_youtube_api
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Extract API key and DB credentials
API_KEY = os.getenv("YOUTUBE_API_KEY")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# Page title
st.title("App Initialization: API and Database Setup")

# Debug section (optional)
with st.expander("Show Loaded Configuration"):
    if API_KEY:
        st.write("API Key (masked):", f"{API_KEY[:4]}****")
    else:
        st.warning("API Key is not loaded from environment.")
    st.write("Database Configuration:", DB_CONFIG)

# Initialization logic
if st.button("Initialize API and Database"):
    # Initialize YouTube API
    if not API_KEY:
        st.error("API Key is missing. Please check your environment configuration.")
        st.stop()

    try:
        youtube = initialize_youtube_api(API_KEY)
        st.session_state["API_KEY"] = API_KEY
        st.session_state["youtube_api"] = youtube
        st.success("YouTube API initialized successfully.")
    except Exception as e:
        st.error(f"Failed to initialize YouTube API: {e}")
        st.stop()

    # Connect to database
    try:
        conn = connect_to_db(
            DB_CONFIG["host"],
            DB_CONFIG["user"],
            DB_CONFIG["password"]
        )

        if conn:
            create_database(conn, DB_CONFIG["database"])
            st.success("Database created or verified.")

            conn.database = DB_CONFIG["database"]
            create_tables(conn)
            st.success("Tables created successfully.")

            st.session_state["conn"] = conn
        else:
            st.error("Could not connect to the MySQL server.")
            st.stop()
    except Exception as e:
        st.error(f"Database setup failed: {e}")
        st.stop()

    st.success("Initialization complete. You can now proceed to the next step.")
