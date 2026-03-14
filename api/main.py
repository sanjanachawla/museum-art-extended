from fastapi import FastAPI
from app.db import get_connection

app = FastAPI()


@app.get("/artworks")
def get_artworks():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT artworks.id,
               artworks.title,
               artists.name AS artist,
               artworks.year,
               artworks.century,
               artworks.department,
               artworks.image_url
        FROM artworks
        JOIN artists
        ON artworks.artist_id = artists.id
        LIMIT 50
    """)

    results = cursor.fetchall()

    conn.close()

    return results


@app.get("/artworks/{artwork_id}")
def get_artwork(artwork_id: int):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT artworks.id,
               artworks.title,
               artists.name AS artist,
               artworks.year,
               artworks.century,
               artworks.department,
               artworks.image_url
        FROM artworks
        JOIN artists
        ON artworks.artist_id = artists.id
        WHERE artworks.id = %s
    """, (artwork_id,))

    result = cursor.fetchone()

    conn.close()

    return result


@app.get("/artists")
def get_artists():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM artists")

    results = cursor.fetchall()

    conn.close()

    return results