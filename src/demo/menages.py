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

year_variables = ["P" + str(year) + "_POPH" for year in selected_years] + ["P" + str(year) + "_POPF" for year in selected_years]
data_commune = data[["CODGEO"] + year_variables]
pattern = re.compile(f"^C({year_pattern})_MEN(H|F)SEUL.*")
filtered_meta_data = filtered_meta_data[filtered_meta_data["COD_VAR"].astype(str).str.match(pattern)]
cod_var = filtered_meta_data["COD_VAR"]
selected_columns = [col for col in data.columns if col in cod_var.values]
filtered_data = data[["CODGEO"] + selected_columns]
filtered_data = filtered_data.merge(nom_commune[["code_insee", "nom_commune"]], 
                                     left_on="CODGEO", right_on="code_insee", 
                                     how="left").drop(columns=["code_insee"])
data_commune_melted = data_commune.melt(
    id_vars = "CODGEO",
    value_vars=year_variables,
    var_name = "vars",
    value_name="vals"
)
data_commune_melted["sexe"] = np.where(data_commune_melted["vars"].str[7:8] == "H", "Homme", "Femme")
data_commune_melted["année"] = "20" + data_commune_melted["vars"].str[1:3]
melted_data = filtered_data.melt(
            id_vars=["nom_commune","CODGEO"],
            value_vars=selected_columns,
            var_name="Variable",
            value_name="Valeur"
        )
melted_data["sexe"] = np.where(melted_data["Variable"].str[7:8] == "H", "Homme", "Femme")
melted_data["année"] = "20" + melted_data["Variable"].str[1:3]
#filtered_data_sum["Année"] = "20"+filtered_data_sum.index.str[1:3]
melted_data = melted_data.merge(data_commune_melted,on=["CODGEO","sexe","année"])
melted_data["Proportion"] = melted_data["Valeur"]/melted_data["vals"]

citron = px.bar(
            melted_data,
            x="sexe",
            y="Valeur",
            color="année",
            barmode="group",
            title=f"main",
            labels={"nom_commune": "Commune", "Valeur": "Population", "Legende": "Année"}
        )

#st.write(citron) supprimé pour l'instant.


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

filtered_columns = data.filter(regex=r'^(?!P21_POP15P$)P21_POP15P').sum()

filtered_columns_df = pd.DataFrame({
    'valeur': filtered_columns.values,
    'statut' :[
    "Marié",
    "Pacsé",
    "Concubinage, Union libre",
    "Veufs",
    "Divorcé",
    "Celibataire"]
})

mangue = px.bar(filtered_columns_df, 
             x='valeur', 
             y='statut', 
             orientation='h', 
             title='Nombre de personnes par statut marital',
             color = 'statut',
             labels={'valeur': 'Valeur', 'statut': 'Statut marital','P21_POP15P_CELIBATAIRE' : 'TEST'})

st.write(mangue)

