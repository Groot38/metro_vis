import streamlit as st
import matplotlib.pyplot as plt
from utils import load_atmo_data
import pandas as pd
import re
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

variables = ["PM10","PM2.5","Dioxyde d'azote","Ozone"]
if "selected_atmo" not in st.session_state or st.session_state["selected_atmo"] == None: 
    selected_variable = st.sidebar.selectbox("Choisissez une catégorie à analyser", variables,index = 0)
    st.session_state["selected_atmo"] = selected_variable
else :
    selected_variable = st.sidebar.selectbox("Choisissez une catégorie à analyser",variables,index = variables.index(st.session_state["selected_atmo"]))
    st.session_state["selected_atmo"] = selected_variable

if selected_variable == "Ozone" :
    O3 = load_atmo_data("../data/atmo/O3")
    O3["Date"] = pd.to_datetime(O3["Date"])
    prune = px.line(
        O3,
        x="Date",
        y=O3.iloc[:,1],
        color="Station",
        title="Évolution de la concentration d'ozone (µg/m3) par Station",
        markers=True,
        labels={"y": "Valeur Mesurée", "Date": "Date", "Station": "Station"}
    )
    prune.add_hline(
        y = 120,
        line_dash="dash",
        line_color="green",
        annotation_text="Objectif de qualité pour la protection de la santé humaine",
        annotation_position="top right"
    )
    st.write(prune)
    st.markdown(
    "<p style='text-align: left; color: gray; margin-top: -50px;'>"
    "Les données sont des moyennes mensuelles allant de février 2014 à janvier 2025.<br>"
    "Le seuil d'objectif de qualité pour la protection de la santé humaine est un maximum journalier de la moyenne sur 8 heures par an.<br>"
    "Source : INSEE, Dossier Complet 2024</p>",
    unsafe_allow_html=True
    )

if selected_variable == "Dioxyde d'azote" :
    NO2 = load_atmo_data("../data/atmo/NO2")
    NO2["Date"] = pd.to_datetime(NO2["Date"])
    prune = px.line(
        NO2,
        x="Date",
        y=NO2.iloc[:,1],
        color="Station",
        title="Évolution de la concentration de dioxyde d'azote (µg/m3) par Station",
        markers=True,
        labels={"y": "Valeur Mesurée", "Date": "Date", "Station": "Station"}
    )
    prune.add_hline(
        y = 40,
        line_dash="dash",
        line_color="green",
        annotation_text="Objectif de qualité FR",
        annotation_position="top right"
    )
    prune.add_hline(
        y = 30,
        line_dash="dash",
        line_color="red",
        annotation_text="Niveau critique pour la protection de la végétation",
        annotation_position="top right"
    )
    st.write(prune)
    st.markdown(
    "<p style='text-align: left; color: gray; margin-top: -50px;'>"
    "Les données sont des moyennes mensuelles allant de février 2014 à janvier 2025.<br>"
    "Le seuil d'objectif de qualité est une moyenne annuelle.<br>"
    "Le seuil critique pour la protection de la végétation est une moyenne annuelle.<br>"
    "Source : INSEE, Dossier Complet 2024</p>",
    unsafe_allow_html=True
    )

if selected_variable == "PM2.5" :
    PM25 = load_atmo_data("../data/atmo/PM25")
    PM25["Date"] = pd.to_datetime(PM25["Date"])
    prune = px.line(
        PM25,
        x="Date",
        y=PM25.iloc[:,1],
        color="Station",
        title="Évolution de la concentration de PM2.5 (µg/m3) par Station",
        markers=True,
        labels={"y": "Valeur Mesurée", "Date": "Date", "Station": "Station"}
    )
    prune.add_hline(
        y = 10,
        line_dash="dash",
        line_color="green",
        annotation_text="Objectif de qualité FR",
        annotation_position="top right"
    )
    prune.add_hline(
        y = 20,
        line_dash="dash",
        line_color="red",
        annotation_text="Valeur cible pour la protection de la santé humaine FR",
        annotation_position="top right"
    )
    prune.add_hline(
        y = 25,
        line_dash="dash",
        line_color="black",
        annotation_text="Valeur limite pour la protection de la santé humaine UE",
        annotation_position="top right"
    )
    st.write(prune)
    st.markdown(
    "<p style='text-align: left; color: gray; margin-top: -50px;'>"
    "Les données sont des moyennes mensuelles allant de février 2014 à janvier 2025.<br>"
    "Le seuil d'objectif de qualité est une moyenne annuelle.<br>"
    "La valeur cible pour la protection de la santé humaine est une moyenne annuelle.<br>"
    "La valeur limite pour la protection de la santé humaine est une moyenne annuelle.<br>"
    "Source : INSEE, Dossier Complet 2024</p>",
    unsafe_allow_html=True
    )

