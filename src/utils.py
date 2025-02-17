import pandas as pd
import json
import streamlit as st
import os


@st.cache_data
def load_data():
    """
    Retourne
    - **data_insee** : Données du dossier complet de l'INSEE.
    - **meta_data** : Méta-données du dossier complet de l'INSEE.
    - **nom_commune** : CSV contenant les codes INSEE et le nom des communes de la métro de Grenoble.

    Exemple :
    code_insee, nom_commune
    38057, Bresson
    """
    data_insee = pd.read_csv("../data_insee/dossier_complet/dossier_complet.csv", sep=',')
    meta_data = pd.read_csv("../data_insee/dossier_complet/meta_dossier_complet.csv", sep=';')
    nom_commune = pd.read_csv("../data/communes.csv", sep=',')
    return data_insee,meta_data,nom_commune

@st.cache_data
def load_geojson():
    """
    Retourne
    - 1 fichier json : correspond au contours geojson des communes de la métropole de Grenoble
       
    """
    with open("../data/iris_contours/contours_communes.geojson", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    return geojson_data

@st.cache_data
def load_atmo_data(rep_path : str):
    """ 
    Cette fonction parcours un répertoire correspondant à un polluant, et concatène chaque fichier de ce répertoire
    ex : Parcours le sous répertoire O3 de data/atmo/O3

    Paramètres
    - rep_path : le nom du sous répertoire dans data/atmo parmi NO2 O3 PM10 et PM25
    exemple : data/atmo/O3

    Retourne
    - 1 dataframe : contenant les donnée sur la qualité de l'air de 6 stations sur le polluant séléctionné

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
    """ 
    Cette fonction renvoie une partie des données du dossier complet de l'INSEE en utilisant un pattern regex.

    Paramètres
    - filtered_meta_data : donnée pré_traité du dossier méta_data de l'INSEE
    - pattern : regex pour séléctionner les bonnes colonnes
    - data : dossier complet de l'INSEE
    - nom_commune : CSV contenant les codes INSEE et le nom des communes de la métro de Grenoble.

    Retourne
    - 1 dataframe filtered_data : contenant les colonnes séléctionnés du dossier complet et le nom_commune
    - 1 series selected_columns : la liste des colonnes séléctionnés grâce au regex

    """
    filtered_meta_data = filtered_meta_data[filtered_meta_data["COD_VAR"].astype(str).str.match(pattern)]
    cod_var = filtered_meta_data["COD_VAR"]
    selected_columns = [col for col in data.columns if col in cod_var.values]
    filtered_data = data[["CODGEO"] + selected_columns]
    filtered_data = filtered_data.merge(nom_commune[["code_insee", "nom_commune"]], 
                                        left_on="CODGEO", right_on="code_insee", 
                                        how="left").drop(columns=["code_insee"])
    return filtered_data,selected_columns