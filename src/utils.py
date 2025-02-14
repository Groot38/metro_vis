import pandas as pd
import json
import streamlit as st
import os

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

@st.cache_data
def load_atmo_data(rep_path : str):
    """ 
    filepath : le nom du sous dossier dans data/atmo
    """
    dataframes = []
    for file in os.listdir(rep_path) :
        filepath = os.path.join(rep_path,file)
        df = pd.read_csv(filepath,sep = ",")
        dataframes.append(df)
    data = pd.concat(dataframes,axis = 0)
    stations_metro = ["St-Martin-d'Hères","Grenoble les Frênes","Grenoble Periurbain Sud","Grenoble Boulevards","Rocade Sud Eybens","Champ-sur-Drac"]
    data = data[data["Station"].isin(stations_metro)]
    return data

def filtre_pattern(filtered_meta_data,pattern,data,nom_commune):
    filtered_meta_data = filtered_meta_data[filtered_meta_data["COD_VAR"].astype(str).str.match(pattern)]
    cod_var = filtered_meta_data["COD_VAR"]
    selected_columns = [col for col in data.columns if col in cod_var.values]
    filtered_data = data[["CODGEO"] + selected_columns]
    filtered_data = filtered_data.merge(nom_commune[["code_insee", "nom_commune"]], 
                                        left_on="CODGEO", right_on="code_insee", 
                                        how="left").drop(columns=["code_insee"])
    return filtered_data,selected_columns