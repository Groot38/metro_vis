import streamlit as st
import pandas as pd


st.title("Etude de consommation de Gaz")

#dépenses dans domaine environnement
# type dep T2 ; 
file_path_gaz = "../data/environnement/elec/conso-gaz-metropole.csv"
file_path_elec = "../data/environnement/elec/eco2mix-metropoles-tr.csv"
gaz = pd.read_csv(file_path_gaz,sep = ";")
elec = pd.read_csv(file_path_elec,sep = ";")

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

