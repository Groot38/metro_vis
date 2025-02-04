import streamlit as st

# Titre de l'application
st.title("Sélectionnez un seul bouton")

# Utilisation du widget radio pour limiter la sélection à un seul bouton
# Le paramètre "index" définit quel bouton est sélectionné par défaut
selection = st.radio(
    "Choisissez un bouton",
    ("Bouton 1", "Bouton 2", "Bouton 3"),
)

# Affichage du bouton sélectionné
if selection == "Bouton 1":
    st.write("Vous avez sélectionné le Bouton 1.")
elif selection == "Bouton 2":
    st.write("Vous avez sélectionné le Bouton 2.")
else:
    st.write("Vous avez sélectionné le Bouton 3.")
