import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json
import re
import matplotlib.pyplot as plt
from utils import load_data,load_geojson
import numpy as np
import plotly.graph_objects as go


geojson_commune = load_geojson()
data,meta_data,nom_commune= load_data()

#st.write(data.head())
visualization_type = st.sidebar.radio("Type de Visualisation", ["Population par commune", "Evolution de la population","Repartition par âge"])

# Option, choix de la colonne et de l'année
st.sidebar.title("Options")
if st.sidebar.checkbox("Afficher les données brutes"):
    st.write(data)
selected_years = []
if st.sidebar.checkbox("2010",value = True):
    selected_years.append("10")
if st.sidebar.checkbox("2015",value = True):
    selected_years.append("15")
if st.sidebar.checkbox("2021",value = True):
    selected_years.append("21")

if selected_years == []:
    selected_years.append("21")
# Construire dynamiquement le pattern pour les années sélectionnées
year_pattern = "|".join(selected_years)

selection_sex = st.sidebar.radio(
    "",
    ("Les deux", "Homme", "Femme"),
)

# Affichage du bouton sélectionné
if selection_sex  == "Homme":
    pattern_sex = re.compile(f"^[P]({year_pattern})_(POPH|H)(0014|1529|3044|4559|6074|7589|90P|^$)*$")
    st.session_state["selected_variable"] = None
elif selection_sex  == "Femme":
    pattern_sex = re.compile(f"^[P]({year_pattern})_(POPF|F)(0014|1529|3044|4559|6074|7589|90P|^$)*$")
    st.session_state["selected_variable"] = None
else:
    pattern_sex = re.compile(f"^[P]({year_pattern})_(POP)(0014|1529|3044|4559|6074|7589|90P|^$)*$")
    st.session_state["selected_variable"] = None
# Premier filtre
pattern = re.compile(f"^[P]({year_pattern})_(POP|F|H)(H|F|[0-9]|$)[a-zA-Z0-9]*$")
filtered_meta_data = meta_data[meta_data["COD_VAR"].astype(str).str.match(pattern)]
# Deuxième filtre sur le sexe
filtered_meta_data = meta_data[meta_data["COD_VAR"].astype(str).str.match(pattern_sex)]
meta_data_age_répartition = filtered_meta_data
# Filtrage des données pour analyse
variables = filtered_meta_data["LIB_VAR_LONG"]
variables=list(dict.fromkeys(var[:-8] for var in variables))

if "selected_variable" not in st.session_state or st.session_state["selected_variable"] == None: 
    selected_variable = st.sidebar.selectbox("Choisissez une catégorie à analyser", variables,index = 0)
    st.session_state["selected_variable"] = selected_variable
else :
    selected_variable = st.sidebar.selectbox("Choisissez une catégorie à analyser",variables,index = variables.index(st.session_state["selected_variable"]))
    st.session_state["selected_variable"] = selected_variable



# Filtrer les données pour la variable choisie
filtered_meta_data["LIB_VAR_LONG_trimmed"] = filtered_meta_data["LIB_VAR_LONG"].str[:-8]
filtered_meta_data = filtered_meta_data[filtered_meta_data["LIB_VAR_LONG_trimmed"] == selected_variable]
cod_var = filtered_meta_data["COD_VAR"]

selected_columns = [col for col in data.columns if col in cod_var.values]

filtered_data = data[["CODGEO"] + selected_columns]
filtered_data = filtered_data.merge(nom_commune[["code_insee", "nom_commune"]], 
                                     left_on="CODGEO", right_on="code_insee", 
                                     how="left").drop(columns=["code_insee"])


