import streamlit as st

# Set page configuration
st.set_page_config(page_title="YouTube Data Analysis", layout="wide")

# Landing Page
st.title("YouTube Data Harvesting & Analysis")
st.write("Welcome! This application lets you:")

st.markdown("""
- **Initialize the App** – Set up API access and database connection.
- **Scrape Data** – Fetch YouTube channel data and store it in the database.
- **Query Database** – Analyze data through pre-built SQL queries.
""")

# Initialization checks
if "API_KEY" not in st.session_state or not st.session_state["API_KEY"]:
    st.warning("API Key is not set. Please go to the 'Initialization' page from the sidebar to enter it.")
    st.stop()

if "conn" not in st.session_state:
    st.warning("Database connection is missing. Please go to the 'Initialization' page to set it up.")
    st.stop()

st.success("Initialization complete. Use the sidebar to access other features.")

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.success("Use the sidebar to move between pages.")
