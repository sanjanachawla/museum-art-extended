from app.met_client import get_artwork
from app.data_normalizer import normalize_artwork_data
from app.db import insert_artwork


def main():

    object_id = 436121

    raw = get_artwork(object_id)

    normalized = normalize_artwork_data(raw)

    insert_artwork(normalized)

    print("\nArtwork inserted into database\n")


if __name__ == "__main__":

    main()