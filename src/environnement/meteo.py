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
file_path_vent_2000_2005 = "../data/environnement/meteo/clim-base_quot_vent-38-2000-2005.csv"
file_path_vent_2005_2010 = "../data/environnement/meteo/clim-base_quot_vent-38-2005-2010.csv"
file_path_vent_2010_2015 = "../data/environnement/meteo/clim-base_quot_vent-38-2010-2015.csv"
file_path_vent_2015_2020 = "../data/environnement/meteo/clim-base_quot_vent-38-2015-2020.csv"
file_path_vent_2020_2025 = "../data/environnement/meteo/clim-base_quot_vent-38-2020-2025.csv"

file_path_autre_2000_2005 = "../data/environnement/meteo/clim-base_quot_autres-38-2000-2005.csv"
file_path_autre_2005_2010 = "../data/environnement/meteo/clim-base_quot_autres-38-2005-2010.csv"
file_path_autre_2010_2015 = "../data/environnement/meteo/clim-base_quot_autres-38-2010-2015.csv"
file_path_autre_2015_2020 = "../data/environnement/meteo/clim-base_quot_autres-38-2015-2020.csv"
file_path_autre_2020_2025 = "../data/environnement/meteo/clim-base_quot_autres-38-2020-2025.csv"

df_2000_2005 = pd.read_csv(file_path_vent_2010_2015)
df_2005_2010 = pd.read_csv(file_path_vent_2005_2010)
df_2010_2015 = pd.read_csv(file_path_vent_2010_2015)
df_2015_2020 = pd.read_csv(file_path_vent_2015_2020)
df_2020_2025 = pd.read_csv(file_path_vent_2020_2025)

df2_2000_2005 = pd.read_csv(file_path_vent_2000_2005)
df2_2005_2010 = pd.read_csv(file_path_vent_2005_2010)
df2_2010_2015 = pd.read_csv(file_path_autre_2010_2015)
df2_2015_2020 = pd.read_csv(file_path_autre_2015_2020)
df2_2020_2025 = pd.read_csv(file_path_autre_2020_2025)


df = pd.concat([df_2000_2005,df_2005_2010,df_2010_2015, df_2015_2020,df_2020_2025], ignore_index=True)
df2 = pd.concat([df2_2000_2005,df2_2005_2010,df2_2010_2015, df2_2015_2020,df2_2020_2025], ignore_index=True)

# 🗓️ Convertir la date en format datetime
df["aaaammjj"] = pd.to_datetime(df["aaaammjj"], format="%Y%m%d")
df2["aaaammjj"] = pd.to_datetime(df2["aaaammjj"], format="%Y%m%d")


df["Moyenne Glissante"] = df.groupby("nom_usuel")["tntxm"].transform(lambda x: x.rolling(window=50, min_periods=1).mean())


# 🎨 Afficher le graphique avec et sans la moyenne glissante
st.line_chart(df, x="aaaammjj", y=["tntxm", "Moyenne Glissante"], color="nom_usuel",x_label="Date",y_label="moyenne de températures en °C")


############################################""

df["année"] = df["aaaammjj"].dt.year
df2["année"] = df2["aaaammjj"].dt.year

df["mois"] = df["aaaammjj"].dt.month
df2["mois"] = df2["aaaammjj"].dt.month

stations_interessantes = ["GRENOBLE-CEA-RADOME", "ST-M-D'HERES-GALOCHERE"]  # Remplace par les num_poste que tu veux
df_filtré = df[df["nom_usuel"].isin(stations_interessantes)]


# 📊 Calculer la température moyenne par année et par station météo
df_temp_annuelle = df_filtré.groupby(["année","nom_usuel"])["tntxm"].mean().reset_index()

# 🖼️ Afficher les données
#st.write("Température moyenne annuelle par station météo :", df_temp_annuelle)

col1, col2  = st.columns([2,1],vertical_alignment="center")

