import streamlit
import requests

API_URL = "http://127.0.0.1:8000"

streamlit.title("MET Museum Art Explorer")

response = requests.get(f"{API_URL}/artworks")
artworks = response.json()

#extract data
artists = sorted(list(set(artwork["artist"] for artwork in artworks)))
centuries = sorted(list(set(artwork["century"] for artwork in artworks if artwork["century"] is not None))) 

selected_artist = streamlit.selectbox("Select Artist", ["All"] + artists)
selected_century = streamlit.selectbox("Select Century", ["All"] + centuries)

filtered_artworks = artworks
if selected_artist != "All":
    filtered_artworks = [artwork for artwork in filtered_artworks if artwork["artist"] == selected_artist]  
if selected_century != "All":
    filtered_artworks = [artwork for artwork in filtered_artworks if artwork["century"] == selected_century]

for artwork in filtered_artworks:
    streamlit.subheader(artwork["title"])
    streamlit.write(f"Artist: {artwork['artist']}")
    streamlit.write(f"Year: {artwork['year']}")
    streamlit.write(f"Century: {artwork['century']}")
    streamlit.write(f"Department: {artwork['department']}")
    if artwork["image_url"]:
        streamlit.image(artwork["image_url"], width=300)
    
    streamlit.markdown("---")