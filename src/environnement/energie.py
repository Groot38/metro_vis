import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


#dépenses dans domaine environnement
# type dep T2 ; 
@st.cache_data
def load_data_energie():
    file_path_gaz = "../data/environnement/elec/conso-gaz-metropole.csv"
    file_path_elec = "../data/environnement/elec/eco2mix-metropoles-tr.csv"
    gaz = pd.read_csv(file_path_gaz,sep = ";")
    elec = pd.read_csv(file_path_elec,sep = ";")
    file_path_elec_bat = "../data/environnement/elec/consommation_elec_grenoble_2012_2022.csv"
    elec_bat = pd.read_csv(file_path_elec_bat, sep=",")
    file_path_elec_tot = "../data/environnement/elec/consommation-annuelle-d-electricite-et-gaz-par-commune(1).csv"
    elec_tot = pd.read_csv(file_path_elec_tot, sep=";")
    return(gaz,elec,elec_bat,elec_tot)

gaz,elec,elec_bat,elec_tot = load_data_energie()

gaz["Date"] = pd.to_datetime(gaz["Date"], format="%Y-%m")
elec["Date"] = pd.to_datetime(elec["Date"], format="%Y-%m-%d")

######################################################################
st.title("Evolution de la consommation de Gaz")

st.line_chart(gaz,x="Date", y= "Consommation de gaz (en KWh PCS 0°C)")

#####################################################################

st.title("Evolution de la consommation d'Electricité")

# Extraire l'année et le mois pour regrouper les données
elec["Année-Mois"] = elec["Date"].dt.to_period("M")

# Calculer la moyenne par mois
elec_mensuel = elec.groupby("Année-Mois")["Consommation (MW)"].mean().reset_index()

elec_mensuel["Année-Mois"] = elec_mensuel["Année-Mois"].dt.to_timestamp()


# Graphique
st.line_chart(elec_mensuel, x="Année-Mois", y="Consommation (MW)")

#############################################################################

# 📆 Convertir la colonne date_releve en datetime
elec_bat["date_releve"] = pd.to_datetime(elec_bat["date_releve"])

# 📅 Extraire année uniquement
elec_bat["Année"] = elec_bat["date_releve"].dt.to_period("Y")

# 🔢 Convertir la colonne "quantite_kwh" en float
elec_bat["quantite_kwh"] = pd.to_numeric(elec_bat["quantite_kwh"], errors="coerce")

# 📊 Calcul de la moyenne annuelle par catégorie
elec_annuel_bat = elec_bat.groupby(["Année", "libelle_niv__4"])["quantite_kwh"].mean().reset_index()

# 🔄 Convertir Année en datetime pour Plotly
elec_annuel_bat["Année"] = elec_annuel_bat["Année"].dt.to_timestamp()

col1, col2  = st.columns([1,4],vertical_alignment="center")

with col1 : 
    # 🎛️ Sélecteur pour choisir UNE SEULE catégorie à afficher
    libelles_disponibles = elec_annuel_bat["libelle_niv__4"].unique()
    libelle_selectionne = st.selectbox("Sélectionnez une catégorie à afficher :", "ECLAIRAGE PUBLIC")

# 📌 Filtrer les données selon la catégorie choisie
elec_filtré = elec_annuel_bat[elec_annuel_bat["libelle_niv__4"] == libelle_selectionne]

with col2 :
    # 📊 Créer un bar chart avec la catégorie sélectionnée
    fig = px.line(
        elec_filtré, 
        x="Année", 
        y="quantite_kwh",  
        title=f"Consommation annuelle d'électricité - {libelle_selectionne}",
        color_discrete_sequence=["#3498db"]  # Bleu pour un style épuré
    )

    # 📈 Afficher dans Streamlit
    st.plotly_chart(fig)


########################################################################################

col3, col4  = st.columns([1,4],vertical_alignment="center")


with col3 :
    # 🎛️ Sélecteur pour choisir les secteurs à afficher
    secteurs_disponibles = elec_tot["FILIERE"].unique()
    secteur_selectionné = st.selectbox("Sélectionnez un secteur :", secteurs_disponibles)
# 📌 Filtrer les données selon le secteur sélectionné
elec_tot_filtré = elec_tot[(elec_tot["FILIERE"] == secteur_selectionné)]
elec_tot_filtré = elec_tot_filtré.groupby(['CODE GRAND SECTEUR','Année']).sum(numeric_only=True).reset_index()
#melted_group_data = melted_data.groupby(['LIB_VAR_LONG',"LIB_V"]).sum(numeric_only=True).reset_index()
with col4 :
    # 📊 Création du barplot empilé
    fig = px.bar(
        elec_tot_filtré, 
        x="Année", 
        y="Conso totale (MWh)",  
        color="CODE GRAND SECTEUR",  # FILIERE sera empilé
        barmode="stack",  # Empilement des filières
        title=f"Consommation par année pour {secteur_selectionné}"
    )

    # 📈 Affichage dans Streamlit
    st.plotly_chart(fig)

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
        barmode="stack",  # Empilement des filières
        title="Rapport consommation d'électricité/hab en 2023"
        )


st.plotly_chart(fig.update_layout(xaxis={'categoryorder': 'total descending'}))


###################################################


