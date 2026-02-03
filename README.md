# **YouTube Data Harvesting and Warehousing using SQL and Streamlit**

## **Project Overview**
This project is a data analysis tool that allows users to fetch, store, and analyze data from YouTube channels. It uses the **YouTube Data API** to extract information such as channel details, videos, and comments, and stores this data in a **MySQL database**. The project also provides a user-friendly **Streamlit application** to view and analyze the stored data using SQL queries.

---

## **Features Implemented**
1. **YouTube API Integration**:
   - Fetch data for a YouTube channel by providing its Channel ID.
   - Collect metadata such as:
     - Channel Name, Subscriber Count, Total Videos, Total Views.
     - Video Details: Title, Views, Likes, Dislikes, Comments.
     - Comments on each video.

2. **Data Storage**:
   - Store fetched data in a **MySQL database** for long-term analysis.
   - Database schema includes three tables:
     - `Channel`: Stores channel-level data.
     - `Playllist`: Stores playlist-level data linked to channels.
     - `Video`: Stores video-level data linked to channels.
     - `Comment`: Stores comment-level data linked to videos.

3. **SQL Query Execution**:
   - Perform powerful SQL queries on the stored data, such as:
     1. Fetch all video names with their corresponding channel names.
     2. Find channels with the most number of videos and the video count.
     3. List the top 10 most-viewed videos with their respective channels.
     4. Count the number of comments on each video with their corresponding video names.
     5. Find videos with the highest likes and their channel names.
     6. Calculate total likes and dislikes for each video with their corresponding video names.
     7. Fetch total views for each channel with corresponding channel names.
     8. Identify channels that published videos in the year 2022.
     9. Calculate the average duration of videos for each channel with thier channel names.
     10. List the top 10 videos with the highest number of comments and thier corresponding channel names.

4. **User Interface with Streamlit**:
   - Interactive Streamlit app to:
     - Input Channel IDs.
     - View fetched data in a table format.
     - Execute SQL queries and display results.

---

## **Technologies Used**
- **Python**: Core programming language.
- **Streamlit**: For building the web interface.
- **YouTube Data API**: For fetching channel and video data.
- **MySQL**: For storing and querying data.
- **Pandas**: For data manipulation and analysis.

---

## **Project Structure**
Here’s how the project is organized:

```
YouTubeDataProject/
│
├── app.py               # Main Streamlit application
├── youtube_api.py        # Handles YouTube API integration
├── database.py           # Database connection and SQL operations
├── data_processing.py    # Data transformation logic
├── utils.py              # Utility functions
├── requirements.txt      # List of Python dependencies
└── README.md             # Project documentation (this file)
```

---

## **How to Set Up and Run the Project**
Follow these steps to set up and run the project:

### 1. **Clone the Repository**
```bash
git clone <repository-url>
cd YouTubeDataProject
```

### 2. **Set Up a Virtual Environment**
1. Create a virtual environment:
   ```bash
   python -m venv youtubedata
   ```
2. Run the following command to see your current execution policy:   
   ```bash
   Get-ExecutionPolicy
   ```
3. If it shows Restricted, Update the Execution Policy:
   ```bash
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   ```
4. Activate the virtual environment:
   - **Windows**:
     ```bash
     youtubedata\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source youtubedata/bin/activate
     ```

5. Install the required dependencies inside the virtual environment:
   ```bash
   pip install -r requirements.txt
   ```

6. Deactivate the virtual environment when done:
   ```bash
   deactivate
   ```

7. To ensure the virtual environment is ignored by Git:
   - Create a `.gitignore` file (if not present) in your project folder.
   - Add the following line to the `.gitignore` file:
     ```
     youtubedata/
     ```

### 3. **Set Up MySQL Database**
1. Install and set up MySQL on your system.
2. Create a new database named `youtube_data`.
3. Update the database credentials inside `.env` file:
   ```
   YOUTUBE_API_KEY=your_youtube_google_api__key
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=youtube_data
   ```

### 4. **Set Up YouTube Data API**
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the YouTube Data API.
3. Generate an API key and replace `YOUR_YOUTUBE_API_KEY` in the `app.py` file:
   ```python
   API_KEY = "YOUR_YOUTUBE_API_KEY"
   ```

### 5. **Run the Application**
Run the Streamlit application using the following command:
```bash
streamlit run app.py
```

This will open a web interface in your default browser.

---

## **Using the Application**
### Step 1: Input a Channel ID
- Enter a YouTube Channel ID in the input box and click "Fetch and Store Data".
- The app will fetch channel details, video information, and comments and store them in the database.

### Step 2: Execute SQL Queries
- Use the dropdown menu to select a query, such as:
  - Top 10 most viewed videos.
  - Channels with videos published in 2022.
  - Total likes and dislikes for each video.
- View the query results in a tabular format.

### Step 3: Analyze Data
- Explore the results directly in the app or extend the analysis using the database.

---

## **Example SQL Queries**
Here are examples of SQL queries used in the app:

1. **Names of all videos and their corresponding channels**:
   ```sql
   SELECT 
                Video.video_name AS video_name, 
                Channel.channel_name AS channel_name
            FROM 
                Video
            JOIN 
                Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN 
                Channel ON Playlist.channel_id = Channel.channel_id;
   ```

2. **Top 10 most-viewed videos**:
   ```sql
   SELECT 
                Video.video_name AS video_name, 
                Video.view_count AS view_count, 
                Channel.channel_name AS channel_name
            FROM 
                Video
            JOIN 
                Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN 
                Channel ON Playlist.channel_id = Channel.channel_id
            ORDER BY 
                Video.view_count DESC
            LIMIT 10;
   ```

3. **Channels that published videos in 2022**:
   ```sql
   SELECT DISTINCT 
                Channel.channel_name AS channel_name
            FROM 
                Video
            JOIN 
                Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN 
                Channel ON Playlist.channel_id = Channel.channel_id
            WHERE 
                YEAR(Video.published_date) = 2022;
   ```

---

## **Learning Outcomes**
This project helps you learn:
- API integration using Python.
- Building data-driven web applications using Streamlit.
- Database management with MySQL.
- Writing and executing SQL queries for data analysis.
- Organizing Python projects in a modular fashion.

---

## **Project Evaluation**
- **Modular Code**: Organized into functional modules (`youtube_api.py`, `database.py`, etc.).
- **Documentation**: Comprehensive `README.md` for easy understanding.
- **User-Friendly**: Streamlit interface for seamless interaction.
- **SQL Query Capability**: Predefined queries for quick insights.

---

## **Credits**
- **Streamlit Documentation**: [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- **YouTube Data API Documentation**: [YouTube API Guide](https://developers.google.com/youtube/v3/getting-started)

---