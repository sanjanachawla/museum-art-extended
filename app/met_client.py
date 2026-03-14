import requests

BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

def get_artwork(object_id: int) -> dict:
    """
    Fetches artwork details from the Metropolitan Museum of Art Collection API.
    """
    # Validate the input
    if not isinstance(object_id, int) or object_id < 0:
        raise ValueError("object_id must be a non-negative integer")    
    # Construct the API URL and make the GET request
    url = f"{BASE_URL}/objects/{object_id}"
    response = requests.get(url, timeout=10)
    # Check for HTTP errors and return the JSON response if successful
    response.raise_for_status()
    # Return the JSON response if the status code is 200, otherwise return None
    if response.status_code == 200:
        return response.json()
    else:
        return None