@st.cache_data
def load_data_energie():
    file_path_2020 = "../data/environnement/elec/dido/Donnees-de-consommation-et-de-points-de-livraison-denergie-a-la-maille-commune-chaleur-e.2020-10.csv"
    file_path_2021 = "../data/environnement/elec/dido/Donnees-de-consommation-et-de-points-de-livraison-denergie-a-la-maille-commune-chaleur-e.2021-10.csv"
    file_path_2022 = "../data/environnement/elec/dido/Donnees-de-consommation-et-de-points-de-livraison-denergie-a-la-maille-commune-chaleur-e.2022-09.csv"
    file_path_2023 = "../data/environnement/elec/dido/Donnees-de-consommation-et-de-points-de-livraison-denergie-a-la-maille-commune-chaleur-e.2023-09.csv"

    df2020 = pd.read_csv(file_path_2020,sep = ";")
    df2021 = pd.read_csv(file_path_2021,sep = ";")
    df2022 = pd.read_csv(file_path_2022,sep = ";")
    df2023 = pd.read_csv(file_path_2023,sep = ";")

    return(df2020,df2021,df2022,df2023)

df2020,df2021,df2022,df2023 = load_data_energie()

codes_insee = [ # Pour limiter sur la métropole
    "38057", "38059", "38071", "38068", "38111", "38126", "38150", "38151", 
    "38158", "38169", "38170", "38179", "38185", "38188", "38200", "38516", 
    "38187", "38317", "38471", "38229", "38235", "38258", "38252", "38271", 
    "38277", "38279", "38281", "38309", "38325", "38328", "38364", "38382", 
    "38388", "38421", "38423", "38436", "38445", "38472", "38474", "38478", 
    "38485", "38486", "38524", "38528", "38529", "38533", "38540", "38545", 
    "38562"
]

df2020bis = df2020.drop(df2020.index[[0]])
df2021bis = df2021.drop(df2020.index[[0]])
df2022bis = df2022.drop(df2020.index[[0]])
df2023bis = df2023.drop(df2020.index[[0]])

df2020GRE = df2020bis[df2020bis["Code géographique du territoire - Code de la zone"].isin(codes_insee)]
df2020GRE.rename(columns={"Niveau de rejet de CO2 des réseaux (en kg/kWh)": "Niveau de rejet direct en CO2 des réseaux (en kg/kWh)"}, inplace=True)

df2021GRE = df2021bis[df2021bis["Code géographique du territoire - Code de la zone"].isin(codes_insee)]
df2022GRE = df2022bis[df2022bis["Code.géographique.du.territoire - Code de la zone"].isin(codes_insee)]
df2022GRE.rename(columns={"Code.géographique.du.territoire - Code de la zone": "Code géographique du territoire - Code de la zone"}, inplace=True)
df2022GRE.rename(columns={"Millésime.des.données": "Millésime des données"}, inplace=True)
df2022GRE.rename(columns={"Niveau.de.rejet.direct.en.CO2.des.réseaux..en.kg.kWh.": "Niveau de rejet direct en CO2 des réseaux (en kg/kWh)"}, inplace=True)


df2023GRE = df2023bis[df2023bis["Code.géographique.du.territoire - Code de la zone"].isin(codes_insee)]
df2023GRE.rename(columns={"Code.géographique.du.territoire - Code de la zone": "Code géographique du territoire - Code de la zone"}, inplace=True)
df2023GRE.rename(columns={"Millésime.des.données": "Millésime des données"}, inplace=True)
df2023GRE.rename(columns={"Niveau.de.rejet.direct.en.CO2.des.réseaux..en.kg.kWh.": "Niveau de rejet direct en CO2 des réseaux (en kg/kWh)"}, inplace=True)

df2020_2023GRE = pd.concat([df2020GRE,df2021GRE,df2022GRE,df2023GRE], ignore_index=True)

col21, col22  = st.columns([1,3],vertical_alignment="center")

with col21 : 
    année_selectionnée = st.selectbox("Sélectionnez une année", sorted(df2020_2023GRE["Millésime des données"].unique(), reverse=True))
    op_selectionné_nom = st.selectbox("Sélectionnez un opérateur", sorted(df2020_2023GRE["Opérateur"].unique(), reverse=True))


    # 🎯 Filtrer le DataFrame pour récupérer la valeur correspondante
    df_filtré = df2020_2023GRE[(df2020_2023GRE["Millésime des données"] == année_selectionnée) & (df2020_2023GRE["Opérateur"] == op_selectionné_nom)]

    # 📊 Afficher la métrique si des données existent
    if not df_filtré.empty:
        valeur_rejet = float(df_filtré["Niveau de rejet direct en CO2 des réseaux (en kg/kWh)"].values[0])
        st.metric(
            label=f"Rejet direct en CO2 des réseaux ({op_selectionné_nom} - {année_selectionnée})",
            value=f"{valeur_rejet:.4f} kg/kWh"
        )
    else:
        st.warning("Aucune donnée disponible pour cette sélection.")

######################################

with col22 :

    df2020_2023GRE["Millésime des données"] = pd.to_numeric(df2020_2023GRE["Millésime des données"], errors="coerce")


    # 📈 Tracer la courbe d'évolution des rejets en CO₂ sur les années
    fig = px.line(
        df2020_2023GRE, 
        x="Millésime des données", 
        y="Niveau de rejet direct en CO2 des réseaux (en kg/kWh)",
        color="Opérateur",
        markers=True,  # Ajouter des points sur la courbe
        title=f"Évolution du rejet direct en CO₂",
        labels={"Millésime des données": "Année", "Niveau de rejet direct en CO2 des réseaux (en kg/kWh)": "CO₂ (kg/kWh)"},
    )

    # 📊 Affichage dans Streamlit
    st.plotly_chart(fig)

###################################################################################
