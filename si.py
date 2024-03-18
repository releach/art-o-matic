import random
import re
import urllib.parse
from collections import OrderedDict

import requests
import streamlit as st
from si_query import si_works_query

# Function that cleans raw text from JSON response
CLEANR = re.compile("<.*?>")


def cleanhtml(raw_text):
    cleantext = re.sub(CLEANR, "", raw_text)
    return cleantext


@st.cache
def get_si_data():
    # Smithsonian Linked Data SPARQL endpoint URL
    url = "http://edan.si.edu/saam/sparql"
    query = si_works_query()

    # Call the SPARQL endpoint, pull back data as JSON, and write it to a list
    r = requests.get(url, params={"format": "json", "query": query})
    data = r.json()
    return data


def construct_list():
    data = get_si_data()
    bindings = data.get("results", {}).get("bindings", [])
    
    def get_value(item, key, default=""):
        return item.get(key, {}).get("value", default)

    artists = [
        OrderedDict(
            {
                "uri": get_value(item, "artist"),
                "label": get_value(item, "sampleLabel"),
                "image": get_value(item, "image"),
                "birthDate": get_value(item, "birthDate"),
                "deathDate": get_value(item, "deathDate"),
                "shortBio": cleanhtml(get_value(item, "shortBio")),
                "nationalityLabel": get_value(item, "nationalityLabel"),
                "workRepresentation": get_value(item, "workRepresentation"),
                "work": get_value(item, "work"),
            }
        )
        for item in bindings
    ]

    return artists


def app():
    st.set_page_config(page_title="Art-O-Matic", page_icon="🖼️")
    
    st.markdown(
        "<h1 style='font-size: 3em; font-family: Verdana, Geneva, sans-serif;'>Art-O-Matic 🖼</h1>",
        unsafe_allow_html=True,
    )
    
    st.write("Refresh the page for more art.")
    
    with st.spinner(text="Loading ..."):
        artist = random.choice(construct_list())
        
        artistName = artist.get("label", "")
        birthDate = artist.get("birthDate", "")[:4]
        deathDate = artist.get("deathDate", "")
        lifeRange = f"{birthDate} - {deathDate}" if birthDate else ""
        artistNat = artist.get("nationalityLabel", "")
        artistDetails = f"{lifeRange}   *   {artistNat}" if artistNat else ""
        
        workId = artist.get("work", "").partition("http://edan.si.edu/saam/id/object/")[2]
        workLink = f"https://americanart.si.edu/search?query={workId}"
        
        cleanArtistName = urllib.parse.quote(artistName)
        artistLink = f"https://americanart.si.edu/search?query={cleanArtistName}&f[0]=content_type:person"
        
        lodArtist = artist.get("uri", "")
        lodWork = artist.get("work", "")
        
        st.image(artist.get("workRepresentation", ""))
        st.markdown(
            """<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """,
            unsafe_allow_html=True,
        )
        
        st.header(artistName)
        st.text(artistDetails)
        
        col1, col2 = st.columns(2)

        if artist.get("image", ""):
            with col1:
                st.image(artist["image"], use_column_width="always")
        with col2:
            st.markdown(artist["shortBio"])
        
        st.markdown(
            """<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """,
            unsafe_allow_html=True,
        )
        
        st.header("Links")
        st.markdown("_Data Source: Smithsonian American Art Museum_")
        st.markdown("The work: [Linked open data](%s)  *  [Search the SAAM catalog](%s)" % (lodWork, workLink))
        st.markdown("The artist: [Linked open data](%s)  *  [Search the SAAM catalog](%s)" % (lodArtist, artistLink))

        hide_streamlit_style = """
                    <style>
                    footer {visibility: hidden;}
                    </style>
                    """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)


app()
