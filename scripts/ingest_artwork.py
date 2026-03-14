from app import met_client
from app import data_normalizer
from app import db
import requests

BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

def get_object_ids():

    url = f"{BASE_URL}/objects"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data["objectIDs"]

def main():
    object_ids = get_object_ids()
    count = 0
    for object_id in object_ids:  # Limit to first 100 for testing

        try:
            raw_artwork = met_client.get_artwork(object_id)
            normalized_artwork = data_normalizer.normalize_artwork_data(raw_artwork)
            inserted = db.insert_artwork(normalized_artwork)
            if inserted:
                print(f"Inserted artwork ID {object_id} into database.")
                count +=1
            #else:
               # print(f"Failed to insert artwork ID {object_id} into database.")
        except Exception as e:
            print(f"Error processing artwork ID {object_id}: {e}")

        if count >= 100:
            break


    print("\nFinished processing artworks.\n")

if __name__ == "__main__":
    main()