import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from src.utils import load_data,load_geojson
import re
import plotly.express as px


st.title("Etude des transports de la métropole")

@st.cache_data
def load_data_transport():
    geojson_path_velo = "data/transport/velo.json"
    geojson_path_tag = "data/transport/lignes_transport_reseau_tag.geojson"

    gdf_velo = gpd.read_file(geojson_path_velo)
    gdf_tag = gpd.read_file(geojson_path_tag)

    return gdf_velo, gdf_tag

col1, col2  = st.columns([1,3],vertical_alignment="top")


velo, tag = load_data_transport()

with col1:
    afficher_pistes_cyclables = st.checkbox("Afficher les pistes cyclables 🚲", value=True)
    afficher_trams = st.checkbox("Afficher les lignes de tram 🚋", value=True)
    afficher_bus = st.checkbox("Afficher les lignes de bus 🚌", value=True)

m = folium.Map(location=[45.1885, 5.7245], zoom_start=11)

if afficher_pistes_cyclables:
    folium.GeoJson(
        velo, 
        name="Pistes Cyclables",
        tooltip=folium.GeoJsonTooltip(fields=["ogc_fid"], aliases=["Nom :"]),  
        style_function=lambda x: {"fillColor": "blue", "color": "black", "weight": 1, "fillOpacity": 0.5},
    ).add_to(m)

trams = tag[tag["id"].str.startswith("SEM_") & tag["id"].str[4:].str.isalpha()]  # Trams (lettres après SEM_)
bus = tag[tag["id"].str.startswith("SEM_") & tag["id"].str[4:].str.isnumeric()]  # Bus (chiffres après SEM_)

if afficher_trams:
    folium.GeoJson(
        trams,  
        name="Lignes de Tram",
        tooltip=folium.GeoJsonTooltip(fields=["id"], aliases=["Tram :"]),  
        style_function=lambda x: {"color": "red", "weight": 4},  
    ).add_to(m)

if afficher_bus:
    folium.GeoJson(
        bus,  
        name="Lignes de Bus",
        tooltip=folium.GeoJsonTooltip(fields=["id"], aliases=["Bus :"]),  
        style_function=lambda x: {"color": "blue", "weight": 2},  
    ).add_to(m)

with col2 :
    st.subheader(f"Cartes des transport de la Métropole de Grenoble")
    # 🎛️ Affichage dans Streamlit
    st_folium(m, width=700, height=500)
    st.markdown(
                "<p style='text-align: left; color: gray; margin-top: -40px;'>"
                "Source : Lignes transport reseau TAG et Pistes cyclables de la métropole Open data Grenoble ALpes Métropole</p><br><br>",
                unsafe_allow_html=True
    )

#Graphique des moyens de transport
geojson_commune = load_geojson()
data,meta_data,nom_commune= load_data()

filtered_columns = data.filter(regex=r'P(21|15|10)_ACTOCC15P_(PASTRANS|MARCHE|VELO|2ROUESMOT|VOITURE|COMMUN)$').sum()

filtered_columns_df = pd.DataFrame({
    'valeur': filtered_columns.values,
    'statut' :filtered_columns.index.str[14:],
    'année' : "20" + filtered_columns.index.str[1:3]
}).sort_values(by = "année")

nom_statuts = {
    "PASTRANS": "Pas de transport",
    "MARCHE": "Marche",
    "VELO": "Vélo",
    "2ROUESMOT": "2 Roues motorisées",
    "VOITURE": "Voiture",
    "COMMUN": "Transports en commun"
}
filtered_columns_df['statut'] = filtered_columns_df['statut'].replace(nom_statuts)

fraise = px.bar(filtered_columns_df, 
             x='statut', 
             y='valeur', 
             title='Moyen de transport utilisé pour se rendre sur le lieu de travail',
             color = 'année',
             labels={'valeur': 'Valeur', 'statut': 'Moyen de transport'},
             barmode='group')

st.write(fraise)
st.markdown(
    "<p style='text-align: left; color: gray; margin-top: -50px;'>"
    "Les catégories 'Vélo' et '2 roues motorisées' ont été ajoutées en 2021, c'est pourquoi il n'y a pas de données en 2015<br>"
    "Source : INSEE, Dossier Complet 2024</p>",
    unsafe_allow_html=True
)