###############################################################################################################
if visualization_type == "Population par commune":
    st.subheader(f"Cartes de la Métropole de Grenoble en fonction de : {selected_variable}")
    colpop, colage  = st.columns([1,1],vertical_alignment="center")
    with colpop:
        # Exemple de visualisation avec Plotly
        color_scale = [
                [0, "white"],  # Rouge pour les plus petites valeurs
                [1, "blue"]  # Vert pour les grandes valeurs
            ]
        fig = px.choropleth_mapbox(
            filtered_data,
            geojson=geojson_commune,
            locations="CODGEO",  # Code géographique (par exemple, code INSEE)
            featureidkey="properties.code",
            color=selected_columns[0],  # Colonne avec les valeurs numériques
            color_continuous_scale=color_scale,
            labels={selected_columns[0]: "Population",
                    "nom_commune" : "Commune"},
            title=f"{selected_variable} par commune en {"20" + max(selected_years)}",
            hover_data={"CODGEO": False, "nom_commune": True}
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            mapbox_style="open-street-map",  # Fond de carte OSM
            mapbox_zoom=9,  # Zoom initial, ajuste selon besoin
            mapbox_center={"lat": 45.166672, "lon": 5.71667},
            height=700  # Centre de la France (ajuste selon tes données)
        )
        fig.update_traces(marker=dict(opacity=0.7))
        st.plotly_chart(fig)
        st.markdown(
            "<p style='text-align: left; color: gray; margin-top: -80px;'>"
            "Source : INSEE, Dossier Complet 2024</p><br><br>",
            unsafe_allow_html=True
        )

    if len(selected_years) > 1 :
        filtered_data["evolution"] = (filtered_data.iloc[:,1]/filtered_data.iloc[:,2])

        min_val = min(filtered_data["evolution"])
        max_val = max(filtered_data["evolution"])

        # Palette personnalisée pour les couleurs
        color_scale = [
            [0, "red"],  # Rouge pour les plus petites valeurs
            [(1 - min_val) / (max_val - min_val), "white"],  # Blanc autour de 1
            [1, "green"]  # Vert pour les grandes valeurs
        ]
        
        # Exemple de visualisation avec Plotly
        nb_annee = len(selected_years)
        with colage:
            figue = px.choropleth_mapbox(
                filtered_data,
                geojson=geojson_commune,
                locations="CODGEO",  # Code géographique (par exemple, code INSEE)
                featureidkey="properties.code",
                color="evolution",  # Colonne avec les valeurs numériques
                color_continuous_scale=color_scale,
                labels={"evolution": "Évolution",
                        "nom_commune" : "Commune"},
                title=f"Evolution * de {selected_variable} par commune entre 20{selected_years[nb_annee-2]} et 20{selected_years[nb_annee-1]}",
                hover_data={"CODGEO": False, "nom_commune": True}
            )
            figue.update_geos(fitbounds="locations", visible=False)
            figue.update_layout(
                mapbox_style="open-street-map",  # Fond de carte OSM
                mapbox_zoom=9,  # Zoom initial, ajuste selon besoin
                mapbox_center={"lat": 45.166672, "lon": 5.71667},
                height=700  # Centre de la France (ajuste selon tes données)
            )
            figue.update_traces(marker=dict(opacity=0.7))
            st.plotly_chart(figue)
            st.markdown(
                "<p style='text-align: left; color: gray; margin-top: -80px;'>"
                "L'évolution a été calculé en faisant le rapport des années sélectionnées <br>"
                "Source : INSEE, Dossier Complet 2024</p>",
                unsafe_allow_html=True
            )
    
    # Carte de la moyenne d'age par commune :
    # Calcul de la moyenne d'age par commune
    cod_var = meta_data_age_répartition["COD_VAR"]
    selected_columns = [col for col in data.columns if col in cod_var.values]

    filtered_data = data[["CODGEO"] + selected_columns]
    filtered_data = filtered_data.merge(nom_commune[["code_insee", "nom_commune"]], 
                                        left_on="CODGEO", right_on="code_insee", 
                                        how="left").drop(columns=["code_insee"])
    
    #vecteurs des centres de chaque catégorie :
    centres = [7, 22, 37, 52, 67, 82, 92]
    filtered_data["age_moy"] = np.dot(filtered_data.iloc[:,2:9],centres)/ filtered_data.iloc[:,1]
    color_scale = [
            [0, "limegreen"],
            [0.5, "forestgreen"],
            [1, "darkred"]
        ]
    
    
    abricot = px.choropleth_mapbox(
        filtered_data,
        geojson=geojson_commune,
        locations="CODGEO",  # Code géographique (par exemple, code INSEE)
        featureidkey="properties.code",
        color="age_moy",  # Colonne avec les valeurs numériques
        color_continuous_scale=color_scale,
        title = f"Moyenne d'âge{' ' if selection_sex == 'Les deux' else " des "+selection_sex + 's'} par commune en {'20' + max(selected_years)}",
        labels={"age_moy" : "Âge moyen",
                "nom_commune" : "Commune"},
        hover_data={"CODGEO": False, "nom_commune": True}
    )
    abricot.update_geos(fitbounds="locations", visible=False)
    abricot.update_layout(
        mapbox_style="open-street-map",  # Fond de carte OSM
        mapbox_zoom=9,  # Zoom initial, ajuste selon besoin
        mapbox_center={"lat": 45.166672, "lon": 5.71667},
        height=700  # Centre de la France (ajuste selon tes données)
    )
    abricot.update_traces(marker=dict(opacity=0.7))
    st.plotly_chart(abricot)
    st.markdown(
        "<p style='text-align: left; color: gray; margin-top: -80px;'>"
        "La moyenne est une estimation calculée à partir des catégories d'âge de la population <br>"
        "Source : INSEE, Dossier Complet 2024</p>",
        unsafe_allow_html=True
    )
