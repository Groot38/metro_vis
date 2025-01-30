import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json
import re

st.set_page_config(
    page_title="Tableau de Bord - Démographie Française",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache
def load_data():
    data = pd.read_csv("../data_insee/dossier_complet/dossier_complet.csv", sep=',')
    meta_data = pd.read_csv("../data_insee/dossier_complet/meta_dossier_complet.csv", sep=';')
    nom_commune = pd.read_csv("../data/communes.csv", sep=',')
    return data,meta_data,nom_commune

@st.cache_data
def load_geojson():
    with open("../data/iris_contours/contours_communes.geojson", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    return geojson_data

geojson_commune = load_geojson()


data,meta_data,nom_commune= load_data()
#st.write(data.head())

# Option, choix de la colonne et de l'année
st.sidebar.title("Options")
if st.sidebar.checkbox("Afficher les données brutes"):
    st.write(data)
selected_years = []
if st.sidebar.checkbox("2010"):
    selected_years.append("10")
if st.sidebar.checkbox("2015"):
    selected_years.append("15")
if st.sidebar.checkbox("2021"):
    selected_years.append("21")

# Construire dynamiquement le pattern pour les années sélectionnées
year_pattern = "|".join(selected_years)

# Générer le pattern dynamique
pattern = re.compile(f"^[PC]({year_pattern})_[a-zA-Z0-9]+$")

filtered_meta_data = meta_data[meta_data["COD_VAR"].astype(str).str.match(pattern)]
# Filtrage des données pour analyse
variables = filtered_meta_data["LIB_VAR_LONG"].unique()
variables = [var[:-8] for var in variables]

selected_variable = st.sidebar.selectbox("Choisissez une variable à analyser", variables)
visualization_type = st.sidebar.radio("Type de Visualisation", ["Carte Choroplèthe", "Histogramme", "Analyse par Catégorie"])



# Filtrer les données pour la variable choisie
meta_data["LIB_VAR_LONG_trimmed"] = filtered_meta_data["LIB_VAR_LONG"].str[:-8]
filtered_meta_data = meta_data[meta_data["LIB_VAR_LONG_trimmed"] == selected_variable]
cod_var = filtered_meta_data["COD_VAR"]

selected_columns = [col for col in data.columns if col in cod_var.values]

filtered_data = data[["CODGEO"] + selected_columns]
filtered_data = filtered_data.merge(nom_commune[["code_insee", "nom_commune"]], 
                                     left_on="CODGEO", right_on="code_insee", 
                                     how="left").drop(columns=["code_insee"])
st.write(filtered_data)



if visualization_type == "Carte Choroplèthe":
    st.subheader(f"Carte Choroplèthe : {selected_variable}")
    # Exemple de visualisation avec Plotly
    fig = px.choropleth(
        filtered_data,
        geojson=geojson_commune,
        locations="CODGEO",  # Code géographique (par exemple, code INSEE)
        featureidkey="properties.code",
        color=selected_columns[0],  # Colonne avec les valeurs numériques
        color_continuous_scale="Viridis",
        labels={selected_columns[0]: selected_variable},
        title=selected_variable
    )
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)

elif visualization_type == "Histogramme":
    st.subheader(f"Histogramme : {selected_variable}")

    # Vérification que des colonnes sont bien sélectionnées
    if not selected_columns:
        st.warning("Aucune année sélectionnée pour l'histogramme.")
    else:
        # Préparer les données pour Altair : transformation en format "long" (melt)
        
        melted_data = filtered_data.melt(
            id_vars=["nom_commune"],  # Maintenir CODGEO comme identifiant
            value_vars=selected_columns,  # Variables à "fondre"
            var_name="Variable",  # Nom de la colonne pour les années
            value_name="Valeur"  # Nom de la colonne pour les valeurs
        ).sort_values(by=["nom_commune","Variable"])
        num_lines = st.sidebar.number_input("Nombre de lignes à afficher", min_value=1, max_value=49, value=10)
    

        # Sélectionner les 'num_lines' premières lignes
        melted_data_tronc = melted_data.head(num_lines*3)
        st.write(melted_data_tronc)
        # Création du graphique en barres
        chart = alt.Chart(melted_data_tronc).mark_bar().encode(
            x=alt.X("nom_commune:N", title="Communes",axis=alt.Axis(labelAngle=-45),sort="-y"),  # Afficher CODGEO sur l'axe X
            y=alt.Y("Valeur:Q", title="Population", axis=alt.Axis(labelAngle=0)),  # Valeurs de la population sur l'axe Y
            color="Variable:N",  # Colorier selon la variable (P21_POP, P15_POP, P10_POP)
            xOffset="Variable:N"
        ).properties(
            title="Comparaison de "+selected_variable+" par commune et par année",
            width=150,  # Largeur de chaque barre
            height=650  # Hauteur du graphique
        ).configure_view(
            stroke=None  # Enlever les bordures autour des graphiques
        )

        st.altair_chart(chart, use_container_width=True)
        melted_group_data = melted_data.groupby('Variable')['Valeur'].sum().reset_index()
        melted_group_data["nom"]= ["Grenoble Alpes Metropole"]*3
        st.write(melted_group_data)
        chark = alt.Chart(melted_group_data).mark_bar(size=100).encode(
            x=alt.X("nom:N", title="Nom",axis=alt.Axis(labelAngle=-45),sort="-y"),  # Afficher CODGEO sur l'axe X
            y=alt.Y("Valeur:Q", title="Population", axis=alt.Axis(labelAngle=0)),  # Valeurs de la population sur l'axe Y
            color="Variable:N",  # Colorier selon la variable (P21_POP, P15_POP, P10_POP)
            xOffset="Variable:N"
        ).properties(
            title="Comparaison par année de "+selected_variable+" sur la métropole de Grenoble",
            width=650,  # Largeur de chaque barre
            height=650  # Hauteur du graphique
        ).configure_view(
            stroke=None  # Enlever les bordures autour des graphiques
        ).configure_scale(
            bandPaddingInner=0
        )

        st.altair_chart(chark, use_container_width=True)
        



elif visualization_type == "Analyse par Catégorie":
    st.subheader("Analyse par Catégorie")
    selected_category = st.selectbox("Choisissez une catégorie", filtered_data["LIB_MOD"].unique())
    category_data = filtered_data[filtered_data["LIB_MOD"] == selected_category]
    st.write(f"Données pour {selected_category}")
    st.write(category_data)
