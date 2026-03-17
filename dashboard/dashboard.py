import streamlit
import requests
import pandas
import plotly.express as px
import os

streamlit.set_page_config(page_title="MET Museum Art Explorer", layout="wide")  

API_URL = os.getenv("API_URL", "http://127.0.0.1:8001")

streamlit.markdown(
    """
    <h1 style='text-align: center; font-size: 4em; color: red; font-family: "Georgia", serif;'>
    MET Museum Art Explorer
    </h1>
    """,
    unsafe_allow_html=True
)

streamlit.markdown(
    """
    <h1 style='text-align: center; font-size: 2em; color: gray; font-family: "Georgia", serif;'>
    explore a subset of the MET Museum's art collection with interactive charts and a gallery view. 
    Use the filters to discover artworks by different artists and centuries.
    </h1>
    """,
    unsafe_allow_html=True
)

streamlit.divider()

try:
    response = requests.get(f"{API_URL}/artworks", timeout=30)
    response.raise_for_status()
    artworks = response.json()
except requests.RequestException as error:
    streamlit.error(f"Failed to load artworks from API at {API_URL}: {error}")
    streamlit.stop()

# turn to dataframe
artworks_df = pandas.DataFrame(artworks)

#extract data
artists = sorted(list(set(artwork["artist"] for artwork in artworks)))
centuries = sorted(list(set(artwork["century"] for artwork in artworks if artwork["century"] is not None))) 

# selected_artist = streamlit.selectbox("Select Artist", ["All"] + artists)
# selected_century = streamlit.selectbox("Select Century", ["All"] + centuries)

# filtered_artworks = artworks
# if selected_artist != "All":
#     filtered_artworks = [artwork for artwork in filtered_artworks if artwork["artist"] == selected_artist]  
# if selected_century != "All":
#     filtered_artworks = [artwork for artwork in filtered_artworks if artwork["century"] == selected_century]

# layout : charts| gallery

# streamlit.subheader("Filtering Options")
streamlit.markdown(
    """
    <h1 style='text-align: left; font-size: 1.5em; color: red; font-family: "Georgia", serif;'>
    Filters
    </h1>
    """,
    unsafe_allow_html=True
)
selected_artist = streamlit.selectbox("Select Artist", ["All"] + artists)
selected_century = streamlit.selectbox("Select Century", ["All"] + centuries)

filtered_artworks = artworks
if selected_artist != "All":
    filtered_artworks = [artwork for artwork in filtered_artworks if artwork["artist"] == selected_artist]  
if selected_century != "All":
    filtered_artworks = [artwork for artwork in filtered_artworks if artwork["century"] == selected_century]

if len(filtered_artworks) == 0:
    streamlit.warning("No artworks match the selected filters. Please adjust your selections.")
streamlit.divider()
charts_col, gallery_col = streamlit.columns([1, 2])

with charts_col:
    artworks_df = pandas.DataFrame(filtered_artworks)
    streamlit.markdown(
    """
    <h1 style='text-align: center; font-size: 1.5em; color: red; font-family: "Georgia", serif;'>
    Collection Analytics
    </h1>
    """,
    unsafe_allow_html=True
    )
    #streamlit.subheader("Collection Analytics")
    # if artworks_df.empty:
    #     streamlit.write("No artworks available to display charts.")
    
    if not artworks_df.empty:
        # artworks by department
        dept_counts = artworks_df["department"].value_counts().reset_index(name="count").rename(columns={"index": "department"})

        pie = px.pie(
            dept_counts,
            names="department",
            values="count",
            title="Artworks by Department"
        )
        streamlit.plotly_chart(pie, width='stretch')


        # century distribution
        centuries_df = artworks_df.dropna(subset=["century"])["century"].value_counts().reset_index(name="count").rename(columns={"index": "century"})

        bar = px.bar(
            centuries_df,
            x="century",
            y="count",
            title="Artworks by Century"
        )
        streamlit.plotly_chart(bar, width='stretch')

        # timeline
        timeline_df = artworks_df.dropna(subset=["year"])
        if not timeline_df.empty:
            timeline = px.scatter(
                timeline_df,
                x="year",
                y="department",
                hover_data=["title", "artist"],
                title="Artworks Timeline"
            )
            streamlit.plotly_chart(timeline, width='stretch')

# right side : gallery
with gallery_col:
    #streamlit.subheader("Artwork Gallery")
    streamlit.markdown(
    """
    <h1 style='text-align: center; font-size: 1.5em; color: red; font-family: "Georgia", serif;'>
    Gallery
    </h1>
    """,
    unsafe_allow_html=True
    )
    # selected_artist = streamlit.selectbox("Select Artist", ["All"] + artists)
    # selected_century = streamlit.selectbox("Select Century", ["All"] + centuries)

    # filtered_artworks = artworks
    # if selected_artist != "All":
    #     filtered_artworks = [artwork for artwork in filtered_artworks if artwork["artist"] == selected_artist]  
    # if selected_century != "All":
    #     filtered_artworks = [artwork for artwork in filtered_artworks if artwork["century"] == selected_century]

    cols = streamlit.columns(3)

    for i, artwork in enumerate(filtered_artworks):

        col = cols[i % 3]

        with col:

            streamlit.image(artwork["image_url"])

            streamlit.markdown(f"### {artwork['title']}")

            streamlit.write(f"**Artist:** {artwork['artist']}")
            streamlit.write(f"**Year:** {artwork['year']}")
            streamlit.write(f"**Century:** {artwork['century']}")
            streamlit.write(f"**Department:** {artwork['department']}")

            streamlit.markdown("---")
