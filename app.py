import streamlit as st

# Set page configuration
st.set_page_config(page_title="YouTube Data Analysis", layout="wide")

# Landing Page
st.title("YouTube Data Harvesting and Analysis")
st.markdown("""
Welcome to the YouTube Data Harvesting App. This application allows you to:

- **Initialize the App** – Set up YouTube API and database (SQLite).
- **Fetch and Store Data** – Retrieve channel data and store it.
- **Explore Stored Data** – View channel, video, and comment details.
- **Run SQL Queries** – Analyze YouTube data using predefined queries.
""")

# Initialization checks
if "API_KEY" not in st.session_state or not st.session_state["API_KEY"]:
    st.warning("API Key is not set. Please go to the 'App Initialization' page to configure it.")
    st.stop()

if "youtube_api" not in st.session_state:
    st.warning("YouTube API is not initialized. Please complete initialization first.")
    st.stop()

if "conn" not in st.session_state:
    st.warning("Database connection is missing. Please go to the 'App Initialization' page to connect to SQLite.")
    st.stop()

st.success("Initialization complete. Use the sidebar to access other features.")

# Optional: Quick navigation button
st.markdown("### Jump to next step:")
if st.button("Go to 'Fetch and Store Data' page"):
    st.switch_page("pages/2_Fetch_and_Store_Data.py")  # Update this if your file name differs

# Sidebar
st.sidebar.title("Navigation")
