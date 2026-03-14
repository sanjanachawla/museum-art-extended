import re
from typing import Any, Optional

def extract_year(object_date: str) -> Any:
    """
    Extracts the year from the objectDate field of the artwork data.
    Handles various formats such as "c. 1500", "1500-1600", "1500", etc.
    """
    if not isinstance(object_date, str):
        return None
    
    # Remove any leading/trailing whitespace
    object_date = object_date.strip()
    
    # Handle cases like "c. 1500" or "ca. 1500"
    match = re.search(r'c\.?\s*(\d{3,4})', object_date, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Handle cases like "1500-1600"
    match = re.search(r'(\d{3,4})\s*-\s*(\d{3,4})', object_date)
    if match:
        return int(match.group(1))  # Return the starting year
    
    # Handle cases like "1500"
    match = re.search(r'^\d{3,4}$', object_date)
    if match:
        return int(match.group(0))
    
    return None


def calculate_century(year: int) -> Optional[int]:
    """
    Calculates the century from a given year.
    For example, 1500-1599 is the 16th century, 1600-1699 is the 17th century, etc.
    """
    if not isinstance(year, int) or year <= 0:
        return None
    return (year - 1) // 100 + 1


def normalize_artist(artist_name: str) -> str:
    """
    Normalizes the artist's name by removing extra whitespace and converting to title case.
    """

    if not isinstance(artist_name, str):
        return "Unknown Artist"
    
    # Remove extra whitespace and convert to title case
    return artist_name.strip().title()

def normalize_artwork_data(raw_artwork: dict) -> dict:
    """
    Normalizes the artwork data by applying all normalization functions.
    """
    if not isinstance(raw_artwork, dict):
        return {}
    
    # Start with a copy of the raw artwork data to avoid modifying the original
    # normalized_data = raw_artwork.copy()

    # Normalize artist name
    # normalized_data['artistDisplayName'] = normalize_artist(normalized_data.get('artistDisplayName', ''))

    # Extract and normalize year
    year = extract_year(raw_artwork.get('objectDate', ''))
    # normalized_data['year'] = year

    # Calculate and add century
    century = calculate_century(year)
    # normalized_data['century'] = century

    normalized_data = {
        "id": raw_artwork.get("objectID"),
        "title": raw_artwork.get("title"),
        "artist": normalize_artist(raw_artwork.get("artistDisplayName")),
        "year": year,
        "century": calculate_century(year),
        "department": raw_artwork.get("department"),
        "image_url": raw_artwork.get("primaryImageSmall") or None,
    }

    return normalized_data