import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk


def meteo_page():
    st.title("Sous-page : Météo")
    st.write("Bienvenue dans la sous-page Météo.")
    if st.button("Retour"):
        st.session_state.page = "Environnement"

st.title("Etude de températures")

# 📂 Charger les données
file_path = "../data/environnement/clim-base_quot_vent-38-2019-2024.csv"
file_path2 = "../data/environnement/clim-base_quot_autres-38-2019-2024.csv"
df = pd.read_csv(file_path)
df2 = pd.read_csv(file_path2)

# 🗓️ Convertir la date en format datetime
df["aaaammjj"] = pd.to_datetime(df["aaaammjj"], format="%Y%m%d")
df2["aaaammjj"] = pd.to_datetime(df2["aaaammjj"], format="%Y%m%d")


# 📊 Calculer la température moyenne par "yyyymm" et par station météo
df_temp_par_jours = df.groupby(["aaaammjj", "num_poste"])["tm"].mean().reset_index()

# 🖼️ Afficher les données
#st.write("Température moyenne par jours et par station météo :", df_temp_par_jours)

# 📈 Tracer le graphique
st.line_chart(df_temp_par_jours, x="aaaammjj", y="tm", color="num_poste")


############################################""

df["année"] = df["aaaammjj"].dt.year
df2["année"] = df2["aaaammjj"].dt.year

df["mois"] = df["aaaammjj"].dt.month
df2["mois"] = df2["aaaammjj"].dt.month

stations_interessantes = ["GRENOBLE-CEA-RADOME", "GRENOBLE - LVD"]  # Remplace par les num_poste que tu veux
df_filtré = df[df["nom_usuel"].isin(stations_interessantes)]


# 📊 Calculer la température moyenne par année et par station météo
df_temp_annuelle = df_filtré.groupby(["année","nom_usuel"])["tm"].mean().reset_index()

# 🖼️ Afficher les données
#st.write("Température moyenne annuelle par station météo :", df_temp_annuelle)

col1, col2  = st.columns([1,1])

with col1:
    # 📊 Tracer le barchart
    st.bar_chart(df_temp_annuelle, x="année", y="tm", color="nom_usuel", stack=False)

with col2:
    layer = pdk.Layer(
    "ScatterplotLayer",  # Type de couche : Scatterplot pour les points
    df_filtré,  # Données filtrées
    get_position=["lon", "lat"],  # Latitude et Longitude
    get_radius=500,  # Taille des points
    get_fill_color=[255, 0, 0, 140],  # Couleur des points (rouge semi-transparent)
    pickable=True,  # Activer la possibilité de cliquer
    auto_highlight=True,  # Activer l'effet au survol
    )

    # Vue de la carte avec pydeck
    view_state = pdk.ViewState(latitude=df_filtré["lat"].mean(), longitude=df_filtré["lon"].mean(), zoom=9)

    # Tooltip pour afficher le nom de la station dans l'infobulle
    tooltip = {
        "html": "<b>Nom du poste :</b> {nom_usuel}",  # Afficher la valeur de 'nom_usuel' dans l'infobulle
        "style": {"backgroundColor": "white", "color": "black"}  # Style de l'infobulle
    }

    # Carte avec pydeck
    deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)

    # Affichage de la carte dans Streamlit
    st.pydeck_chart(deck)

###################################################

col1, col2,col3 = st.columns([1, 2,2])

# 🎯 Filtrer les données pour la station GRENOBLE-CEA-RADOME
dfGRE = df[df["nom_usuel"] == "GRENOBLE-CEA-RADOME"]

# 📆 Dictionnaire des mois
mois_dict = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

with col1:
    # 🎛️ Sélecteurs pour l'année et le mois
    année_selectionnée = st.selectbox("Sélectionnez une année", sorted(dfGRE["année"].unique(), reverse=True))

    # 🔄 Mapper les mois avec leurs noms
    mois_options = {mois_dict[m]: m for m in sorted(dfGRE["mois"].unique())}

    # 📌 Sélectionner un mois avec affichage des noms mais stockage des chiffres
    mois_selectionné_nom = st.selectbox("Sélectionnez un mois", list(mois_options.keys()))
    mois_selectionné = mois_options[mois_selectionné_nom]

# 📌 Filtrer les données selon l'année et le mois sélectionnés
df_filtréGRE = dfGRE[(dfGRE["année"] == année_selectionnée) & (dfGRE["mois"] == mois_selectionné)]

# 🏷️ Catégoriser les températures
df_filtréGRE["Catégorie Température"] = pd.cut(
    df_filtréGRE["tm"],
    bins=[-float("inf"), 5, 15, 25, float("inf")],
    labels=["< 5°C", "5-15°C", "15-25°C", "> 25°C"]
)

# 📊 Compter les jours dans chaque catégorie
df_pie = df_filtréGRE["Catégorie Température"].value_counts().reset_index()
df_pie.columns = ["Catégorie Température", "Nombre de jours"]

# 🎨 Définition d'une palette de couleurs
color_map = {
    "< 5°C": "#3498db",  # Bleu
    "5-15°C": "#2ecc71",  # Vert
    "15-25°C": "#f1c40f",  # Jaune
    "> 25°C": "#e74c3c"  # Rouge
}

with col2:
    # 🎨 Création du camembert avec Plotly
    fig = px.pie(
        df_pie, 
        values="Nombre de jours", 
        names="Catégorie Température", 
        title=f"🌡 Répartition des températures en {mois_selectionné_nom} {année_selectionnée} à GRENOBLE-CEA-RADOME",
        color="Catégorie Température",
        color_discrete_map=color_map
    )

    # 🖼️ Affichage du camembert dans Streamlit
    st.plotly_chart(fig)