################################################################################################################
elif visualization_type == "Evolution de la population":
    st.subheader(f"Histogramme : {selected_variable}")

    # Vérification que des colonnes sont bien sélectionnées
    if not selected_columns:
        st.warning("Aucune année sélectionnée pour l'histogramme.")
    else:
        # Préparer les données pour Altair : transformation en format "long" (melt)
        
        filtered_data["rank"] = filtered_data.iloc[:,1].rank(method="min",ascending=False)
        
        melted_data = filtered_data.melt(
            id_vars=["nom_commune"],  # Maintenir CODGEO comme identifiant
            value_vars=selected_columns,  # Variables à "fondre"
            var_name="Variable",  # Nom de la colonne pour les années
            value_name="Valeur"  # Nom de la colonne pour les valeurs
        )#.sort_values(by=["nom_commune","Variable"])
        # Répéter les rangs pour chaque variable de la même commune

        melted_data["Rank"] = melted_data["nom_commune"].map(filtered_data.set_index("nom_commune")["rank"])

        # Trier proprement le tableau comme souhaité
        melted_data = melted_data.sort_values(by=["Rank", "nom_commune", "Variable"])

        num_lines = st.sidebar.number_input("Nombre de lignes à afficher", min_value=1, max_value=49, value=10)
    
        custom_labels = {
        "21": "2021",
        "15": "2015",
        "10": "2010"
        }
        melted_data["Legende"] = melted_data["Variable"].str[1:3].replace(custom_labels)
        # Sélectionner les 'num_lines' premières lignes
        melted_data_tronc = melted_data.head(num_lines*len(selected_years))
        
        # Création du graphique en barres
        chart = alt.Chart(melted_data_tronc).mark_bar().encode(
            x=alt.X("nom_commune:N", title="Communes",axis=alt.Axis(labelAngle=90),sort="-y"),  # Afficher CODGEO sur l'axe X
            y=alt.Y("Valeur:Q", title="Population", axis=alt.Axis(labelAngle=0)),  # Valeurs de la population sur l'axe Y
            color="Legende:N",  # Colorier selon la variable (P21_POP, P15_POP, P10_POP)
            xOffset="Variable:N"
        ).properties(
            title="Comparaison de "+selected_variable+" par commune et par année",
            width=150,  # Largeur de chaque barre
            height=650  # Hauteur du graphique
        ).configure_view(
            stroke=None  # Enlever les bordures autour des graphiques
        )

        st.altair_chart(chart, use_container_width=True)
        st.markdown(
            "<p style='text-align: left; color: gray; margin-top: -80px;'>"
            "Source : INSEE, Dossier Complet 2024</p>",
            unsafe_allow_html=True
        )


        melted_group_data = melted_data.groupby('Variable')['Valeur'].sum().reset_index()
        melted_group_data["nom"]= ["Grenoble Alpes Metropole"]*len(selected_years)


        melted_group_data["Legende"] = melted_group_data["Variable"].str[1:3].replace(custom_labels)
        
        chark = alt.Chart(melted_group_data).mark_bar(size=100).encode(
            x=alt.X("nom:N", title="Année",axis=alt.Axis(labelAngle=0),sort="-y"),  # Afficher CODGEO sur l'axe X
            y=alt.Y("Valeur:Q", title="Population", axis=alt.Axis(labelAngle=0)),  # Valeurs de la population sur l'axe Y
            color="Legende:N",  # Colorier selon la variable (P21_POP, P15_POP, P10_POP)
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
        st.markdown(
            "<p style='text-align: left; color: gray;'>"
            "Source : INSEE, Dossier Complet 2024</p>",
            unsafe_allow_html=True
        )

elif visualization_type == "Repartition par âge":
    filtered_meta_data = meta_data[meta_data["COD_VAR"].astype(str).str.match(pattern_sex)]
    pattern_pie = re.compile(f"^[P]({year_pattern})_\\w+\\d+$")
    filtered_meta_data = filtered_meta_data[filtered_meta_data["COD_VAR"].astype(str).str.match(pattern_pie)]
    variables = filtered_meta_data["LIB_VAR_LONG"]
    variables=list(dict.fromkeys(var[:-8] for var in variables))
    meta_data["LIB_VAR_LONG_trimmed"] = filtered_meta_data["LIB_VAR_LONG"].str[:-8]
    filtered_meta_data = meta_data[meta_data["LIB_VAR_LONG_trimmed"].isin(variables)]

    cod_var = filtered_meta_data["COD_VAR"]

    selected_columns = [col for col in data.columns if col in cod_var.values]

    filtered_data = data[["CODGEO"] + selected_columns]
    filtered_data = filtered_data.merge(nom_commune[["code_insee", "nom_commune"]], 
                                        left_on="CODGEO", right_on="code_insee", 
                                        how="left").drop(columns=["code_insee"])
    melted_data = filtered_data.melt(
        id_vars=["nom_commune"],  # Maintenir CODGEO comme identifiant
        value_vars=selected_columns,  # Variables à "fondre"
        var_name="LIB_V",  # Nom de la colonne pour les années
        value_name="Valeur"  # Nom de la colonne pour les valeurs
    )
    melted_data = melted_data.merge(
        filtered_meta_data[["COD_VAR", "LIB_VAR_LONG"]],
        left_on="LIB_V",  # Colonne dans `melted_data`
        right_on="COD_VAR",  # Colonne dans `filtered_meta_data`
        how="inner"  # Pour ne pas perdre d'informations
    )

    melted_group_data = melted_data.groupby(['LIB_VAR_LONG',"LIB_V"]).sum(numeric_only=True).reset_index()
    melted_group_data["Année"] = melted_group_data["LIB_V"].str[1:3]
    melted_group_data["Catégorie"] = melted_group_data["LIB_VAR_LONG"].str[:-8]

    # Création du barplot
    fig = px.bar(
        melted_group_data, 
        x="Année", 
        y="Valeur", 
        color="Catégorie", 
        title="Diagramme empilé des catégories d'âge", 
        labels={"Category": "Catégories", "Value": "Valeurs", "Subcategory": "Sous-catégories"},
        barmode="stack"
    )
    fig.update_traces(width=1)

    # Affichage de la figure
    st.write(fig)
    st.markdown(
        "<p style='text-align: left; color: gray;'>"
        "Source : INSEE, Dossier Complet 2024</p>",
        unsafe_allow_html=True
    )