import pandas as pd
import json
import streamlit as st

@st.cache_data
def load_data():
    data = pd.read_csv("../data_insee/dossier_complet/dossier_complet.csv", sep=',')
    meta_data = pd.read_csv("../data_insee/dossier_complet/meta_dossier_complet.csv", sep=';')
    nom_commune = pd.read_csv("../data/communes.csv", sep=',')
    return data,meta_data,nom_commune

@st.cache_data
def load_geojson():
    with open("../data/iris_contours/contours_communes.geojson", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    return geojson_data