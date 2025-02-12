import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import numpy as np



def meteo_page():
    st.title("Sous-page : Météo")
    st.write("Bienvenue dans la sous-page Météo.")
    if st.button("Retour"):
        st.session_state.page = "Environnement"

st.title("Etude de températures")

@st.cache_data
def load_data_meteo():
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


    return(df_2000_2005,df_2005_2010,df_2010_2015,df_2015_2020,df_2020_2025,df2_2000_2005,df2_2005_2010,df2_2010_2015,df2_2015_2020,df2_2020_2025)

df_2000_2005,df_2005_2010,df_2010_2015,df_2015_2020,df_2020_2025,df2_2000_2005,df2_2005_2010,df2_2010_2015,df2_2015_2020,df2_2020_2025=load_data_meteo()
df = pd.concat([df_2000_2005,df_2005_2010,df_2010_2015, df_2015_2020,df_2020_2025], ignore_index=True)
df2 = pd.concat([df2_2000_2005,df2_2005_2010,df2_2010_2015, df2_2015_2020,df2_2020_2025], ignore_index=True)

# 🗓️ Convertir la date en format datetime
df["aaaammjj"] = pd.to_datetime(df["aaaammjj"], format="%Y%m%d")
df2["aaaammjj"] = pd.to_datetime(df2["aaaammjj"], format="%Y%m%d")

#######################################################################################
st.subheader("Etude de températures globales sur 20 ans.")

col1, col2  = st.columns([2,1],vertical_alignment="top")
df["Moyenne Glissante"] = df.groupby("nom_usuel")["tntxm"].transform(lambda x: x.rolling(window=100, min_periods=50).mean())
df = df.rename(columns={"tntxm": "Moyenne entre la température min et max"})

with col1:
    # 🎨 Afficher le graphique avec et sans la moyenne glissante
    st.line_chart(df, x="aaaammjj", y=["Moyenne entre la température min et max", "Moyenne Glissante"], color="nom_usuel",x_label="Date",y_label="moyenne de températures en °C")

#######################

# 📌 Convertir les dates en format datetime
df["aaaammjj"] = pd.to_datetime(df["aaaammjj"])
df["Année"] = df["aaaammjj"].dt.year  # Extraire l'année

# 📈 Moyenne des températures par année
df_annee = df.groupby("Année")["Moyenne entre la température min et max"].mean().reset_index()

# 🔢 Calcul de la tendance linéaire avec NumPy
pente, intercept = np.polyfit(df_annee["Année"], df_annee["Moyenne entre la température min et max"], 1)

# 🔺 Calcul de l'augmentation totale sur la période
augmentation_temp = pente * (df_annee["Année"].max() - df_annee["Année"].min())

with col2:
    # 🎯 Affichage du chiffre clé avec Streamlit
    st.metric(
        label="Augmentation de la température sur la période",
        value=f"{augmentation_temp:.2f}°C",
        delta=f"{pente:.2f}°C/an",
        delta_color="inverse" if pente < 0 else "normal",
    )
    with st.expander("Infos"):
        st.write('''
            La tendance des températures au cours des années est positive.   
            Les températures augmentents en moyenne de :red[0.09 °C/an].  
            En 20 ans, la température a augmenté de :red[1.73 °C].
             ''')


######################

st.subheader("Etude de températures annuelles")

multi='''
            On observe mieux cette tendance en observant sur les moyennes annuelles.
             '''
st.markdown(multi)


# 📊 Graphique avec tendance
df_annee["Tendance Linéaire"] = intercept + pente * df_annee["Année"]
fig = px.line(df_annee, x="Année", y=["Moyenne entre la température min et max", "Tendance Linéaire"])

# 🎨 Mise à jour des labels des axes
fig.update_layout(
    xaxis_title="Année",
    yaxis_title="Moyenne de température annuelle (°C)",
    yaxis=dict(
        range=[0, 20]  # Limiter l'axe y entre 0 et 15
    )
)
st.plotly_chart(fig)


