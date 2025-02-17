import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px



@st.cache_data
def load_data_energie():
    """
    Cette fonction renvoie les df sur l'énergie de la métro contenu dans data/environnement/elec/
    """
    file_path_gaz = "data/environnement/elec/conso-gaz-metropole.csv"
    file_path_elec = "data/environnement/elec/eco2mix-metropoles-tr.csv"
    gaz = pd.read_csv(file_path_gaz,sep = ";")
    elec = pd.read_csv(file_path_elec,sep = ";")
    file_path_elec_bat = "data/environnement/elec/consommation_elec_grenoble_2012_2022.csv"
    elec_bat = pd.read_csv(file_path_elec_bat, sep=",")
    file_path_elec_tot = "data/environnement/elec/consommation-annuelle-d-electricite-et-gaz-par-commune(1).csv"
    elec_tot = pd.read_csv(file_path_elec_tot, sep=";")
    return(gaz,elec,elec_bat,elec_tot)

gaz,elec,elec_bat,elec_tot = load_data_energie()

gaz["Date"] = pd.to_datetime(gaz["Date"], format="%Y-%m")
elec["Date"] = pd.to_datetime(elec["Date"], format="%Y-%m-%d")

######################################################################
st.title("Evolution de la consommation de Gaz")

st.line_chart(gaz,x="Date", y= "Consommation de gaz (en KWh PCS 0°C)")
st.markdown(
            "<p style='text-align: left; color: gray; margin-top: -40px;'>"
            "Source : Consommation mensuelle brute de gaz des grandes Métropoles françaises (zone NaTran et Teréga) ODRE</p><br><br>",
            unsafe_allow_html=True
        )
#####################################################################

st.title("Evolution de la consommation d'Electricité")

elec["Année-Mois"] = elec["Date"].dt.to_period("M")

elec_mensuel = elec.groupby("Année-Mois")["Consommation (MW)"].mean().reset_index()

elec_mensuel["Année-Mois"] = elec_mensuel["Année-Mois"].dt.to_timestamp()


# Graphique de la consommation d'éléctritie
st.line_chart(elec_mensuel, x="Année-Mois", y="Consommation (MW)")
st.markdown(
            "<p style='text-align: left; color: gray; margin-top: -40px;'>"
            "Source : Consommation d'électricité des grandes Métropoles françaises temps réel ODRE</p><br><br>",
            unsafe_allow_html=True
        )
#############################################################################

elec_bat["date_releve"] = pd.to_datetime(elec_bat["date_releve"])

elec_bat["Année"] = elec_bat["date_releve"].dt.to_period("Y")

elec_bat["quantite_kwh"] = pd.to_numeric(elec_bat["quantite_kwh"], errors="coerce")

# moyenne annuel par catégorie
elec_annuel_bat = elec_bat.groupby(["Année", "libelle_niv__4"])["quantite_kwh"].mean().reset_index()

elec_annuel_bat["Année"] = elec_annuel_bat["Année"].dt.to_timestamp()

elec_filtré = elec_annuel_bat[elec_annuel_bat["libelle_niv__4"] == "ECLAIRAGE PUBLIC"]

fig = px.line(
    elec_filtré, 
    x="Année", 
    y="quantite_kwh",  
    title=f"Consommation annuelle d'électricité - ECLAIRAGE PUBLIC",
    color_discrete_sequence=["#3498db"]
)
fig.update_yaxes(rangemode="tozero")

st.plotly_chart(fig)
st.markdown(
            "<p style='text-align: left; color: gray; margin-top: -50px;'>"
            "Source :  Consommations d'électricité des bâtiments de la ville de Grenoble 2012-2022 OPEN DATA GRENOBLE METROPOLE</p><br><br>",
            unsafe_allow_html=True
        )

########################################################################################

col3, col4  = st.columns([1,4],vertical_alignment="center")


with col3 :
    secteurs_disponibles = elec_tot["FILIERE"].unique()
    secteur_selectionné = st.selectbox("Sélectionnez un secteur :", secteurs_disponibles)
elec_tot_filtré = elec_tot[(elec_tot["FILIERE"] == secteur_selectionné)]
elec_tot_filtré = elec_tot_filtré.groupby(['CODE GRAND SECTEUR','Année']).sum(numeric_only=True).reset_index()
with col4 :
    fig = px.bar(
        elec_tot_filtré, 
        x="Année", 
        y="Conso totale (MWh)",  
        color="CODE GRAND SECTEUR",
        barmode="stack",
        title=f"Consommation par année pour {secteur_selectionné}"
    )

    st.plotly_chart(fig)
    st.markdown(
            "<p style='text-align: left; color: gray; margin-top: -50px;'>"
            "Source : Consommation annuelle d’électricité et gaz par région et par secteur d’activité (jusqu'en 2021) ORE</p><br><br>",
            unsafe_allow_html=True
        )

col11, col12, col13,col14  = st.columns([1,1,1,1],vertical_alignment="center")

with col11 :
    with st.expander("Industrie"):
                st.write('''
                    Le secteur industriel comprend les activités économiques qui combinent des facteurs de production 
                    (installations, approvisionnements, travail, savoir) pour produire des biens matériels destinés au marché.
                    ''')
                
with col12 :
    with st.expander("Tertiaire"):
                st.write('''
                    Le secteur tertiaire recouvre un vaste champ d'activités qui s'étend du commerce à l'administration,
                    en passant par les transports, les activités financières et immobilières, 
                    les services aux entreprises et services aux particuliers, l'éducation, la santé et l'action sociale.
                    ''')
                
with col13 :
    with st.expander("Résidentiel"):
                st.write('''
                    Ce secteur d’utilisation de l’énergie consiste en des quartiers d’habitation.
                    ''')

with col14 :
             
    with st.expander("Agriculture"):
                st.write('''
                    Ce secteur de l'économie comprend les cultures, l'élevage, la chasse, la pêche et la sylviculture.
                    ''')


    #########################################################################

elec_annuel_tot = elec_tot[elec_tot["CODE GRAND SECTEUR"] == "RESIDENTIEL"]
elec_annuel_tot["Rapport par habitant"] = elec_annuel_tot["Conso totale (MWh)"]/elec_annuel_tot["Nombre d'habitants"]
elec_annuel_tot_commune = elec_annuel_tot.groupby(["Année", "Nom Commune"])["Rapport par habitant"].mean().reset_index()

elec_annuel_tot_commune_2023= elec_annuel_tot_commune[elec_annuel_tot_commune["Année"] == 2023]


fig = px.bar(
        elec_annuel_tot_commune_2023, 
        x="Nom Commune", 
        y="Rapport par habitant",  
        barmode="stack",
        title="Rapport de la consommation d'électricité en MWh par habitant en 2023"
        )


st.plotly_chart(fig.update_layout(xaxis={'categoryorder': 'total descending'}))
st.markdown(
            "<p style='text-align: left; color: gray; margin-top: -20px;'>"
            "Source : Consommation annuelle d’électricité et gaz par commune en 2023 ORE </p><br><br>",
            unsafe_allow_html=True
        )

###################################################

