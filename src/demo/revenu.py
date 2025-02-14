import streamlit as st
import matplotlib.pyplot as plt
from utils import load_data
import pandas as pd
import re
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

data,meta_data,nom_commune= load_data()
pattern = re.compile(r"^TP60")
filtered_meta_data = meta_data[meta_data["COD_VAR"].astype(str).str.match(pattern)]

# Filtrage des données pour analyse
variables = filtered_meta_data["LIB_VAR_LONG"]
variables=list(dict.fromkeys(var[:-8] for var in variables))

filtered_meta_data["LIB_VAR_LONG_trimmed"] = filtered_meta_data["LIB_VAR_LONG"].str[:-8]
filtered_meta_data["CSP"] = filtered_meta_data["LIB_VAR_LONG_trimmed"].str.extract(r"plus (.+)")
cod_var = filtered_meta_data["COD_VAR"]

selected_columns = [col for col in data.columns if col in cod_var.values]
filtered_data = data[["CODGEO"] + selected_columns]
filtered_data = filtered_data.merge(nom_commune[["code_insee", "nom_commune"]], 
                                     left_on="CODGEO", right_on="code_insee", 
                                     how="left").drop(columns=["code_insee"])



pattern_salaire = re.compile(r"^SNHM")
filtered_meta_data = meta_data[meta_data["COD_VAR"].astype(str).str.match(pattern_salaire)]

# Filtrage des données pour analyse
variables = filtered_meta_data["LIB_VAR_LONG"]
variables=list(dict.fromkeys(var[:-8] for var in variables))

filtered_meta_data["LIB_VAR_LONG_trimmed"] = filtered_meta_data["LIB_VAR_LONG"].str[:-8]
filtered_meta_data["CSP"] = filtered_meta_data["LIB_VAR_LONG_trimmed"].str.extract(r"plus (.+)")
cod_var = filtered_meta_data["COD_VAR"]

selected_columns = [col for col in data.columns if col in cod_var.values]
filtered_data = data[selected_columns]
selection_sex = st.sidebar.radio(
    "",
    ("Homme", "Femme", "Les deux"),
)

# Affichage du bouton sélectionné
if selection_sex == "Homme":
    pattern_sex = r"^SNHMH[A-Za-z].*$"
elif selection_sex == "Femme":
    pattern_sex = r"^SNHMF[A-Za-z].*$"
else:
    pattern_sex = r"^SNHM[^HF][A-Za-z].*$"


filtered_columns = [col for col in filtered_data.columns if re.match(pattern_sex, col)]

filtered_data = filtered_data[filtered_columns]

filtered_data["CODGEO"] = data["CODGEO"]
filtered_data = filtered_data.merge(nom_commune[["code_insee", "nom_commune"]], 
                                     left_on="CODGEO", right_on="code_insee", 
                                     how="left").drop(columns=["code_insee"])
filtered_data = filtered_data.dropna(thresh=3).reset_index()
st.write(filtered_data)
nom_var = filtered_meta_data["LIB_VAR_LONG"][filtered_meta_data["COD_VAR"].isin(filtered_data.columns)]
st.write(nom_var)
var_mapping = dict(zip(filtered_meta_data["COD_VAR"], filtered_meta_data["LIB_VAR_LONG"]))
df_melted = filtered_data.melt(id_vars=["nom_commune"], var_name="Catégorie", value_name="Valeur")
df_melted["Catégorie"] = df_melted["Catégorie"].map(var_mapping)
# Création du barplot interactif avec Plotly Express
fig = px.bar(df_melted, x="nom_commune", y="Valeur", color="Catégorie", 
             labels={"Valeur": "Valeur", "nom_commune": "Nom de la Commune", "Catégorie": "Variable"},
             title="Barplot par catégorie pour chaque ville")
st.write(fig)
st.markdown(
    "<p style='text-align: left; color: gray;'>"
    "Source : INSEE, Dossier Complet 2024</p>",
    unsafe_allow_html=True
)