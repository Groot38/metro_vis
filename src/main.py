import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Fonction de login
def login():
    # Demander le nom d'utilisateur et le mot de passe
    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")
    
    # Authentification simple (ici avec des identifiants prédéfinis)
    if st.button("Log in"):
        if username == "luc" and password == "tom":  # Identifiants simples pour la démo
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
            
        else:
            st.error("Invalid username or password.")

# Fonction de logout
def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
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
