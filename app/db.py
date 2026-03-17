import mysql.connector
import os
import time

# from dotenv import load_dotenv
# load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "rootpassword"),
    "database": os.getenv("DB_NAME", "met_art"),
    "port": int(os.getenv("DB_PORT", 3306)),
}


def env_flag(name, default=False):

    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


# def get_connection():

#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="rootpassword",
#         database="met_art"
#     )

def get_connection():

    return mysql.connector.connect(**DB_CONFIG)


def get_server_connection():

    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"],
    )


def wait_for_database(max_attempts=120, delay_seconds=2):

    last_error = None

    for _ in range(max_attempts):
        try:
            conn = get_server_connection()
            conn.close()
            return
        except mysql.connector.Error as error:
            last_error = error
            time.sleep(delay_seconds)

    raise last_error


def initialize_database(create_database_if_missing=False):

    if create_database_if_missing:
        server_conn = get_server_connection()
        server_cursor = server_conn.cursor()

        server_cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}"
        )

        server_cursor.close()
        server_conn.close()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS artists (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS artworks (
            id INT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            artist_id INT NOT NULL,
            year INT NULL,
            century INT NULL,
            department VARCHAR(255) NULL,
            image_url TEXT NULL,
            CONSTRAINT fk_artworks_artist
                FOREIGN KEY (artist_id) REFERENCES artists(id)
        )
        """
    )

    conn.commit()
    cursor.close()
    conn.close()


def count_artworks():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM artworks")
    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count

def get_or_create_artist(name):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM artists WHERE name = %s",
        (name,)
    )

    result = cursor.fetchone()

    if result:

        cursor.close()
        conn.close()

        return result[0]

    cursor.execute(
        "INSERT INTO artists (name) VALUES (%s)",
        (name,)
    )

    conn.commit()

    artist_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return artist_id


def insert_artwork(record):

    required_fields = ["id", "title", "artist", "year", "century", "department", "image_url"]

    for field in required_fields:
        if field not in record:
            return  False # Skip if any required field is missing

    conn = get_connection()
    cursor = conn.cursor()
    artist_id = get_or_create_artist(record["artist"])

    cursor.execute(
        """
        INSERT IGNORE INTO artworks
        (id, title, artist_id, year, century, department, image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            record["id"],
            record["title"],
            artist_id,
            record["year"],
            record["century"],
            record["department"],
            record["image_url"]
        )
    )

    conn.commit()
    inserted = cursor.rowcount > 0

    cursor.close()
    conn.close()
    return inserted


def get_department_distribution():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT department, COUNT(*) AS count
    FROM artworks
    GROUP BY department
    ORDER BY count DESC
    """)

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

def get_century_distribution():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT century, COUNT(*) AS count
    FROM artworks
    GROUP BY century
    ORDER BY count DESC
    """)

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def get_timeline_distribution():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT year, COUNT(*) AS count
        FROM artworks
        WHERE year IS NOT NULL
        GROUP BY year
        ORDER BY year
        """
    )

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results
