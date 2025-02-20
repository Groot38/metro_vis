import streamlit as st
from src.utils import load_data,load_geojson
import plotly.express as px
import re
import numpy as np


geojson_commune = load_geojson()
data,meta_data,nom_commune= load_data()

visualization_type = st.sidebar.radio("Type de Visualisation", ["Population par commune", "Evolution de la population","Repartition par âge"])

st.sidebar.title("Options")
st.sidebar.text("Sélectionnez les années : ")
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
    "Sélectionnez un sexe : ",
    ("Les deux", "Homme", "Femme"),
)

if selection_sex  == "Homme":
    pattern_sex = re.compile(f"^[P]({year_pattern})_(POPH|H)(0014|1529|3044|4559|6074|7589|90P|^$)*$")
    st.session_state["selected_variable"] = None
elif selection_sex  == "Femme":
    pattern_sex = re.compile(f"^[P]({year_pattern})_(POPF|F)(0014|1529|3044|4559|6074|7589|90P|^$)*$")
    st.session_state["selected_variable"] = None
else:
    pattern_sex = re.compile(f"^[P]({year_pattern})_(POP)(0014|1529|3044|4559|6074|7589|90P|^$|75P)*$")
    st.session_state["selected_variable"] = None
# Premier filtre
pattern = re.compile(f"^[P]({year_pattern})_(POP|F|H)(H|F|[0-9]|$)[a-zA-Z0-9]*$")
filtered_meta_data = meta_data[meta_data["COD_VAR"].astype(str).str.match(pattern)]
# Deuxième filtre sur le sexe
filtered_meta_data = meta_data[meta_data["COD_VAR"].astype(str).str.match(pattern_sex)]
meta_data_age_répartition = filtered_meta_data

variables = filtered_meta_data["LIB_VAR_LONG"]
variables=list(dict.fromkeys(var[:-8] for var in variables))

if "selected_variable" not in st.session_state or st.session_state["selected_variable"] == None: 
    selected_variable = st.sidebar.selectbox("Choisissez une catégorie à analyser", variables,index = 0)
    st.session_state["selected_variable"] = selected_variable
