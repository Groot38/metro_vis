import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


@st.cache_data
def load_data_full():
    file_path_full_data = "../data/environnement/devdurable/5.16-ITDD-Auvergne-Rhone-Alpes-Toutes-les-communes.2024-01.csv"
    df_full = pd.read_csv(file_path_full_data,sep = ";")
    return(df_full)

df_full = load_data_full()

df_full_bis = df_full.drop(df_full.index[[0]])

critair_post = df_full_bis[df_full_bis["Libellé de la variable"]=="Nombre de voitures particulières immatriculés selon énergie et vignette Crit’Air"]
critair = critair_post[["COG_COMMUNE - Libellé de la zone","Libellé du sous-champ","A2013","A2014","A2015","A2016","A2017","A2018","A2019","A2020","A2021","A2022","A2023"]]


# 📌 Sélectionner un critère
critères_disponibles = critair["Libellé du sous-champ"].unique()
critère_selectionné = st.selectbox("Sélectionnez un critère :", critères_disponibles)

# 📌 Filtrer les données selon le critère sélectionné
critair_filtré = critair[critair["Libellé du sous-champ"] == critère_selectionné]

# 🔄 Restructurer le dataframe pour avoir "Année" en colonne (Melt)
critair_melted = critair_filtré.melt(id_vars=["COG_COMMUNE - Libellé de la zone", "Libellé du sous-champ"], var_name="Année", value_name="Valeur")

# 📈 Tracer la courbe par ville
fig = px.line(
    critair_melted, 
    x="Année", 
    y="Valeur", 
    color="COG_COMMUNE - Libellé de la zone",  
    markers=True, 
    title=f"Évolution de {critère_selectionné} par ville",
    labels={"Valeur": critère_selectionné, "Année": "Année"}
)

# 📊 Affichage dans Streamlit
st.plotly_chart(fig)