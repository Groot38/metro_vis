import streamlit as st
import pandas as pd

file_path = "../data/environnement/covoiturage.csv"  # 📂 Adapter le chemin
df = pd.read_csv(file_path)

# Définir un mapping de couleurs correct
color_mapping = {
    "Parking": "#FF8000",  # orange
    "Parking relais": "#FF00FF",  # violet
    "Aire de covoiturage": "#00FFFF",  # Bleu
}

# Appliquer les couleurs
df["color"] = df["type"].map(color_mapping).fillna("#808080")  # Gris par défaut

# Afficher la carte avec st.map()
st.map(df, latitude="ylat", longitude="xlong", color="color")

