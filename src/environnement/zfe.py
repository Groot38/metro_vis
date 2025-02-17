import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


@st.cache_data
def load_data_full():
    """
    Cette fonction renvoie le CSV sur le parc auto de la métro de Grenoble
    """
    file_path_full_data = "../data/environnement/devdurable/Donnees-sur-le-parc-de-vehicule-au-niveau-communal.2023-05.csv"
    df_full = pd.read_csv(file_path_full_data,sep = ";",skiprows=1)
    return(df_full)

df_full= load_data_full()



st.title("Etude des ZFE")
multi = '''
    Voitures :red[Crit’Air 5] et non classés : interdits depuis juillet 2023  
    Véhicules :orange[Crit’Air 4] : interdits depuis le 1er janvier 2024  
    Véhicule utilitaire léger et poids lourd :green[Crit’Air 3] : interdits depuis le 1er juillet 2023  

    Ces restrictions s’appliquent du lundi au vendredi, de 7h à 19h, hors week-ends et jours fériés.  

    Pour les prochaines étapes, le calendrier prévisionnel prévoit une interdiction au 1er janvier 2025 pour les véhicules :green[Crit Air 3].  
    La métropole de Grenoble envisage également d’interdire les véhicules :blue[Crit’Air 2] avant 2030, en anticipation de la fin des ventes de véhicules thermiques annoncée pour 2035.
    '''
st.subheader("Dans la Zone à Faibles Émissions (ZFE) de Grenoble Alpes Métropole, les restrictions de circulation s’appliquent aux véhicules suivants en fonction de leur vignette Crit’Air :")  
st.markdown(multi)

with st.expander("Infos"):
        st.write('''
            Au 1er janvier 2022, le parc de véhicules en circulation se compose de 38,7 millions de voitures particulières, 
            6,3 millions de véhicules utilitaires légers, 616 000 poids lourds et 95 000 autobus et autocars. 
            Le SDES met à disposition des statistiques par genre de véhicule (voitures particulières, véhicules utilitaires légers, 
            poids lourds, autobus et autocars) ; par localisation (région, département, commune) ; selon les caractéristiques 
            techniques du véhicule (motorisation, âge, vignette Crit’Air, poids total autorisé en charge — PTAC) et les 
            caractéristiques de l’utilisateur (ménages, entreprises, administrations, et secteurs d’activité).
            ''')

# codes insee de la métropole
codes_insee = [
    "38057", "38059", "38071", "38068", "38111", "38126", "38150", "38151", 
    "38158", "38169", "38170", "38179", "38185", "38188", "38200", "38516", 
    "38187", "38317", "38471", "38229", "38235", "38258", "38252", "38271", 
    "38277", "38279", "38281", "38309", "38325", "38328", "38364", "38382", 
    "38388", "38421", "38423", "38436", "38445", "38472", "38474", "38478", 
    "38485", "38486", "38524", "38528", "38529", "38533", "38540", "38545", 
    "38562"
]

codes_insee = list(map(str, codes_insee)) 

# on garde uniquement les codes communes de la métro
df_metroGRE = df_full[df_full["COMMUNE_CODE"].isin(codes_insee)]

colonnes_annees = ["PARC_2011", "PARC_2012", "PARC_2013", "PARC_2014", "PARC_2015", 
                   "PARC_2016", "PARC_2017", "PARC_2018", "PARC_2019", "PARC_2020", 
                   "PARC_2021", "PARC_2022"]

df_melted = df_metroGRE.melt(
    id_vars=["COMMUNE_CODE", "COMMUNE_LIBELLE", "CATEGORIE_VEHICULE", "CRITAIR"],  
    value_vars=colonnes_annees, 
    var_name="Année", 
    value_name="Nombre de véhicules"
)

df_melted["Année"] = df_melted["Année"].str.extract(r"(\d{4})").astype(int)

col1, col2  = st.columns([1,3],vertical_alignment="center")

with col1 :
    ville_selectionnee = st.selectbox("Sélectionnez une ville :", sorted(df_melted["COMMUNE_LIBELLE"].unique()))
    critair_selectionne = st.selectbox("Sélectionnez un Crit'Air :", sorted(df_melted["CRITAIR"].dropna().unique()))

df_filtré = df_melted[
    (df_melted["COMMUNE_LIBELLE"] == ville_selectionnee) & 
    (df_melted["CRITAIR"] == critair_selectionne)
]

# on a un df qui fait la somme des véhicules par année
df_evolution = df_filtré.groupby("Année")["Nombre de véhicules"].sum()
val_2011 = df_evolution.get(2011, 0)
val_2022 = df_evolution.get(2022, 0)

if val_2011 > 0:  
    evolution_pourcentage = ((val_2022 - val_2011) / val_2011) * 100
else:
    evolution_pourcentage = None

with col2 :
    fig = px.bar(
        df_filtré, 
        x="Année", 
        y="Nombre de véhicules",  
        color="CATEGORIE_VEHICULE",  
        barmode="stack",  
        title=f"Évolution du parc {critair_selectionne} à {ville_selectionnee} par catégorie de véhicule"
    )

    st.plotly_chart(fig)

    st.markdown(
            "<p style='text-align: left; color: gray; margin-top: -40px;'>"
            "Source : Données sur le parc de véhicules au niveau communal SDES</p><br><br>",
            unsafe_allow_html=True
        )

with col1 :
    if evolution_pourcentage is not None:
        st.metric(
            label=f"Évolution 2011 → 2022 ({critair_selectionne} à {ville_selectionnee})",
            value=f"{evolution_pourcentage:.2f} %",
            delta=f"{val_2022 - val_2011} véhicules"
        )
    else:
        st.write("Pas de données disponibles pour calculer l'évolution.")

##################################################################################

df_grouped = df_melted[df_melted["CRITAIR"] == critair_selectionne].groupby(["Année", "COMMUNE_LIBELLE"], as_index=False)["Nombre de véhicules"].sum()

fig = px.line(
    df_grouped, 
    x="Année", 
    y="Nombre de véhicules",  
    color="COMMUNE_LIBELLE",   
    title=f"Évolution du parc {critair_selectionne}",
    markers=True
)

fig.update_layout(
    xaxis=dict(
        tickmode="linear",
        dtick=1  
    ),
    yaxis_title="Nombre de véhicules"
)
st.plotly_chart(fig)

st.markdown(
            "<p style='text-align: left; color: gray; margin-top: -40px;'>"
            "Source : Données sur le parc de véhicules au niveau communal SDES</p><br><br>",
            unsafe_allow_html=True
)


df_group_critair = df_melted.groupby(["CRITAIR","Année"]).sum(numeric_only = True).reset_index()

kiwi = px.line(
    df_group_critair, 
    x="Année", 
    y="Nombre de véhicules",  
    color="CRITAIR",   
    title=f"Évolution du parc automobile par vignette Crit'Air",
    markers=True
)

kiwi.update_layout(
    xaxis=dict(
        tickmode="linear",
        dtick=1  
    ),
    yaxis_title="Nombre de véhicules"
)
st.plotly_chart(kiwi)

st.markdown(
            "<p style='text-align: left; color: gray; margin-top: -40px;'>"
            "Source : Données sur le parc de véhicules au niveau communal SDES</p><br><br>",
            unsafe_allow_html=True
)


###############################################################################


        
st.link_button("Source SDES", "https://www.statistiques.developpement-durable.gouv.fr/catalogue?page=dataset&datasetId=64511438f3196b5b550dd093")

    ############################################""

