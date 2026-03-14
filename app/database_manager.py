from app.db import get_connection


def clear_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM artworks")
    cursor.execute("DELETE FROM artists")

    conn.commit()

    cursor.close()
    conn.close()

    print("Tables cleared.")


def drop_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS artworks")
    cursor.execute("DROP TABLE IF EXISTS artists")

    conn.commit()

    cursor.close()
    conn.close()

    print("Tables dropped.")