if selected_variable == "PM10" :
    PM10 = load_atmo_data("../data/atmo/PM10")
    PM10["Date"] = pd.to_datetime(PM10["Date"])
    prune = px.line(
        PM10,
        x="Date",
        y=PM10.iloc[:,1],
        color="Station",
        title="Évolution de la concentration de PM10 (µg/m3) par Station",
        markers=True,
        labels={"y": "Valeur Mesurée", "Date": "Date", "Station": "Station"}
    )
    prune.add_hline(
        y = 30,
        line_dash="dash",
        line_color="green",
        annotation_text="Objectif de qualité FR",
        annotation_position="top right"
    )
    prune.add_hline(
        y = 40,
        line_dash="dash",
        line_color="red",
        annotation_text="Valeurs limites pour la protection de la santé humaine UE",
        annotation_position="top right"
    )
    prune.add_hline(
        y = 80,
        line_dash="dash",
        line_color="black",
        annotation_text="Seuil d'alerte FR",
        annotation_position="top right"
    )
    st.write(prune)
    st.markdown(
    "<p style='text-align: left; color: gray; margin-top: -50px;'>"
    "Les données sont des moyennes mensuelles allant de février 2014 à janvier 2025.<br>"
    "L'objectif de qualité est une moyenne annuelle.<br>"
    "La valeur limite pour la protection de la santé humaine est une moyenne annuelle.<br>"
    "Le seuil d'alerte est une moyenne sur 24h.<br>"
    "Source : INSEE, Dossier Complet 2024</p>",
    unsafe_allow_html=True
    )


#############################PARTIE DE ROMANE######################################################################
@st.cache_data
def load_data():
    file_path_ges = "../data/environnement/5.16-ITDD-Auvergne-Rhone-Alpes-Toutes-les-communes.2024-01.csv"
    df = pd.read_csv(file_path_ges,sep = ";",skiprows=1)
    return(df)

df= load_data()

df2 = df.drop(df.index[[0]])
ges = df2[df2["LIBELLE_VARIABLE"]=="Emissions de gaz à effet de serre par gaz"]

col1, col2  = st.columns([1,1],vertical_alignment="center")

with col1 :
    ville_selectionnee = st.selectbox("Sélectionnez une ville :", sorted(ges["CODGEO_LIBELLE"].unique()))
    gaz_selectionnee = st.selectbox("Sélectionnez un gaz à effet de serre :", sorted(ges["LIBELLE_SOUS_CHAMP"].unique()))
    ges_filtré = ges[(ges["CODGEO_LIBELLE"] == ville_selectionnee) & (ges["LIBELLE_SOUS_CHAMP"] == gaz_selectionnee)]

    if not ges_filtré.empty: 
        valeur_2016 = ges_filtré["A2016"].values[0]
        valeur_2018 = ges_filtré["A2018"].values[0]
    
        if valeur_2016 != 0:
            evolution = ((valeur_2018 - valeur_2016) / valeur_2016) * 100
        else:
            evolution = 0

        st.metric(
            label=f"Évolution 2016 → 2018 de {gaz_selectionnee} à {ville_selectionnee} en tonnes équivalent CO2",
            value=f"{evolution:.2f} %"
        )
    else:
        st.warning("Aucune donnée disponible pour cette sélection.")
    valeur_2018
    st.markdown(
        "<p style='text-align: left; color: gray;'>"
        "Source : SDES, Indicateurs territoriaux de développement durable (ITDD)</p>",
        unsafe_allow_html=True
    )

st.link_button("Source SDES", "https://www.statistiques.developpement-durable.gouv.fr/catalogue?page=datafile&datafileRid=318d1042-79c8-4d39-b337-9d261050cf7d")

#source Indicateurs territoriaux de développement durable (ITDD) : SDES