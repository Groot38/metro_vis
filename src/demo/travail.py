import streamlit as st
import random

# Liste des sorts à afficher
sorts = ["Boule de feu", "Rayons de glace", "Main spectrale", "Flèche magique", "Mur de force"]

# Incrément d'un compteur pour chaque rechargement de page
if "reload_counter" not in st.session_state:
    st.session_state.reload_counter = 0

st.session_state.reload_counter += 1

# Choisir un sort aléatoire à chaque retour
sort_aleatoire = random.choice(sorts)

st.write(f"Sort aléatoire lors de votre visite : 💫 {sort_aleatoire}")
st.write(f"Nombre de visites : {st.session_state.reload_counter}")

# Ajouter une checkbox simple pour tester les interactions
st.checkbox("Cette checkbox ne doit pas influencer le sort aléatoire.")
