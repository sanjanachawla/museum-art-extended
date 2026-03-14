from app.met_client import get_artwork
from app.data_normalizer import normalize_artwork_data


def main():

    object_id = 436121

    raw = get_artwork(object_id)

    normalized = normalize_artwork_data(raw)

    print("\nNormalized Artwork\n")

    for key, value in normalized.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()