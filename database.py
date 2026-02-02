import sqlite3
import logging
import os

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/database.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

DB_PATH = "youtube_data.db"

# ---------- CONNECTION ----------
def connect_to_db():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        logging.info("SQLite connection successful.")
        return conn
    except Exception as e:
        logging.error(f"SQLite connection failed: {e}")
        raise

# ---------- TABLE CREATION ----------
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
                playlist_name TEXT
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
                caption TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Comment (
                comment_id TEXT PRIMARY KEY,
                video_id TEXT,
                comment_text TEXT,
                comment_author TEXT,
                comment_published_date TEXT
            );
        """)

        conn.commit()
        logging.info("All SQLite tables created successfully.")
    except Exception as e:
        logging.error(f"Table creation failed: {e}")
        raise
    finally:
        cursor.close()

# ---------- INSERT FUNCTIONS ----------
def insert_channel(conn, channel):
    query = """
        INSERT INTO Channel VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(channel_id) DO UPDATE SET
            channel_name = excluded.channel_name,
            channel_views = excluded.channel_views,
            channel_status = excluded.channel_status;
    """
    values = (
        channel["channel_id"],
        channel["channel_name"],
        channel["channel_type"],
        channel["channel_views"],
        channel["channel_description"],
        channel["channel_status"]
    )
    _execute_single(conn, query, values, "channel")

def insert_playlist(conn, playlist):
    query = """
        INSERT INTO Playlist VALUES (?, ?, ?)
        ON CONFLICT(playlist_id) DO UPDATE SET
            playlist_name = excluded.playlist_name;
    """
    values = (
        playlist["playlist_id"],
        playlist["channel_id"],
        playlist["playlist_name"]
    )
    _execute_single(conn, query, values, "playlist")

def insert_videos(conn, videos):
    query = """
        INSERT INTO Video VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(video_id) DO UPDATE SET
            view_count = excluded.view_count,
            like_count = excluded.like_count,
            dislike_count = excluded.dislike_count,
            comment_count = excluded.comment_count;
    """
    values_list = [
        (
            v["video_id"], v["playlist_id"], v["video_name"], v["video_description"],
            v["published_date"], v["view_count"], v["like_count"], v["dislike_count"],
            v["favorite_count"], v["comment_count"], v["duration"],
            v["thumbnail"], v["caption"]
        ) for v in videos
    ]
    _execute_batch(conn, query, values_list, "videos")

def insert_comments(conn, comments):
    query = """
        INSERT INTO Comment VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(comment_id) DO UPDATE SET
            comment_text = excluded.comment_text;
    """
    values_list = [
        (
            c["comment_id"], c["video_id"], c["comment_text"],
            c["comment_author"], c["comment_published_date"]
        ) for c in comments
    ]
    _execute_batch(conn, query, values_list, "comments")

# ---------- HELPERS ----------
def _execute_single(conn, query, values, label):
    cursor = conn.cursor()
    try:
        cursor.execute(query, values)
        conn.commit()
        logging.info(f"{label.capitalize()} inserted.")
    except Exception as e:
        logging.error(f"Insert {label} failed: {e}")
        raise
    finally:
        cursor.close()

def _execute_batch(conn, query, values_list, label):
    cursor = conn.cursor()
    try:
        cursor.executemany(query, values_list)
        conn.commit()
        logging.info(f"{label.capitalize()} batch inserted: {len(values_list)} rows.")
    except Exception as e:
        logging.error(f"Batch insert {label} failed: {e}")
        raise
    finally:
        cursor.close()

# ---------- QUERY EXECUTION ----------
def execute_query(conn, query):
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Query failed: {e}")
        raise
    finally:
        cursor.close()

def get_query_results(conn, query_type):
    queries = {
        "video_channel_names": """
            SELECT Video.video_name, Channel.channel_name
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id;
        """,
        "most_videos_channels": """
            SELECT Channel.channel_name, COUNT(Video.video_id) AS video_count
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
        "channels_published_2022": """
            SELECT DISTINCT Channel.channel_name
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            WHERE substr(Video.published_date, 1, 4) = '2022';
        """
    }

    if query_type not in queries:
        raise ValueError("Invalid query type")

    return execute_query(conn, queries[query_type])
