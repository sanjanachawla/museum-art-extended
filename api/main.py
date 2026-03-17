from fastapi import FastAPI
from app.db import get_connection
from app import db
from fastapi.responses import JSONResponse
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("api")

app = FastAPI()


@app.get("/health")
def health_check():

    return {"status": "ok"}


@app.get("/artworks")
def get_artworks():

    try:
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
    except Exception as e:
        logger.error(f"Error in /artworks endpoint: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})



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

@app.get("/analytics")
def get_analytics():

    analytics = {
        "department": db.get_department_distribution(),
        "century": db.get_century_distribution(),
        "timeline": db.get_timeline_distribution()
    }

    return analytics
