from app.db import get_connection


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artists (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artworks (
        id INT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        artist_id INT,
        year INT,
        century INT,
        department VARCHAR(255) NOT NULL,
        image_url TEXT NOT NULL,
        FOREIGN KEY (artist_id) REFERENCES artists(id)
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("Tables created successfully.")


def initialize_database():
    create_tables()


if __name__ == "__main__":
    initialize_database()