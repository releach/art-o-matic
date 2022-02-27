import random
import re
from collections import OrderedDict

import requests
import streamlit as st

# Function that cleans raw text from JSON response
CLEANR = re.compile("<.*?>")


def cleanhtml(raw_text):
    cleantext = re.sub(CLEANR, "", raw_text)
    return cleantext



@st.cache(suppress_st_warning=True)
def get_si_data():
    # Smithsonian Linked Data SPARQL endpoint URL
    url = "http://edan.si.edu/saam/sparql"

    # SPARQL query for artists, bio, death/birth dates, images
    query = """
    PREFIX edan: <http://edan.si.edu/saam/id/ontologies/>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT ?artist (SAMPLE(?label) as ?sampleLabel) ?image ?shortBio ?deathDate ?birthDate ?nationalityLabel ?workRepresentation ?work
    WHERE {
    ?artist edan:PE_has_main_representation ?image ;
            edan:PE_has_note_artistbio ?shortBio ;
            cidoc:P1_is_identified_by ?displayName .
    ?displayName rdfs:label ?label .

    ?artist cidoc:P100i_died_in ?P100i_died_in .
    ?P100i_died_in cidoc:P4_has_time-span ?deathSpan .
    ?deathSpan cidoc:P82_at_some_time_within ?deathDate .

    ?artist cidoc:P98i_was_born ?P98i_was_born .
    ?P98i_was_born cidoc:P4_has_time-span ?birthSpan .
    ?birthSpan cidoc:P82_at_some_time_within ?birthDate .

    ?artist cidoc:P107i_is_current_or_former_member_of ?nationality .
    ?nationality skos:prefLabel ?nationalityLabel .

    ?production cidoc:P14_carried_out_by ?artist .
    ?production cidoc:P108_has_produced ?work .
    ?work cidoc:P138i_has_representation ?workRepresentation
    }
    GROUP BY ?artist ?image ?shortBio ?deathDate ?birthDate ?nationalityLabel ?workRepresentation ?work
    LIMIT 5000
    """

    # Call the SPARQL endpoint, pull back data as JSON, and write it to a list
    r = requests.get(url, params={"format": "json", "query": query})
    data = r.json()
    return data

@st.cache(suppress_st_warning=True)
def construct_list():
    data = get_si_data()
    artists = []
    for item in data["results"]["bindings"]:
        shortBio = cleanhtml(item["shortBio"]["value"])
        artists.append(
            OrderedDict(
                {
                    "uri": item["artist"]["value"],
                    "label": item["sampleLabel"]["value"],
                    "image": item["image"]["value"],
                    "birthDate": item["birthDate"]["value"],
                    "deathDate": item["deathDate"]["value"],
                    "shortBio": shortBio,
                    "nationalityLabel": item["nationalityLabel"]["value"],
                    "workRepresentation": item["workRepresentation"]["value"],
                    "work": item["work"]["value"],
                }
            )
        )

    return artists


def app():
    st.set_page_config(page_title="Art-O-Matic", page_icon="🖼️", layout="wide")
    st.markdown(
        "<h1 style='font-size: 4em; font-family: Verdana, Geneva, sans-serif;'>Art-O-Matic</h1>",
        unsafe_allow_html=True,
    )
    st.write("Refresh the page for more art.")
    list = construct_list()
    artist = random.choice(list)
    birthDate = artist["birthDate"][0:4]
    deathDate = artist["deathDate"]
    lifeRange = f"{birthDate} - {deathDate}"
    artistnat = artist["nationalityLabel"]
    artistDetails = f"{lifeRange}   *   {artistnat}"
    lodlink = artist["work"]
    workid = artist["work"].partition("http://edan.si.edu/saam/id/object/")[2]
    worklink = f"https://americanart.si.edu/search?query={workid}"

    with st.container():
        st.image(artist["workRepresentation"])
        st.write("[Linked open data about this work](%s)" % lodlink)
        st.write("[Search the catalog for this work](%s)" % worklink)
        st.markdown(
            """<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """,
            unsafe_allow_html=True,
        )
    with st.container():
        st.header(artist["label"])
        st.text(artistDetails)
        col3, col4 = st.columns(2)
        with col3:
            st.image(artist["image"], use_column_width="always")
        with col4:
            st.markdown(artist["shortBio"])


app()
