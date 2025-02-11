import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import re
import matplotlib.pyplot as plt
from utils import load_data,load_geojson
import numpy as np
import plotly.graph_objects as go


geojson_commune = load_geojson()
data,meta_data,nom_commune= load_data()

filtered_meta_data = meta_data[meta_data["THEME"] == "Couples - Familles - Ménages"] 

selected_years = []
if st.sidebar.checkbox("2010",value = True):
    selected_years.append("10")
if st.sidebar.checkbox("2015",value = True):
    selected_years.append("15")
if st.sidebar.checkbox("2021",value = True):
    selected_years.append("21")

if selected_years == []:
    selected_years.append("21")

year_pattern = "|".join(selected_years)

visualization_type = st.sidebar.radio("Analyse des ménages par : ", ["Catégorie d'âge", "Sexe"])

if visualization_type == "Sexe" : 
    selection_sex = st.sidebar.radio(
        "",
        ("Les deux", "Homme", "Femme"),
    )

    # Affichage du bouton sélectionné
    if selection_sex  == "Homme":
        pattern_sex = "H"
        st.session_state["selected_variable"] = None
    elif selection_sex  == "Femme":
        pattern_sex = "F"
        st.session_state["selected_variable"] = None
    else:
        pattern_sex = "Pop"
        st.session_state["selected_variable"] = None

    selection, uhu = st.columns([1,4],vertical_alignment="center")

    with selection : 
        categories = elec_tot["FILIERE"].unique()
        secteur_selectionné = st.selectbox("Sélectionnez un secteur :", secteurs_disponibles)


