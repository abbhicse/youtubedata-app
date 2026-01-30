import streamlit as st
from database import create_database, create_tables, connect_to_db
from fetch import initialize_youtube_api
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# Page title
st.title("App Initialization: API & Database Setup")

# Display current config (optional for debug)
with st.expander("Debug: Show Loaded Configuration"):
    st.write("API Key (masked):", f"{API_KEY[:4]}****")
    st.write("DB Config:", DB_CONFIG)

# Initialize button
if st.button("Initialize API & Database"):
    try:
        # Initialize YouTube API
        youtube = initialize_youtube_api(API_KEY)
        st.session_state["youtube_api"] = youtube
        st.success("YouTube API initialized successfully.")
    except Exception as e:
        st.error(f"Failed to initialize YouTube API: {e}")
        st.stop()

    try:
        # Connect to MySQL server
        conn = connect_to_db(DB_CONFIG["host"], DB_CONFIG["user"], DB_CONFIG["password"])
        if conn:
            create_database(conn, DB_CONFIG["database"])
            st.success("Database created or verified.")

            conn.database = DB_CONFIG["database"]
            create_tables(conn)
            st.success("Tables created successfully.")

            # Save to session for future pages
            st.session_state["db_connection"] = conn
        else:
            st.error("Could not connect to MySQL server.")
            st.stop()
    except Exception as e:
        st.error(f"Database setup failed: {e}")
        st.stop()

    st.success("Initialization complete! Now proceed to 'Scrap Data'.")
    st.balloons()
