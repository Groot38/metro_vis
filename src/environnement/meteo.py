import streamlit as st
import pandas as pd

def meteo_page():
    st.title("Sous-page : Météo")
    st.write("Bienvenue dans la sous-page Météo.")
    if st.button("Retour"):
        st.session_state.page = "Environnement"



# 📂 Charger les données
file_path = "../data/environnement/clim-base_quot_vent-38-2019-2024.csv"
df = pd.read_csv(file_path)

# 🗓️ Convertir la date en format datetime
df["aaaammjj"] = pd.to_datetime(df["aaaammjj"], format="%Y%m%d")

# 📊 Calculer la température moyenne par "yyyymm" et par station météo
df_temp_par_jours = df.groupby(["aaaammjj", "num_poste"])["tm"].mean().reset_index()

# 🖼️ Afficher les données
st.write("Température moyenne par jours et par station météo :", df_temp_par_jours)

# 📈 Tracer le graphique
st.line_chart(df_temp_par_jours, x="aaaammjj", y="tm", color="num_poste")






df["année"] = df["aaaammjj"].dt.year

stations_interessantes = [38538002, 38472403]  # Remplace par les num_poste que tu veux
df_filtré = df[df["num_poste"].isin(stations_interessantes)]


# 📊 Calculer la température moyenne par année et par station météo
df_temp_annuelle = df_filtré.groupby(["année", "num_poste"])["tampli"].mean().reset_index()

# 🖼️ Afficher les données
st.write("Température moyenne annuelle par station météo :", df_temp_annuelle)

# 📊 Tracer le barchart
st.bar_chart(df_temp_annuelle, x="année", y="tampli", color="num_poste", stack=False)