############################################""

df["année"] = df["aaaammjj"].dt.year
df2["année"] = df2["aaaammjj"].dt.year

df["mois"] = df["aaaammjj"].dt.month
df2["mois"] = df2["aaaammjj"].dt.month

stations_interessantes = ["GRENOBLE-CEA-RADOME", "ST-M-D'HERES-GALOCHERE"]  # Remplace par les num_poste que tu veux
df_filtré = df[df["nom_usuel"].isin(stations_interessantes)]


# 📊 Calculer la température moyenne par année et par station météo
df_temp_annuelle = df_filtré.groupby(["année","nom_usuel"])["Moyenne entre la température min et max"].mean().reset_index()

# 🖼️ Afficher les données
#st.write("Température moyenne annuelle par station météo :", df_temp_annuelle)

col1, col2  = st.columns([1,1],vertical_alignment="top")
with col1:
    with st.expander("Infos"):
        st.write('''
            Les données météo sont prises à partir de différents postes sur Grenoble. Certains postes ont étés mis en place plus tard.  
            Les températures peuvent différer selon la localisation du poste (proche montagne, cours d'eau ou pleine ville).
             ''')
    
    # 📊 Tracer le barchart
    st.bar_chart(df_temp_annuelle, x="année", y="Moyenne entre la température min et max", color="nom_usuel", stack=False, y_label="moyenne de températures en °C")


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

st.subheader("Etude de températures mensuelles")
# 📆 Dictionnaire des mois
mois_dict = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

# 🌍 Colonnes pour l'affichage
col1, col2,col3 = st.columns([1,2,2],vertical_alignment="top")

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
    df_filtré["Moyenne entre la température min et max"],
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


with col3:
    # 🎯 Calculer la moyenne de tntxm pour l'année et le mois sélectionnés
    moyenne_selectionnée = df_filtré["Moyenne entre la température min et max"].mean()

    # 📊 Calculer la moyenne des mêmes mois sur les autres années
    moyenne_autres_annees = df[df["mois"] == mois_selectionné]["Moyenne entre la température min et max"].mean()

    # 🔼🔽 Calculer la différence entre les deux moyennes
    variation = moyenne_selectionnée - moyenne_autres_annees

    # 🎨 Affichage avec st.metric
    st.metric(
        label=f"Moyenne de température ({mois_selectionné_nom} {année_selectionnée})",
        value=f"{moyenne_selectionnée:.2f}°C",
        delta=f"{variation:.2f}°C",
        delta_color="inverse" if variation < 0 else "normal",
    )
    with st.expander("Infos"):
        st.write('''
            En sélectionnant le mois de l'année d'intérêt, cette métrique indique la température moyenne du mois ainsi que l'écart de température avec la moyenne du même mois de toutes les autres années.  
            Cela vous indiquera si ce mois a été plus chaud ou plus froid que les mêmes mois des autres années.
            ''')
     # 📊 Calculer la moyenne de température par année pour le mois sélectionné
    df_moyennes_mois = df[df["mois"] == mois_selectionné].groupby("année")["Moyenne entre la température min et max"].mean().reset_index()



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

col11, col21 = st.columns([2,3],vertical_alignment="center")

with col11 : 
    # 🎨 Création du graphique avec Plotly
    fig = px.line(
        df_moyennes_mois, 
        x="année", 
        y="Moyenne entre la température min et max", 
        markers=True,
        title=f"📈 Températures moyennes en {mois_selectionné_nom} (toutes années)",
        labels={"Moyenne entre la température min et max": "Température moyenne (°C)", "année": "Année"},
        line_shape="linear",
        range_y=[-10, 35]
    )

    # 🖼️ Affichage du graphique dans Streamlit
    st.plotly_chart(fig)


st.link_button("Source Météo France", "https://meteo.data.gouv.fr/form")


#############################################################



