import os
import time

import requests

from app import data_normalizer
from app import db
from app import met_client
from app.seed_ids import FALLBACK_SEED_OBJECT_IDS
from scripts.ingest_artwork import is_valid_artwork


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value is not None else default


def is_retryable_error(error: Exception) -> bool:
    if isinstance(error, requests.Timeout):
        return True

    if isinstance(error, requests.ConnectionError):
        return True

    if isinstance(error, requests.HTTPError) and error.response is not None:
        return error.response.status_code in {408, 425, 429, 500, 502, 503, 504}

    return False


def candidate_ids_for_seed(target_count: int, max_attempts: int) -> list[int]:
    pool_size = max(max_attempts * 3, target_count * 10)
    candidate_ids = list(FALLBACK_SEED_OBJECT_IDS)

    try:
        dynamic_ids = met_client.get_seed_candidate_ids(
            limit=max_attempts,
            pool_size=pool_size,
        )
    except requests.RequestException as error:
        print(f"Falling back to curated seed IDs after object list fetch failed: {error}")
        dynamic_ids = []

    for object_id in dynamic_ids:
        if object_id not in candidate_ids:
            candidate_ids.append(object_id)

    return candidate_ids[:max_attempts]


def seed_artworks(target_count: int) -> int:
    current_count = db.count_artworks()
    max_attempts = env_int("INITIAL_ARTWORK_MAX_ATTEMPTS", 300)
    max_retries_per_artwork = env_int("INITIAL_ARTWORK_RETRIES_PER_ARTWORK", 2)
    retry_backoff_seconds = float(os.getenv("INITIAL_ARTWORK_RETRY_BACKOFF_SECONDS", "1.5"))
    minimum_seed_count = env_int("INITIAL_ARTWORK_MINIMUM_COUNT", target_count)
    fail_on_shortfall = db.env_flag("FAIL_ON_SEED_SHORTFALL", default=True)

    if current_count >= target_count:
        print(f"Artwork seed skipped. Existing rows: {current_count}")
        return current_count

    object_ids = candidate_ids_for_seed(target_count, max_attempts)
    inserted_count = current_count
    attempts = 0
    retryable_failures = 0
    permanent_failures = 0

    for object_id in object_ids:
        if inserted_count >= target_count:
            break
        if attempts >= max_attempts:
            break

        attempts += 1
        last_error = None

        for retry_index in range(max_retries_per_artwork + 1):
            try:
                raw_artwork = met_client.get_artwork(object_id)

                if not raw_artwork:
                    break

                normalized = data_normalizer.normalize_artwork_data(raw_artwork)

                if not is_valid_artwork(normalized):
                    break

                inserted = db.insert_artwork(normalized)

                if inserted:
                    inserted_count += 1
                    print(f"Seeded artwork {object_id} ({inserted_count}/{target_count})")

                last_error = None
                break
            except Exception as error:
                last_error = error

                if not is_retryable_error(error) or retry_index == max_retries_per_artwork:
                    break

                sleep_seconds = retry_backoff_seconds * (retry_index + 1)
                print(
                    f"Retrying artwork {object_id} after transient error: {error} "
                    f"(attempt {retry_index + 2}/{max_retries_per_artwork + 1})"
                )
                time.sleep(sleep_seconds)

        if last_error is not None:
            if is_retryable_error(last_error):
                retryable_failures += 1
            else:
                permanent_failures += 1
            print(f"Error seeding artwork {object_id}: {last_error}")

    print(
        "Bootstrap finished with "
        f"{inserted_count} artworks after {attempts} attempts "
        f"({retryable_failures} transient failures, {permanent_failures} permanent failures)."
    )

    if inserted_count < minimum_seed_count and fail_on_shortfall:
        raise RuntimeError(
            f"Seed shortfall: expected at least {minimum_seed_count} artworks, got {inserted_count}."
        )

    return inserted_count


def main() -> None:
    seed_count = env_int("INITIAL_ARTWORK_SEED_COUNT", 100)
    create_db_if_missing = db.env_flag("CREATE_DB_IF_MISSING", default=False)
    run_seed = db.env_flag("RUN_SEED", default=True)

    db.wait_for_database()
    db.initialize_database(create_database_if_missing=create_db_if_missing)

    if run_seed:
        seed_artworks(seed_count)


if __name__ == "__main__":
    main()
