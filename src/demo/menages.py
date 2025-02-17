import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import re
import matplotlib.pyplot as plt
from utils import load_data,load_geojson,filtre_pattern
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

pattern = re.compile(f"^C({year_pattern})_NE24F.*")

filtered_data,selected_columns = filtre_pattern(meta_data[meta_data["THEME"] == "Couples - Familles - Ménages"],pattern,data,nom_commune)
melted_data = filtered_data.melt(
            id_vars=["nom_commune"],
            value_vars=selected_columns,
            var_name="Variable",
            value_name="Valeur"
        )   

melted_data["année"] = "20" + melted_data["Variable"].str[1:3]
melted_data["nombre enfants"] = melted_data["Variable"].str[9:11]
melted_data = melted_data.groupby(["nombre enfants","année"]).sum(numeric_only=True).reset_index()
#melted_data = melted_data[melted_data["année"] == 20+max(selected_years)].sort_values(by=["nom_commune", "nombre enfants"])
melted_data = melted_data.sort_values(["nombre enfants"])

# Création du barplot avec Plotly Express
passion = px.bar(melted_data, 
             x="année", 
             y="Valeur", 
             color="nombre enfants", 
             title="Évolution du nombre d'enfants par famille",
             labels={"Valeur": "Nombre d'enfants", "année": "Année", "nombre enfants": "Nombre d'enfants"},
             barmode="group")

st.write(passion)
st.markdown(
    "<p style='text-align: left; color: gray; margin-top: -50px;'>"
    "Source : INSEE, Dossier Complet 2024</p>",
    unsafe_allow_html=True
)

filtered_columns = data.filter(regex=r'^(?!P21_POP15P$)P21_POP15P').sum()

filtered_columns_df = pd.DataFrame({
    'valeur': filtered_columns.values,
    'statut' :[
    "Marié",
    "Pacsé",
    "Concubinage, Union libre",
    "Veuf",
    "Divorcé",
    "Celibataire"]
})

mangue = px.bar(filtered_columns_df, 
             x='valeur', 
             y='statut', 
             orientation='h', 
             title='Nombre de personnes par statut marital',
             color = 'statut',
             labels={'valeur': 'Valeur', 'statut': 'Statut marital','P21_POP15P_CELIBATAIRE' : 'TEST'},
             ).update_yaxes(categoryorder="total ascending")

st.write(mangue)
st.markdown(
    "<p style='text-align: left; color: gray; margin-top: -50px;'>"
    "Source : INSEE, Dossier Complet 2024</p>",
    unsafe_allow_html=True
)

