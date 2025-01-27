import streamlit as st

def meteo_page():
    st.title("Sous-page : Météo")
    st.write("Bienvenue dans la sous-page Météo.")
    if st.button("Retour"):
        st.session_state.page = "Environnement"
