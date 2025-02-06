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
    st.write(O3)
    O3["Date"] = pd.to_datetime(O3["Date"])
    prune = px.line(
        O3,
        x="Date",
        y=O3.iloc[:,1],
        color="Station",
        title="Évolution de la concentration d'azote (µg/m3) par Station",
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
    prune.add_hline(
        y = 25,
        line_dash="dash",
        line_color="black",
        annotation_text="Valeur limite pour la protection de la santé humaine UE",
        annotation_position="top right"
    )
    # Affichage de la figure
    st.write(prune)

if selected_variable == "Dioxyde d'azote" :
    NO2 = load_atmo_data("../data/atmo/NO2")
    st.write(NO2)
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
    prune.add_hline(
        y = 25,
        line_dash="dash",
        line_color="black",
        annotation_text="Valeur limite pour la protection de la santé humaine UE",
        annotation_position="top right"
    )
    # Affichage de la figure
    st.write(prune)

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
    # Affichage de la figure
    st.write(prune)

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
    # Affichage de la figure
    st.write(prune)
