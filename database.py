import mysql.connector as sql
import logging
import os

# Setup logs
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/database.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def connect_to_db(host, user, password, database=None):
    print(f"Connecting to MySQL server... host={host}, user={user}, database={database}")
    logging.info(f"Connecting to MySQL server with host={host}, user={user}, database={database}")

    try:
        mydb = sql.connect(
            host=host,
            user=user,
            password=password,
            database=database if database else None,
            use_pure=True
        )
        print("MySQL connection successful.")
        logging.info("MySQL connection successful.")
        return mydb
    except Exception as e:
        print(f"Failed to connect to MySQL: {e}")
        logging.error(f"Failed to connect to MySQL: {e}")
        raise

def create_database(connection, database_name):
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    cursor.close()
    print(f"Database '{database_name}' created or verified.")
    logging.info(f"Database '{database_name}' created or verified.")

def create_tables(connection):
    cursor = connection.cursor()
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
        connection.commit()
        print("All tables created successfully.")
        logging.info("All tables created successfully.")
    except Exception as e:
        print(f"Table creation error: {e}")
        logging.error(f"Table creation error: {e}")
        raise
    finally:
        cursor.close()

def insert_channel(connection, channel):
    cursor = connection.cursor()
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
    try:
        cursor.execute(query, values)
        connection.commit()
        print("Channel data inserted.")
        logging.info("Channel data inserted.")
    except Exception as e:
        print(f"Failed to insert channel: {e}")
        logging.error(f"Failed to insert channel: {e}")
        raise
    finally:
        cursor.close()

def insert_playlist(connection, playlist):
    cursor = connection.cursor()
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
    try:
        cursor.execute(query, values)
        connection.commit()
        print("Playlist data inserted.")
        logging.info("Playlist data inserted.")
    except Exception as e:
        print(f"Failed to insert playlist: {e}")
        logging.error(f"Failed to insert playlist: {e}")
        raise
    finally:
        cursor.close()

def insert_videos(connection, videos):
    cursor = connection.cursor()
    query = """
        INSERT INTO Video (video_id, playlist_id, video_name, video_description, published_date, 
                           view_count, like_count, dislike_count, favorite_count, comment_count, duration, thumbnail, caption)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        view_count = VALUES(view_count), 
        like_count = VALUES(like_count), 
        dislike_count = VALUES(dislike_count), 
        comment_count = VALUES(comment_count);
    """
    try:
        for video in videos:
            values = (
                video["video_id"],
                video["playlist_id"],
                video["video_name"],
                video["video_description"],
                video["published_date"],
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
        connection.commit()
        print("Video data inserted.")
        logging.info("Video data inserted.")
    except Exception as e:
        print(f"Failed to insert videos: {e}")
        logging.error(f"Failed to insert videos: {e}")
        raise
    finally:
        cursor.close()

def insert_comments(connection, comments):
    cursor = connection.cursor()
    query = """
        INSERT INTO Comment (comment_id, video_id, comment_text, comment_author, comment_published_date)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        comment_text = VALUES(comment_text);
    """
    try:
        for comment in comments:
            values = (
                comment["comment_id"],
                comment["video_id"],
                comment["comment_text"],
                comment["comment_author"],
                comment["comment_published_date"]
            )
            cursor.execute(query, values)
        connection.commit()
        print("Comment data inserted.")
        logging.info("Comment data inserted.")
    except Exception as e:
        print(f"Failed to insert comments: {e}")
        logging.error(f"Failed to insert comments: {e}")
        raise
    finally:
        cursor.close()

def execute_query(connection, query):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()

def get_query_results(connection, query_type):
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
            SELECT Video.video_name AS video_name, Video.view_count AS view_count, Channel.channel_name AS channel_name
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            ORDER BY Video.view_count DESC
            LIMIT 10;
        """,
        "video_comment_counts": """
            SELECT Video.video_name AS video_name, Video.comment_count AS comment_count FROM Video;
        """,
        "most_liked_videos": """
            SELECT Video.video_name AS video_name, Video.like_count AS like_count, Channel.channel_name AS channel_name
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            ORDER BY Video.like_count DESC
            LIMIT 10;
        """,
        "video_likes_dislikes": """
            SELECT Video.video_name AS video_name, Video.like_count AS like_count, Video.dislike_count AS dislike_count
            FROM Video;
        """,
        "channel_total_views": """
            SELECT Channel.channel_name AS channel_name, Channel.channel_views AS total_views FROM Channel;
        """,
        "channels_published_2022": """
            SELECT DISTINCT Channel.channel_name AS channel_name
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            WHERE YEAR(Video.published_date) = 2022;
        """,
        "average_video_duration": """
            SELECT Channel.channel_name AS channel_name, AVG(Video.duration) / 60 AS avg_duration_minutes
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            GROUP BY Channel.channel_name;
        """,
        "most_commented_videos": """
            SELECT Video.video_name AS video_name, Video.comment_count AS comment_count, Channel.channel_name AS channel_name
            FROM Video
            JOIN Playlist ON Video.playlist_id = Playlist.playlist_id
            JOIN Channel ON Playlist.channel_id = Channel.channel_id
            ORDER BY Video.comment_count DESC
            LIMIT 10;
        """
    }

    query = queries.get(query_type, "")
    if not query:
        raise ValueError(f"Invalid query type: {query_type}")
    
    return execute_query(connection, query)
