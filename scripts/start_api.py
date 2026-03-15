import os

import uvicorn

from app import data_normalizer
from app import db
from app import met_client
from scripts.ingest_artwork import get_object_ids, is_valid_artwork


def seed_artworks(target_count: int) -> None:
    current_count = db.count_artworks()

    if current_count >= target_count:
        print(f"Artwork seed skipped. Existing rows: {current_count}")
        return

    object_ids = get_object_ids()
    inserted_count = current_count

    for object_id in object_ids:
        if inserted_count >= target_count:
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
                inserted_count += 1
                print(f"Seeded artwork {object_id} ({inserted_count}/{target_count})")
        except Exception as error:
            print(f"Error seeding artwork {object_id}: {error}")


def main() -> None:
    seed_count = int(os.getenv("INITIAL_ARTWORK_SEED_COUNT", "100"))
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", "8000"))

    db.wait_for_database()
    db.initialize_database()
    seed_artworks(seed_count)

    uvicorn.run("api.main:app", host=api_host, port=api_port)


if __name__ == "__main__":
    main()
