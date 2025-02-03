import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json
import re
import matplotlib.pyplot as plt
from utils import load_data,load_geojson


geojson_commune = load_geojson()
data,meta_data,nom_commune= load_data()

#st.write(data.head())

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

# Générer le pattern dynamique
#pattern = re.compile(f"^[P]({year_pattern})_[PFH][O0-9][a-zA-Z0-9]*$")
pattern = re.compile(f"^[P]({year_pattern})_(POP|F|H)(H|F|[0-9]|$)[a-zA-Z0-9]*$")

filtered_meta_data = meta_data[meta_data["COD_VAR"].astype(str).str.match(pattern)]
# Filtrage des données pour analyse
variables = filtered_meta_data["LIB_VAR_LONG"]
variables=list(dict.fromkeys(var[:-8] for var in variables))

if "selected_variable" not in st.session_state or st.session_state["selected_variable"] == None: 
    selected_variable = st.sidebar.selectbox("Choisissez une catégorie à analyser", variables,index = 0)
    st.session_state["selected_variable"] = selected_variable
else :
    selected_variable = st.sidebar.selectbox("Choisissez une catégorie à analyser",variables,index = variables.index(st.session_state["selected_variable"]))
    st.session_state["selected_variable"] = selected_variable
visualization_type = st.sidebar.radio("Type de Visualisation", ["Carte Choroplèthe", "Histogramme","Diagramme Circulaire"])



# Filtrer les données pour la variable choisie
filtered_meta_data["LIB_VAR_LONG_trimmed"] = filtered_meta_data["LIB_VAR_LONG"].str[:-8]
filtered_meta_data = filtered_meta_data[filtered_meta_data["LIB_VAR_LONG_trimmed"] == selected_variable]
cod_var = filtered_meta_data["COD_VAR"]

selected_columns = [col for col in data.columns if col in cod_var.values]

filtered_data = data[["CODGEO"] + selected_columns]
filtered_data = filtered_data.merge(nom_commune[["code_insee", "nom_commune"]], 
                                     left_on="CODGEO", right_on="code_insee", 
                                     how="left").drop(columns=["code_insee"])



if visualization_type == "Carte Choroplèthe":
    st.subheader(f"Carte Choroplèthe : {selected_variable}")
    # Exemple de visualisation avec Plotly
    fig = px.choropleth(
        filtered_data,
        geojson=geojson_commune,
        locations="CODGEO",  # Code géographique (par exemple, code INSEE)
        featureidkey="properties.code",
        color=selected_columns[0],  # Colonne avec les valeurs numériques
        color_continuous_scale="Inferno",
        labels={selected_columns[0]: selected_variable},
        title=selected_variable
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=700)
    st.plotly_chart(fig)

elif visualization_type == "Histogramme":
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
            x=alt.X("nom_commune:N", title="Communes",axis=alt.Axis(labelAngle=-45),sort="-y"),  # Afficher CODGEO sur l'axe X
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
        melted_group_data = melted_data.groupby('Variable')['Valeur'].sum().reset_index()
        melted_group_data["nom"]= ["Grenoble Alpes Metropole"]*len(selected_years)


        melted_group_data["Legende"] = melted_group_data["Variable"].str[1:3].replace(custom_labels)
        
        chark = alt.Chart(melted_group_data).mark_bar(size=100).encode(
            x=alt.X("nom:N", title="Nom",axis=alt.Axis(labelAngle=-45),sort="-y"),  # Afficher CODGEO sur l'axe X
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

elif visualization_type == "Diagramme Circulaire":
    pattern2021POP = re.compile(f"^[P]({year_pattern})_(PO)(P0014|P1529|P3044|P4559|P6074|P7589|P90P)*$")
    filtered_meta_data = meta_data[meta_data["COD_VAR"].astype(str).str.match(pattern2021POP)]
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
        var_name="Variable",  # Nom de la colonne pour les années
        value_name="Valeur"  # Nom de la colonne pour les valeurs
    )
    

    melted_group_data = melted_data.groupby('Variable')['Valeur'].sum().reset_index()
    st.write(melted_group_data.sort_values(by="Variable"))
    variables_trimmed = [var[23:] for var in variables]
    fig = px.pie(melted_group_data, 
             names=variables_trimmed,  # Colonnes pour les noms des secteurs
             values='Valeur',  # Colonnes pour les valeurs
             title="Distribution des valeurs par Variable",
             color='Variable',  # Colorie les secteurs par "Variable"
             color_discrete_sequence=px.colors.qualitative.Set1
             )  # Palette de couleurs
    st.write(melted_group_data["Variable"].sort_values())
    # Affichage du graphique dans Streamlit
    st.write(fig)
