import streamlit as st

# Set page configuration
st.set_page_config(page_title="YouTube Data Analysis", layout="wide")

# Landing Page
st.title("YouTube Data Harvesting & Analysis")
st.write("Welcome! This application lets you:")

st.markdown("""
- **Initialize the App** – Set up API access and database connection.
- **Scrap Data** – Fetch YouTube channel data and store it in the database.
- **Query Database** – Analyze data through pre-built SQL queries.
""")

st.info("Please start by running the **'Initialization'** page from the sidebar to set up the system.")

st.sidebar.title(" Navigation")
st.sidebar.success("Use the sidebar to move between pages.")
