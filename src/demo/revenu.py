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

variables = filtered_meta_data["LIB_VAR_LONG"]
variables=list(dict.fromkeys(var[:-8] for var in variables))

filtered_meta_data["LIB_VAR_LONG_trimmed"] = filtered_meta_data["LIB_VAR_LONG"].str[:-8]
filtered_meta_data["CSP"] = filtered_meta_data["LIB_VAR_LONG_trimmed"].str.extract(r"plus (.+)")
cod_var = filtered_meta_data["COD_VAR"]

selected_columns = [col for col in data.columns if col in cod_var.values]
filtered_data = data[selected_columns]
selection_sex = st.sidebar.radio(
    "",
    ("Homme", "Femme", "Les deux","comparaison homme femme"),
)

if selection_sex == "Homme":
    pattern_sex = r"^SNHMH[A-Za-z].*$"
    sex_char = "des hommes"
    nb_car = 36
elif selection_sex == "Femme":
    pattern_sex = r"^SNHMF[A-Za-z].*$"
    sex_char = "des femmes"
    nb_car = 36
elif selection_sex == "Les deux":
    pattern_sex = r"^SNHM[CPEO].*$"
    sex_char = ""
    nb_car = 30
else:
    pattern_sex = r"^SNHM[F|H][CPEO].*$"
    sex_char = "des femmes et des hommes"
    nb_car = 30



filtered_columns = [col for col in filtered_data.columns if re.match(pattern_sex, col)]

filtered_data = filtered_data[filtered_columns]

filtered_data["CODGEO"] = data["CODGEO"]
filtered_data = filtered_data.merge(nom_commune[["code_insee", "nom_commune"]], 
                                     left_on="CODGEO", right_on="code_insee", 
                                     how="left").drop(columns=["code_insee"])
filtered_data = filtered_data.dropna(thresh=3).reset_index()
nom_var = filtered_meta_data["LIB_VAR_LONG"][filtered_meta_data["COD_VAR"].isin(filtered_data.columns)]


var_mapping = dict(zip(filtered_meta_data["COD_VAR"], filtered_meta_data["LIB_VAR_LONG"]))
df_melted = filtered_data.melt(id_vars=["nom_commune"], var_name="Catégorie", value_name="Valeur")
df_melted["Catégorie"] = df_melted["Catégorie"].map(var_mapping).str[nb_car:-12]
df_melted = df_melted.sort_values(by="Valeur", ascending=False)

def insert_line_breaks(text, max_length=30):
    """
    Insère un retour à la ligne (<br>) tous les 20 caractères dans une chaîne.
    
    :param text: la chaîne à traiter
    :param max_length: la longueur maximale avant d'insérer un <br>
    :return: la chaîne modifiée avec des retours à la ligne
    """
    return "<br>-".join([text[i:i+max_length] for i in range(0, len(text), max_length)])

df_melted["Catégorie"] = df_melted["Catégorie"].map(lambda x: insert_line_breaks(x) if isinstance(x, str) else x)
fig = px.bar(df_melted, x="nom_commune", y="Valeur", color="Catégorie", 
             labels={"Valeur": "Montant en euros", "nom_commune": "Nom de la Commune", "Catégorie": f"Salaire net moyen horaire {sex_char} en 2022"},
             title="Salaire en fonction des catégories et des communes en 2022",barmode="group")
st.write(fig)
st.markdown(
    "<p style='text-align: left; color: gray;'>"
    "Source : INSEE, Dossier Complet 2024</p>",
    unsafe_allow_html=True
)

df_grouped = df_melted.groupby("Catégorie")["Valeur"].mean().reset_index()
df_grouped["sexe"] = df_grouped["Catégorie"].apply(
    lambda x: "femme" if x[0].lower() == "f" else "homme" 
)
if(selection_sex=="comparaison homme femme"):
    df_grouped["categ"] = df_grouped["Catégorie"].apply(
        lambda x: "cadres, professions intellectuelles supérieures <br>et des chefs d'entreprises salariés" if x[7:9].lower() == "ca" else 
                "ouvriers" if x[7:9].lower() == "ou" else 
                "professions intermédiaires" if x[7:9].lower() == "ex" else
                "employés"
    )
    figue = px.bar(df_grouped, 
                x="categ", 
                y="Valeur", 
                color = "sexe",
                labels={"Valeur": "Montants des salaires en euros", "categ": "Catégorie"}, 
                title=f"Comparaisons du salaire {sex_char} en 2022 par catégorie socioprofessionnelle",barmode="group")
    st.write(figue)
    st.markdown(
        "<p style='text-align: left; color: gray;'>"
        "Source : INSEE, Dossier Complet 2024</p>",
        unsafe_allow_html=True
    )
else:
    figue = px.bar(df_grouped, 
                x="Catégorie", 
                y="Valeur", 
                color = "Catégorie",
                labels={"Valeur": "Montants des salaires en euros", "Catégorie": "Catégorie"}, 
                title=f"Salaire net moyen horaire {sex_char} en 2022 par catégorie")
    st.write(figue)
    st.markdown(
        "<p style='text-align: left; color: gray;'>"
        "Source : INSEE, Dossier Complet 2024</p>",
        unsafe_allow_html=True
    )