else :
    selected_variable = st.sidebar.selectbox("Choisissez une catégorie à analyser",variables,index = variables.index(st.session_state["selected_variable"]))
    st.session_state["selected_variable"] = selected_variable



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
        color_scale = [
                [0, "white"],
                [1, "blue"]
            ]
        fig = px.choropleth_mapbox(
            filtered_data,
            geojson=geojson_commune,
            locations="CODGEO",
            featureidkey="properties.code",
            color=selected_columns[0],
            color_continuous_scale=color_scale,
            labels={selected_columns[0]: "Population",
                    "nom_commune" : "Commune"},
            title=f"{selected_variable} par commune en 20{max(selected_years)}",
            hover_data={"CODGEO": False, "nom_commune": True}
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=9,
            mapbox_center={"lat": 45.166672, "lon": 5.71667},
            height=700
        )
        fig.update_traces(marker=dict(opacity=0.7))
        st.plotly_chart(fig)
        st.markdown(
            "<p style='text-align: left; color: gray; margin-top: -80px;'>"
            "Source : INSEE, Dossier Complet 2024</p><br><br>",
            unsafe_allow_html=True
        )

    if len(selected_years) > 1 :
        filtered_data["evolution"] = (filtered_data.iloc[:,1]/filtered_data.iloc[:,len(selected_years)])

        min_val = min(filtered_data["evolution"])
        max_val = max(filtered_data["evolution"])

        #Palette personalisée
        color_scale = [
            [0, "red"],
            [(1 - min_val) / (max_val - min_val), "white"],  
            [1, "green"] 
        ]
        
        nb_annee = len(selected_years)
        with colage:
            figue = px.choropleth_mapbox(
                filtered_data,
                geojson=geojson_commune,
                locations="CODGEO",  
                featureidkey="properties.code",
                color="evolution",
                color_continuous_scale=color_scale,
                labels={"evolution": "Évolution",
                        "nom_commune" : "Commune"},
                title=f"Evolution de {selected_variable} par commune entre 20{selected_years[nb_annee-len(selected_years)]} et 20{selected_years[nb_annee-1]}",
                hover_data={"CODGEO": False, "nom_commune": True}
            )
            figue.update_geos(fitbounds="locations", visible=False)
            figue.update_layout(
                mapbox_style="open-street-map",
                mapbox_zoom=9, 
                mapbox_center={"lat": 45.166672, "lon": 5.71667},
                height=700
            )
            figue.update_traces(marker=dict(opacity=0.7))
            st.plotly_chart(figue)
            st.markdown(
                "<p style='text-align: left; color: gray; margin-top: -80px;'>"
                "L'évolution a été calculée en faisant le rapport des années sélectionnées <br>"
                "Source : INSEE, Dossier Complet 2024</p>",
                unsafe_allow_html=True
            )
    else:
        with colage:
            st.warning("Pour afficher la carte des évolutions, veuillez sélectionner aux moins 2 années")
    
    # Carte de la moyenne d'age par commune :
    cod_var = meta_data_age_répartition["COD_VAR"]
    selected_columns = [col for col in data.columns if col in cod_var.values]

    filtered_data = data[["CODGEO"] + selected_columns]
    filtered_data = filtered_data.merge(nom_commune[["code_insee", "nom_commune"]], 
                                        left_on="CODGEO", right_on="code_insee", 
                                        how="left").drop(columns=["code_insee"])
    
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
        locations="CODGEO",
        featureidkey="properties.code",
        color="age_moy",
        color_continuous_scale=color_scale,
        title = f"Age moyen{' ' if selection_sex == 'Les deux' else " des "+selection_sex + 's'} par commune en {'20' + max(selected_years)}",
        labels={"age_moy" : "Âge moyen",
                "nom_commune" : "Commune"},
        hover_data={"CODGEO": False, "nom_commune": True}
    )
    abricot.update_geos(fitbounds="locations", visible=False)
    abricot.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=9,
        mapbox_center={"lat": 45.166672, "lon": 5.71667},
        height=700
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

    if not selected_columns:
        st.warning("Aucune année sélectionnée pour l'histogramme.")
    else:
        filtered_data["rank"] = filtered_data.iloc[:, 1].rank(method="min", ascending=False)

        # On adapte les données pour le barchart
        melted_data = filtered_data.melt(
            id_vars=["nom_commune"],
            value_vars=selected_columns,
            var_name="Variable",
            value_name="Valeur"
        )

        # Ajout des rangs
        melted_data["Rank"] = melted_data["nom_commune"].map(filtered_data.set_index("nom_commune")["rank"])
        melted_data = melted_data.sort_values(by=["Rank", "nom_commune", "Variable"])

        num_lines = st.sidebar.number_input("Nombre de lignes à afficher", min_value=1, max_value=49, value=10)
        custom_labels = {"21": "2021", "15": "2015", "10": "2010"}

        melted_data["Legende"] = melted_data["Variable"].str[1:3].replace(custom_labels)
        melted_data_tronc = melted_data.head(num_lines * len(selected_years))

        mandarine = px.bar(
            melted_data_tronc,
            x="nom_commune",
            y="Valeur",
            color="Legende",
            barmode="group",
            title=f"Comparaison de {selected_variable} par commune et par année",
            labels={"nom_commune": "Commune", "Valeur": "Population", "Legende": "Année"}
        )

        mandarine.update_layout(
            xaxis_title="Communes",
            yaxis_title="Population",
            width=900,
            height=650,
            bargap=0.15,
            xaxis_tickangle=90
        )

        st.plotly_chart(mandarine, use_container_width=True)
        st.markdown(
            "<p style='text-align: left; color: gray; margin-top: -40px;'>"
            "Source : INSEE, Dossier Complet 2024</p>",
            unsafe_allow_html=True
        )

        melted_group_data = melted_data.groupby('Variable')['Valeur'].sum().reset_index()
        melted_group_data["nom"] = ["Grenoble Alpes Metropole"] * len(selected_years)
        melted_group_data["Legende"] = melted_group_data["Variable"].str[1:3].replace(custom_labels)

        banane = px.bar(
            melted_group_data,
            x="nom",
            y="Valeur",
            color="Legende",
            barmode="group",
            title=f"Comparaison par année de {selected_variable} sur la métropole de Grenoble",
            labels={"nom": "Grenoble Alpes Métropole", "Valeur": "Population", "Legende": "Année"},
            hover_data={"nom" : False} 
        )

        banane.update_layout(
            xaxis_title="Année",
            yaxis_title="Population",
            #width=650,
            #height=650,
            #bargap=0.75,
            bargroupgap=0.75
        )

        st.plotly_chart(banane, use_container_width=True)
        st.markdown(
            "<p style='text-align: left; color: gray;'>"
            "Source : INSEE, Dossier Complet 2024</p>",
            unsafe_allow_html=True
        )

elif visualization_type == "Repartition par âge":
    filtered_meta_data = meta_data[meta_data["COD_VAR"].astype(str).str.match(pattern_sex)]
    pattern_pie = re.compile(f"^P({year_pattern})_\w+\d+.*")
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
        id_vars=["nom_commune"],
        value_vars=selected_columns,
        var_name="LIB_V",
        value_name="Nombre" 
    )
    melted_data = melted_data.merge(filtered_meta_data[["COD_VAR", "LIB_VAR_LONG"]],left_on="LIB_V",right_on="COD_VAR",how="inner")

    melted_group_data = melted_data.groupby(['LIB_VAR_LONG',"LIB_V"]).sum(numeric_only=True).reset_index()
    melted_group_data["Année"] = "20"+melted_group_data["LIB_V"].str[1:3]
    melted_group_data["Catégorie"] = melted_group_data["LIB_VAR_LONG"].str[:-8]

    fig = px.bar(
        melted_group_data, 
        x="Année", 
        y="Nombre", 
        color="Catégorie", 
        title="Diagramme empilé des catégories d'âge", 
        labels={"Category": "Catégories"},
        barmode="stack"
    )
    fig.update_traces(width=1)
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=melted_group_data["Année"].unique()))

    st.write(fig)
    st.markdown(
        "<p style='text-align: left; color: gray;'>"
        "Source : INSEE, Dossier Complet 2024</p>",
        unsafe_allow_html=True
    )