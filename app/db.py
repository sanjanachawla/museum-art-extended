import mysql.connector


def get_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootpassword",
        database="met_art"
    )


def get_or_create_artist(name):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM artists WHERE name = %s",
        (name,)
    )

    result = cursor.fetchone()

    if result:

        conn.close()

        return result[0]

    cursor.execute(
        "INSERT INTO artists (name) VALUES (%s)",
        (name,)
    )

    conn.commit()

    artist_id = cursor.lastrowid

    conn.close()

    return artist_id


def insert_artwork(record):

    conn = get_connection()

    cursor = conn.cursor()

    artist_id = get_or_create_artist(record["artist"])

    cursor.execute(
        """
        INSERT INTO artworks
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

    conn.close()