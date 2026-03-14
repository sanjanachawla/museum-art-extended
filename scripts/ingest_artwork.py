import random
import requests

from app import met_client
from app import data_normalizer
from app import db


MET_OBJECTS_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects"


def get_object_ids():
    """Fetch all available MET object IDs."""
    response = requests.get(MET_OBJECTS_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["objectIDs"]


def is_valid_artwork(record):
    """Ensure artwork contains all required fields."""

    if not record:
        return False

    required_fields = ["id", "title", "artist", "department", "image_url"]

    for field in required_fields:
        if not record.get(field):
            return False

    return True


def main():

    print("Fetching MET object IDs...")
    object_ids = get_object_ids()

    # randomize order to get diverse artworks
    random.shuffle(object_ids)

    success_count = 0

    for object_id in object_ids:

        if success_count >= 100:
            break

        try:

            raw_artwork = met_client.get_artwork(object_id)

            if not raw_artwork:
                continue

            normalized = data_normalizer.normalize_artwork_data(raw_artwork)

            if not is_valid_artwork(normalized):
                continue

            inserted = db.insert_artwork(normalized)

            if inserted:
                success_count += 1
                print(f"Inserted artwork {object_id} ({success_count}/100)")

        except Exception as e:
            print(f"Error processing artwork {object_id}: {e}")

    print("\nFinished ingesting artworks.")


if __name__ == "__main__":
    main()