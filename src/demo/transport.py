import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# 📂 Charger les fichiers GeoJSON
@st.cache_data
def load_data_transport():
    geojson_path_velo = "../data/transport/velo.json"
    geojson_path_tag = "../data/transport/lignes_transport_reseau_tag.geojson"

    # 📍 Lire directement avec GeoPandas
    gdf_velo = gpd.read_file(geojson_path_velo)
    gdf_tag = gpd.read_file(geojson_path_tag)

    return gdf_velo, gdf_tag

# 📊 Charger les données
velo, tag = load_data_transport()

# 🎛️ Ajouter des cases à cocher pour afficher les données souhaitées
afficher_pistes_cyclables = st.checkbox("Afficher les pistes cyclables 🚲", value=True)
afficher_trams = st.checkbox("Afficher les lignes de tram 🚋", value=True)
afficher_bus = st.checkbox("Afficher les lignes de bus 🚌", value=True)

# 🌍 Créer une carte Folium centrée sur Grenoble
m = folium.Map(location=[45.1885, 5.7245], zoom_start=11)

# 🚲 Ajouter les pistes cyclables si coché
if afficher_pistes_cyclables:
    folium.GeoJson(
        velo, 
        name="Pistes Cyclables",
        tooltip=folium.GeoJsonTooltip(fields=["ogc_fid"], aliases=["Nom :"]),  
        style_function=lambda x: {"fillColor": "blue", "color": "black", "weight": 1, "fillOpacity": 0.5},
    ).add_to(m)

# 📌 Filtrer les données de transport pour trams et bus
trams = tag[tag["id"].str.startswith("SEM_") & tag["id"].str[4:].str.isalpha()]  # Trams (lettres après SEM_)
bus = tag[tag["id"].str.startswith("SEM_") & tag["id"].str[4:].str.isnumeric()]  # Bus (chiffres après SEM_)

# 🚋 Ajouter les trams si coché
if afficher_trams:
    folium.GeoJson(
        trams,  
        name="Lignes de Tram",
        tooltip=folium.GeoJsonTooltip(fields=["id"], aliases=["Tram :"]),  
        style_function=lambda x: {"color": "red", "weight": 4},  
    ).add_to(m)

# 🚌 Ajouter les bus si coché
if afficher_bus:
    folium.GeoJson(
        bus,  
        name="Lignes de Bus",
        tooltip=folium.GeoJsonTooltip(fields=["id"], aliases=["Bus :"]),  
        style_function=lambda x: {"color": "blue", "weight": 2},  
    ).add_to(m)

# 🎛️ Affichage dans Streamlit
st_folium(m, width=700, height=500)
