import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px



st.title("Etude de consommation de Gaz")

#dépenses dans domaine environnement
# type dep T2 ; 
@st.cache_data
def load_data_energie():
    file_path_gaz = "../data/environnement/elec/conso-gaz-metropole.csv"
    file_path_elec = "../data/environnement/elec/eco2mix-metropoles-tr.csv"
    gaz = pd.read_csv(file_path_gaz,sep = ";")
    elec = pd.read_csv(file_path_elec,sep = ";")
    file_path_elec_bat = "../data/environnement/elec/consommation_elec_grenoble_2012_2022.csv"
    elec_bat = pd.read_csv(file_path_elec_bat, sep=",")
    file_path_elec_tot = "../data/environnement/elec/consommation-annuelle-d-electricite-et-gaz-par-commune(1).csv"
    elec_tot = pd.read_csv(file_path_elec_tot, sep=";")
    return(gaz,elec,elec_bat,elec_tot)

gaz,elec,elec_bat,elec_tot = load_data_energie()

gaz["Date"] = pd.to_datetime(gaz["Date"], format="%Y-%m")
elec["Date"] = pd.to_datetime(elec["Date"], format="%Y-%m-%d")



st.bar_chart(gaz,x="Date", y= "Consommation de gaz (en KWh PCS 0°C)")



st.title("Etude de consommation d'Electricité")

# Extraire l'année et le mois pour regrouper les données
elec["Année-Mois"] = elec["Date"].dt.to_period("M")

# Calculer la moyenne par mois
elec_mensuel = elec.groupby("Année-Mois")["Consommation (MW)"].mean().reset_index()

elec_mensuel["Année-Mois"] = elec_mensuel["Année-Mois"].dt.to_timestamp()


# Graphique
st.bar_chart(elec_mensuel, x="Année-Mois", y="Consommation (MW)")

#############################################################################

# 📂 Charger les données


# 📆 Convertir la colonne date_releve en datetime
elec_bat["date_releve"] = pd.to_datetime(elec_bat["date_releve"])

# 📅 Extraire année uniquement
elec_bat["Année"] = elec_bat["date_releve"].dt.to_period("Y")

# 🔢 Convertir la colonne "quantite_kwh" en float
elec_bat["quantite_kwh"] = pd.to_numeric(elec_bat["quantite_kwh"], errors="coerce")

# 📊 Calcul de la moyenne annuelle par catégorie
elec_annuel_bat = elec_bat.groupby(["Année", "libelle_niv__4"])["quantite_kwh"].mean().reset_index()

# 🔄 Convertir Année en datetime pour Plotly
elec_annuel_bat["Année"] = elec_annuel_bat["Année"].dt.to_timestamp()

col1, col2  = st.columns([1,4],vertical_alignment="center")

with col1 : 
    # 🎛️ Sélecteur pour choisir UNE SEULE catégorie à afficher
    libelles_disponibles = elec_annuel_bat["libelle_niv__4"].unique()
    libelle_selectionne = st.selectbox("Sélectionnez une catégorie à afficher :", libelles_disponibles)

# 📌 Filtrer les données selon la catégorie choisie
elec_filtré = elec_annuel_bat[elec_annuel_bat["libelle_niv__4"] == libelle_selectionne]

with col2 :
    # 📊 Créer un bar chart avec la catégorie sélectionnée
    fig = px.bar(
        elec_filtré, 
        x="Année", 
        y="quantite_kwh",  
        title=f"Consommation annuelle d'électricité - {libelle_selectionne}",
        color_discrete_sequence=["#3498db"]  # Bleu pour un style épuré
    )

    # 📈 Afficher dans Streamlit
    st.plotly_chart(fig)


########################################################################################



col3, col4  = st.columns([1,4],vertical_alignment="center")


with col3 :
    # 🎛️ Sélecteur pour choisir les secteurs à afficher
    secteurs_disponibles = elec_tot["FILIERE"].unique()
    secteur_selectionné = st.selectbox("Sélectionnez un secteur :", secteurs_disponibles)
    filieres_disponibles = elec_tot["CODE GRAND SECTEUR"].unique()
    filieres_selectionnees = st.multiselect("Sélectionnez les filières à afficher :", filieres_disponibles, default=filieres_disponibles)

# 📌 Filtrer les données selon le secteur sélectionné
elec_tot_filtré = elec_tot[(elec_tot["FILIERE"] == secteur_selectionné) & (elec_tot["CODE GRAND SECTEUR"].isin(filieres_selectionnees))]

with col4 :
    # 📊 Création du barplot empilé
    fig = px.bar(
        elec_tot_filtré, 
        x="Année", 
        y="Conso totale (MWh)",  
        color="CODE GRAND SECTEUR",  # FILIERE sera empilé
        barmode="stack",  # Empilement des filières
        title=f"Consommation par année pour {secteur_selectionné}"
    )

    # 📈 Affichage dans Streamlit
    st.plotly_chart(fig)