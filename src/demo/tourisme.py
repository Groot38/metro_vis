import streamlit as st
import altair as alt
import pandas as pd

# Exemple de données
data = pd.DataFrame({
    "nom_commune": ["Commune A", "Commune B", "Commune C"],
    "Valeur": [1000, 2000, 1500],
    "Legende": ["P21_POP", "P15_POP", "P10_POP"],
    "Variable": ["Variable A", "Variable B", "Variable C"]
})

selected_variable = "Population Comparée"  

# Création du graphique avec Altair
chart = alt.Chart(data).mark_bar().encode(
    x=alt.X("nom_commune:N", title="Communes", axis=alt.Axis(labelAngle=-45), sort="-y"),
    y=alt.Y("Valeur:Q", title="Population"),
    color="Legende:N",
    xOffset="Variable:N"
).properties(
    title=f"Comparaison de {selected_variable} par commune et par année",
    width=150,
    height=450
).configure_view(
    stroke=None
)

# Ajouter du texte sur les barres
text = chart.mark_text(align='center', baseline='middle', dy=-5).encode(
    text=alt.Text('Valeur:Q', format=',.0f'),
    color=alt.value('black')
)

# Combiner le graphique et le texte
final_chart = chart + text

# Afficher dans Streamlit
st.title("Visualisation des Données")
st.altair_chart(final_chart, use_container_width=True)
