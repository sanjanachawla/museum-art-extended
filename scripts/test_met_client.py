from app import met_client

def main():
    object_id = 463121
    artwork = met_client.get_artwork(object_id)
    if artwork:

        print("Artwork details:")
        print(f"Object ID: {artwork['objectID']}")
        print(f"Title: {artwork['title']}")
        print(f"Artist: {artwork['artistDisplayName']}")
        print(f"Date: {artwork['objectDate']}")

if __name__ == "__main__":
    main()