import random

import requests

BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"
DEFAULT_HEADERS = {
    "User-Agent": "museum-art-extended/1.0"
}
DEFAULT_TIMEOUT = 10
SESSION = requests.Session()
SESSION.headers.update(DEFAULT_HEADERS)


def get_object_ids() -> list[int]:
    response = SESSION.get(f"{BASE_URL}/objects", timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    return data["objectIDs"]


def get_seed_candidate_ids(limit: int, pool_size: int | None = None) -> list[int]:
    object_ids = get_object_ids()

    if pool_size is not None:
        object_ids = object_ids[:pool_size]

    if limit >= len(object_ids):
        random.shuffle(object_ids)
        return object_ids

    return random.sample(object_ids, limit)

def get_artwork(object_id: int) -> dict:
    """
    Fetches artwork details from the Metropolitan Museum of Art Collection API.
    """
    # Validate the input
    if not isinstance(object_id, int) or object_id < 0:
        raise ValueError("object_id must be a non-negative integer")    
    # Construct the API URL and make the GET request
    url = f"{BASE_URL}/objects/{object_id}"
    response = SESSION.get(url, timeout=DEFAULT_TIMEOUT)
    # Check for HTTP errors and return the JSON response if successful
    response.raise_for_status()
    # Return the JSON response if the status code is 200, otherwise return None
    if response.status_code == 200:
        return response.json()
    else:
        return None
