import streamlit as st

def population_page():
    st.title("Sous-page : Population")
    st.write("Bienvenue dans la sous-page Population.")
    if st.button("Retour"):
        st.session_state.page = "Demo"