import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

login_page = st.Page(login, title="Log in", icon="🔑")
logout_page = st.Page(logout, title="Log out", icon="🚪")


population = st.Page("demo/population.py", title="Population", icon="👥")
travail = st.Page("demo/travail.py", title="Travail", icon="💼")
tourisme = st.Page("demo/tourisme.py", title="Tourisme", icon="✈️")


meteo = st.Page("environnement/meteo.py", title="Météo", icon="🌧️")
dechet = st.Page("environnement/dechet.py", title="Déchet", icon="♻️")

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Accueil": [logout_page],
            "Demographie": [population, travail, tourisme],
            "Environnemnent": [meteo, dechet],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()