with col1:
    # 📊 Tracer le barchart
    st.bar_chart(df_temp_annuelle, x="année", y="tntxm", color="nom_usuel", stack=False, y_label="moyenne de températures en °C")

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
        "html": "<b>Poste :</b> {nom_usuel}",  # Afficher la valeur de 'nom_usuel' dans l'infobulle
        "style": {"backgroundColor": "white", "color": "black"}  # Style de l'infobulle
    }

    # Carte avec pydeck
    deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)

    # Affichage de la carte dans Streamlit
    st.pydeck_chart(deck)

###################################################

# 📆 Dictionnaire des mois
mois_dict = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

# 🌍 Colonnes pour l'affichage
col1, col2, col3 = st.columns([1, 2, 2])

with col1:
    # 🎛️ Sélecteur d'année
    année_selectionnée = st.selectbox("Sélectionnez une année", sorted(df["année"].unique(), reverse=True))

    # 🎯 Filtrer les stations disponibles pour cette année
    stations_disponibles = df[df["année"] == année_selectionnée]["nom_usuel"].unique()

    if len(stations_disponibles) > 1:
        # Si plusieurs stations, afficher un sélecteur
        station_selectionnée = st.selectbox("Sélectionnez une station météo", stations_disponibles)
    else:
        # Si une seule station, la sélectionner automatiquement
        station_selectionnée = stations_disponibles[0]
        st.write(f"📍 Station sélectionnée automatiquement : **{station_selectionnée}**")

    # 🎯 Filtrer les données pour la station sélectionnée
    df_station = df[df["nom_usuel"] == station_selectionnée]

    # 🔄 Mapper les mois avec leurs noms
    mois_options = {mois_dict[m]: m for m in sorted(df_station["mois"].unique())}

    # 📌 Sélectionner un mois avec affichage des noms mais stockage des chiffres
    mois_selectionné_nom = st.selectbox("Sélectionnez un mois", list(mois_options.keys()))
    mois_selectionné = mois_options[mois_selectionné_nom]

# 📌 Filtrer les données selon l'année, le mois et la station sélectionnés
df_filtré = df_station[(df_station["année"] == année_selectionnée) & (df_station["mois"] == mois_selectionné)]

# 🏷️ Catégoriser les températures
df_filtré["Catégorie Température"] = pd.cut(
    df_filtré["tntxm"],
    bins=[-float("inf"), 5, 15, 25, float("inf")],
    labels=["< 5°C", "5-15°C", "15-25°C", "> 25°C"]
)

# 📊 Compter les jours dans chaque catégorie
df_pie = df_filtré["Catégorie Température"].value_counts().reset_index()
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
        title=f"🌡 Répartition des températures en {mois_selectionné_nom} {année_selectionnée} à {station_selectionnée}",
        color="Catégorie Température",
        color_discrete_map=color_map
    )

    # 🖼️ Affichage du camembert dans Streamlit
    st.plotly_chart(fig)

with col3:
    # 🎯 Calculer la moyenne de tntxm pour l'année et le mois sélectionnés
    moyenne_selectionnée = df_filtré["tntxm"].mean()

    # 📊 Calculer la moyenne des mêmes mois sur les autres années
    moyenne_autres_annees = df[df["mois"] == mois_selectionné]["tntxm"].mean()

    # 🔼🔽 Calculer la différence entre les deux moyennes
    variation = moyenne_selectionnée - moyenne_autres_annees

    # 🎨 Affichage avec st.metric
    st.metric(
        label=f"Moyenne de température ({mois_selectionné_nom} {année_selectionnée})",
        value=f"{moyenne_selectionnée:.2f}°C",
        delta=f"{variation:.2f}°C",
        delta_color="inverse" if variation < 0 else "normal",
    )
     # 📊 Calculer la moyenne de température par année pour le mois sélectionné
    df_moyennes_mois = df[df["mois"] == mois_selectionné].groupby("année")["tntxm"].mean().reset_index()

    # 🎨 Création du graphique avec Plotly
    fig = px.line(
        df_moyennes_mois, 
        x="année", 
        y="tntxm", 
        markers=True,
        title=f"📈 Températures moyennes en {mois_selectionné_nom} (toutes années)",
        labels={"tntxm": "Température moyenne (°C)", "année": "Année"},
        line_shape="linear",
        range_y=[-10, 35]
    )

    # 🖼️ Affichage du graphique dans Streamlit
    st.plotly_chart(fig)
