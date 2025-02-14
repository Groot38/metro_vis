import streamlit as st
from PIL import Image
import time
import pandas as pd
import numpy as np
import random


# Configuration de la page
st.set_page_config(
    page_title="Accueil - Dashboard", 
    page_icon="🌍", 
    layout="wide"
)

# Vérification de l'état de connexion
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ---- Fonction de login ----
def login():
    st.title("🌟 Bienvenue",)
    st.subheader("Analyses de données :blue[démographiques], :red[économiques] et :green[environnementales]")

    # Zone de connexion
    st.write("")
    st.write("")

    col1, col2,col3  = st.columns([1,2,1])

    with col1:
        st.image("../data/images/logo.png", use_container_width=True)
        with st.expander("Infos"):
             st.write('''
                Cette application vise à utiliser les données de la Métropole Grenoble Alpes.
                Projet Tutoré Master SSD by Tom Soheïl et Roro.
                 ''')
        if st.button("🔑 Cliquez ici", key="login_button", help="Cliquez pour accèder aux données"):
            st.session_state.logged_in = True
            st.rerun()   
    

    with col2:

        # Liste des images
        image_paths = ["../data/images/im1.jpg", "../data/images/im2.jpg", "../data/images/im3.jpg"]

        # Initialiser l'index de l'image dans la session Streamlit
        if "image_index" not in st.session_state:
            st.session_state.image_index = random.choice([-1,0,1])

        # Fonction pour changer d'image
        def previous_image():
            st.session_state.image_index = (st.session_state.image_index - 1) % len(image_paths)

        def next_image():
            st.session_state.image_index = (st.session_state.image_index + 1) % len(image_paths)

        # Afficher l'image actuelle
        st.image(image_paths[st.session_state.image_index], use_container_width=True)

        # Créer les boutons de navigation
        col1, col2, col3bis = st.columns([1, 6, 1])
        with col1:
            if st.button("⬅️", key="prev"):
                previous_image()
                st.rerun()

        with col3bis:
            if st.button("➡️", key="next"):
                next_image()
                st.rerun()
    with col3:
        st.caption("Sources des données en Open Data")
        st.link_button("Open Data de la Métropole de Grenoble", "https://data.metropolegrenoble.fr/")
        st.link_button("Data.gouv", "https://www.data.gouv.fr/fr/")
        st.link_button("Insee","https://www.insee.fr/fr/accueil")


    

# ---- Fonction de logout ----
def logout():
    st.write("### ")
    if st.button("🚪Retour à la page d'accueil"):
        st.session_state.logged_in = False
        st.success("Déconnexion réussie !")
        st.rerun()

# ---- Création des pages ----
login_page = st.Page(login, title="Page d'informations", icon="ℹ️")
logout_page = st.Page(logout, title="Information", icon="ℹ️")

population = st.Page("demo/population.py", title="Population", icon="👥")
travail = st.Page("demo/travail.py", title="Travail", icon="💼")
revenu = st.Page("demo/revenu.py", title="Revenu", icon="💵")
menages = st.Page("demo/menages.py", title="Ménages", icon="🧹")
transport = st.Page("demo/transport.py", title="Transport", icon="🚲")


meteo = st.Page("environnement/meteo.py", title="Météo", icon="🌧️")
energie = st.Page("environnement/energie.py", title="Energie", icon="⚡")
atmo = st.Page("environnement/atmo.py",title= "Qualité de l'air",icon = "🌫️")
zfe = st.Page("environnement/zfe.py",title= "ZFE et parc automobile",icon = "🚗")


# ---- Gestion de la navigation ----
if st.session_state.logged_in:
    pg = st.navigation(
        {
            "": [logout_page],
            "📊 Démographie": [population, travail, menages,transport,revenu],
            "🌱 Environnement": [meteo, energie,atmo,zfe],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()
