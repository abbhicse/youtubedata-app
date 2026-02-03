import sqlite3 as sql
import logging
import os

print("LOADED DATABASE.PY VERSION: SQLITE + PARAMS")
# Setup logs
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/database.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def connect_to_db(db_path="youtube_data.db"):
    try:
        conn = sql.connect(db_path, detect_types=sql.PARSE_DECLTYPES | sql.PARSE_COLNAMES, check_same_thread=False)
        conn.row_factory = sql.Row  # For dict-like access
        logging.info("✅ SQLite connection successful.")
        return conn
    except Exception as e:
        logging.error(f"❌ Failed to connect to SQLite: {e}")
        raise

def create_database(conn, db_name):
    logging.info("SQLite uses file-based DB. No explicit CREATE DATABASE needed.")

def create_tables(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Channel (
                channel_id TEXT PRIMARY KEY,
                channel_name TEXT,
                channel_type TEXT,
                channel_views INTEGER,
                channel_description TEXT,
                channel_status TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Playlist (
                playlist_id TEXT PRIMARY KEY,
                channel_id TEXT,
                playlist_name TEXT,
                FOREIGN KEY (channel_id) REFERENCES Channel (channel_id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Video (
                video_id TEXT PRIMARY KEY,
                playlist_id TEXT,
                video_name TEXT,
                video_description TEXT,
                published_date TEXT,
                view_count INTEGER,
                like_count INTEGER,
                dislike_count INTEGER,
                favorite_count INTEGER,
                comment_count INTEGER,
                duration INTEGER,
                thumbnail TEXT,
                caption TEXT,
                FOREIGN KEY (playlist_id) REFERENCES Playlist (playlist_id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Comment (
                comment_id TEXT PRIMARY KEY,
                video_id TEXT,
                comment_text TEXT,
                comment_author TEXT,
                comment_published_date TEXT,
                FOREIGN KEY (video_id) REFERENCES Video (video_id)
            );
        """)
        conn.commit()
        logging.info("✅ Tables created successfully.")
    finally:
        cursor.close()

def insert_channel(conn, channel):
    cursor = conn.cursor()
    query = """
        INSERT OR REPLACE INTO Channel (
            channel_id, channel_name, channel_type, channel_views, channel_description, channel_status
        ) VALUES (?, ?, ?, ?, ?, ?)
    """
    values = (
        channel["channel_id"],
        channel["channel_name"],
        channel["channel_type"],
        channel["channel_views"],
        channel["channel_description"],
        channel["channel_status"]
    )
    cursor.execute(query, values)
    conn.commit()
    cursor.close()

def insert_playlist(conn, playlist):
    cursor = conn.cursor()
    query = """
        INSERT OR REPLACE INTO Playlist (playlist_id, channel_id, playlist_name)
        VALUES (?, ?, ?)
    """
    values = (
        playlist["playlist_id"],
        playlist["channel_id"],
        playlist["playlist_name"]
    )
    cursor.execute(query, values)
    conn.commit()
    cursor.close()

def insert_videos(conn, videos):
    cursor = conn.cursor()
    query = """
        INSERT OR REPLACE INTO Video (
            video_id, playlist_id, video_name, video_description, published_date,
            view_count, like_count, dislike_count, favorite_count, comment_count,
            duration, thumbnail, caption
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    for video in videos:
        values = (
            video["video_id"],
            video["playlist_id"],
            video["video_name"],
            video["video_description"],
            str(video["published_date"]),
            video["view_count"],
            video["like_count"],
            video["dislike_count"],
            video["favorite_count"],
            video["comment_count"],
            video["duration"],
            video["thumbnail"],
            video["caption"]
        )
        cursor.execute(query, values)
    conn.commit()
    cursor.close()

def insert_comments(conn, comments):
    cursor = conn.cursor()
    query = """
        INSERT OR REPLACE INTO Comment (
            comment_id, video_id, comment_text, comment_author, comment_published_date
        ) VALUES (?, ?, ?, ?, ?)
    """
    for comment in comments:
        values = (
            comment["comment_id"],
            comment["video_id"],
            comment["comment_text"],
            comment["comment_author"],
            str(comment["comment_published_date"])
        )
        cursor.execute(query, values)
    conn.commit()
    cursor.close()

def execute_query(conn, query, params=()):
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        cursor.close()

def get_query_results(conn, query_type):
    queries = {
        "video_channel_names": """
            SELECT Video.video_name AS video_name, Channel.channel_name AS channel_name
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id;
        """,
        "most_videos_channels": """
            SELECT Channel.channel_name AS channel_name, COUNT(Video.video_id) AS video_count
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            GROUP BY Channel.channel_name
            ORDER BY video_count DESC
            LIMIT 1;
        """,
        "top_viewed_videos": """
            SELECT Video.video_name, Video.view_count, Channel.channel_name
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            ORDER BY Video.view_count DESC
            LIMIT 10;
        """,
        "video_comment_counts": """
            SELECT video_name, comment_count FROM Video;
        """,
        "most_liked_videos": """
            SELECT Video.video_name, Video.like_count, Channel.channel_name
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            ORDER BY like_count DESC
            LIMIT 10;
        """,
        "video_likes_dislikes": """
            SELECT video_name, like_count, dislike_count FROM Video;
        """,
        "channel_total_views": """
            SELECT channel_name, channel_views AS total_views FROM Channel;
        """,
        "channels_published_2022": """
            SELECT DISTINCT Channel.channel_name
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            WHERE strftime('%Y', published_date) = '2022';
        """,
        "average_video_duration": """
            SELECT Channel.channel_name, ROUND(AVG(Video.duration)/60, 2) AS avg_duration_minutes
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            GROUP BY Channel.channel_name;
        """,
        "most_commented_videos": """
            SELECT Video.video_name, Video.comment_count, Channel.channel_name
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            ORDER BY comment_count DESC
            LIMIT 10;
        """
    }

    query = queries.get(query_type, "")
    if not query:
        raise ValueError(f"Invalid query type: {query_type}")

    return execute_query(conn, query)
