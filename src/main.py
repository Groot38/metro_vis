import streamlit as st
import random

st.set_page_config(
    page_title="Accueil - Dashboard", 
    page_icon="🌍", 
    layout="wide"
)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False



def login():
    """
    Cette fonction permets de passer de la page d'accueil à la l'application.
    """
    st.title("🌟 Bienvenue",)
    st.subheader("Analyses de données :blue[démographiques], :red[économiques] et :green[environnementales]")

    st.write("")
    st.write("")

    col1, col2,col3  = st.columns([1,2,1])

    with col1:
        st.image("../data/images/logo.png", use_container_width=True)
        with st.expander("Infos"):
             st.write('''
                Cette application vise à utiliser les données de la Métropole Grenoble Alpes.
                Projet Tutoré Master SSD by Toto Soso et Roro.
                 ''')
    

    with col2:
        image_paths = ["../data/images/im1.jpg", "../data/images/im2.jpg", "../data/images/im3.jpg"]
        # choisi une image de façon aléatoire
        if "image_index" not in st.session_state:
            st.session_state.image_index = random.choice([-1,0,1])

        
        def previous_image():
            """
            Cette fonction permet de mettre l'image précédente en accédant au session.state
            """
            st.session_state.image_index = (st.session_state.image_index - 1) % len(image_paths)

        def next_image():
            """
            Cette fonction permet de mettre l'image suivante en accédant au session.state
            """
            st.session_state.image_index = (st.session_state.image_index + 1) % len(image_paths)

        # on affiche l'image courante
        st.image(image_paths[st.session_state.image_index], use_container_width=True)

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
        if st.button("🔑 Cliquez ici", key="login_button", help="Cliquez pour accèder à l'application"):
            st.session_state.logged_in = True
            st.rerun()   
        st.caption("Sources des données en Open Data")
        st.link_button("Open Data de la Métropole de Grenoble", "https://data.metropolegrenoble.fr/",help="lien vers le portail de l'open data de la métropole")
        st.link_button("Data.gouv", "https://www.data.gouv.fr/fr/",help="lien vers data.gouv")
        st.link_button("Insee","https://www.insee.fr/fr/accueil",help="lien vers INSEE")


    

def info():
    """
    Cette fonction permet de passer de l'application à la page d'accueil.
    """
    st.title("Bienvenue sur la page d'information")

    st.text("Cette application est dédié à la métropole de Grenoble, les 2 axes de travail sont l'environnement et la démographie.")
    st.text("N'hésitez pas à parcourir chaque page une par une")

    st.subheader("Descriptif des pages lié à la démographie :")

    st.text("Page menages : On va trouver ici ce qui est lié aux nombre d'enfants et statut mariétal")
    st.text("Page population : On va trouver des informations sur le nombre d'habitants, l'âge de la population et plus encore...")
    st.text("Page revenu : On va avoir les informations sur les salaires en fonction du sexe et de la commune")
    st.text("Page travail : On aura les catégories socioprofessionelles et le nombre d'actifs par rapport au nombre de retraité")

    st.subheader("Descriptif des pages lié à l'environnement :") 
    
    st.text("Page atmo : On aura sur cette page les informations liés à la qualité de l'air selon certains polluants")
    st.text("Page energie : On aura sur cette page les informations liés à la consommation de gaz et d'éléctricité de la métropole")
    st.text("Page meteo : On a ici les informations sur la météo sur 6 stations différentes")
    st.text("Page transport : On a ici les informations lié aux mobilités pour aller au travail")
    st.text("Page zfe : On a ici les informations sur les ZFE et l'évolution du parc automobile de la metropole")


    if st.button("🚪Retour à la page d'accueil"):
        st.session_state.logged_in = False
        st.rerun()

# page d'accueil et page d'info
login_page = st.Page(login, title="Page d'informations", icon="ℹ️")
logout_page = st.Page(info, title="Information", icon="ℹ️")

# pages démographie
population = st.Page("demo/population.py", title="Population", icon="👥")
travail = st.Page("demo/travail.py", title="Travail", icon="💼")
revenu = st.Page("demo/revenu.py", title="Revenu", icon="💵")
menages = st.Page("demo/menages.py", title="Ménages", icon="🧹")


# pages environnement
meteo = st.Page("environnement/meteo.py", title="Météo", icon="🌧️")
energie = st.Page("environnement/energie.py", title="Energie", icon="⚡")
atmo = st.Page("environnement/atmo.py",title= "Qualité de l'air",icon = "🌫️")
zfe = st.Page("environnement/zfe.py",title= "ZFE et parc automobile",icon = "🚗")
transport = st.Page("environnement/transport.py", title="Transport", icon="🚲")


if st.session_state.logged_in:
    pg = st.navigation(
        {
            "": [logout_page],
            "📊 Démographie": [population, travail, menages,revenu],
            "🌱 Environnement": [meteo, energie,atmo,zfe,transport],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()
