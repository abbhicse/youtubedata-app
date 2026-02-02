import mysql.connector as sql
import logging
import os

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/database.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def connect_to_db(host, user, password, database=None):
    logging.info(f"Connecting to MySQL server at {host}, user={user}, database={database}")
    try:
        conn = sql.connect(
            host=host,
            user=user,
            password=password,
            database=database if database else None,
            use_pure=True
        )
        conn.ping(reconnect=True, attempts=3, delay=2)
        logging.info("MySQL connection successful.")
        return conn
    except Exception as e:
        logging.error(f"MySQL connection failed: {e}")
        raise

def create_database(conn, database_name):
    try:
        cursor = conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}`")
        logging.info(f"Database '{database_name}' created or verified.")
    except Exception as e:
        logging.error(f"Failed to create database '{database_name}': {e}")
        raise
    finally:
        cursor.close()

def create_tables(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Channel (
                channel_id VARCHAR(255) PRIMARY KEY,
                channel_name VARCHAR(255),
                channel_type VARCHAR(255),
                channel_views INT,
                channel_description TEXT,
                channel_status VARCHAR(255)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Playlist (
                playlist_id VARCHAR(255) PRIMARY KEY,
                channel_id VARCHAR(255),
                playlist_name VARCHAR(255),
                FOREIGN KEY (channel_id) REFERENCES Channel (channel_id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Video (
                video_id VARCHAR(255) PRIMARY KEY,
                playlist_id VARCHAR(255),
                video_name VARCHAR(255),
                video_description TEXT,
                published_date DATETIME,
                view_count INT,
                like_count INT,
                dislike_count INT,
                favorite_count INT,
                comment_count INT,
                duration INT,
                thumbnail VARCHAR(255),
                caption VARCHAR(255),
                FOREIGN KEY (playlist_id) REFERENCES Playlist (playlist_id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Comment (
                comment_id VARCHAR(255) PRIMARY KEY,
                video_id VARCHAR(255),
                comment_text TEXT,
                comment_author VARCHAR(255),
                comment_published_date DATETIME,
                FOREIGN KEY (video_id) REFERENCES Video (video_id)
            );
        """)
        conn.commit()
        logging.info("All tables created successfully.")
    except Exception as e:
        logging.error(f"Error during table creation: {e}")
        raise
    finally:
        cursor.close()

def insert_channel(conn, channel):
    query = """
        INSERT INTO Channel (channel_id, channel_name, channel_type, channel_views, channel_description, channel_status)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            channel_name = VALUES(channel_name),
            channel_views = VALUES(channel_views),
            channel_status = VALUES(channel_status);
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
        INSERT INTO Playlist (playlist_id, channel_id, playlist_name)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            playlist_name = VALUES(playlist_name);
    """
    values = (
        playlist["playlist_id"],
        playlist["channel_id"],
        playlist["playlist_name"]
    )
    _execute_single(conn, query, values, "playlist")

def insert_videos(conn, videos):
    query = """
        INSERT INTO Video (video_id, playlist_id, video_name, video_description, published_date, 
                           view_count, like_count, dislike_count, favorite_count, comment_count,
                           duration, thumbnail, caption)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            view_count = VALUES(view_count),
            like_count = VALUES(like_count),
            dislike_count = VALUES(dislike_count),
            comment_count = VALUES(comment_count);
    """
    values_list = [
        (
            v["video_id"], v["playlist_id"], v["video_name"], v["video_description"], v["published_date"],
            v["view_count"], v["like_count"], v["dislike_count"], v["favorite_count"],
            v["comment_count"], v["duration"], v["thumbnail"], v["caption"]
        ) for v in videos
    ]
    _execute_batch(conn, query, values_list, "videos")

def insert_comments(conn, comments):
    query = """
        INSERT INTO Comment (comment_id, video_id, comment_text, comment_author, comment_published_date)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            comment_text = VALUES(comment_text);
    """
    values_list = [
        (
            c["comment_id"], c["video_id"], c["comment_text"],
            c["comment_author"], c["comment_published_date"]
        ) for c in comments
    ]
    _execute_batch(conn, query, values_list, "comments")

def _execute_single(conn, query, values, label):
    cursor = conn.cursor()
    try:
        cursor.execute(query, values)
        conn.commit()
        logging.info(f"{label.capitalize()} data inserted.")
    except Exception as e:
        logging.error(f"Failed to insert {label}: {e}")
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
        logging.error(f"Failed to insert {label} batch: {e}")
        raise
    finally:
        cursor.close()

def execute_query(conn, query):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        logging.error(f"Query execution failed: {e}")
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
        "video_comment_counts": """
            SELECT video_name, comment_count FROM Video;
        """,
        "most_liked_videos": """
            SELECT Video.video_name, Video.like_count, Channel.channel_name
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            ORDER BY Video.like_count DESC
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
            WHERE YEAR(Video.published_date) = 2022;
        """,
        "average_video_duration": """
            SELECT Channel.channel_name, ROUND(AVG(Video.duration) / 60, 2) AS avg_duration_minutes
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
            ORDER BY Video.comment_count DESC
            LIMIT 10;
        """
    }

    query = queries.get(query_type)
    if not query:
        logging.error(f"Invalid query type requested: {query_type}")
        raise ValueError(f"Invalid query type: {query_type}")

    logging.info(f"Executing query: {query_type}")
    return execute_query(conn, query)
