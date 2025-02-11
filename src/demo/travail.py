import streamlit as st
import matplotlib.pyplot as plt
from utils import load_data
import pandas as pd
import re
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

data,meta_data,nom_commune= load_data()

########################################################## Sidebar ###################################################################

st.sidebar.title("Options")
if st.sidebar.checkbox("Afficher les données brutes"):
    st.write(data)
selected_years = []
if st.sidebar.checkbox("2010",value = True):
    selected_years.append("10")
if st.sidebar.checkbox("2015",value = True):
    selected_years.append("15")
if st.sidebar.checkbox("2021",value = True):
    selected_years.append("21")

if selected_years == []:
    selected_years.append("21")

year_pattern = "|".join(selected_years)

selection_sex = st.sidebar.radio(
    "",
    ("Homme", "Femme", "Les deux"),
)

# Affichage du bouton sélectionné
if selection_sex  == "Homme":
    pattern_sex = "H"
    st.session_state["selected_variable"] = None
elif selection_sex  == "Femme":
    pattern_sex = "F"
    st.session_state["selected_variable"] = None
else:
    pattern_sex = "POP"
    st.session_state["selected_variable"] = None

#Évolution de la proportion actifs/retraités
pattern = re.compile(f"^[C]({year_pattern})_({pattern_sex})15P_CS\d*$")
filtered_meta_data = meta_data[meta_data["COD_VAR"].astype(str).str.match(pattern)]

# Filtrage des données pour analyse
variables = filtered_meta_data["LIB_VAR_LONG"]
variables=list(dict.fromkeys(var[:-8] for var in variables))

filtered_meta_data["LIB_VAR_LONG_trimmed"] = filtered_meta_data["LIB_VAR_LONG"].str[:-8]
filtered_meta_data["CSP"] = filtered_meta_data["LIB_VAR_LONG_trimmed"].str.extract(r"plus (.+)")
cod_var = filtered_meta_data["COD_VAR"]

selected_columns = [col for col in data.columns if col in cod_var.values]

filtered_data_global = pd.DataFrame(data[selected_columns].apply(sum,axis = 0))
filtered_data_global["subcat"] = filtered_data_global.index.str[-3:]
filtered_data_global["Catégorie"] = filtered_data_global.index.str[:3]
filtered_data_global["Valeur"] = filtered_data_global[0]
CSP = pd.DataFrame(filtered_meta_data["CSP"].drop_duplicates())
CSP["indice"] = range(1,9)
filtered_data_global["indice"] = filtered_data_global["subcat"].str[2].astype(int)
resultat = pd.merge(filtered_data_global, CSP, on="indice", how="left").sort_values(by = "Catégorie",ascending=True)
resultat["Année"] = "20"+resultat["Catégorie"].str[1:]

# Création du barplot
fig = px.bar(
    resultat, 
    x="Année", 
    y="Valeur", 
    color="CSP", 
    title="Diagramme empilé des catégories socio-professionneles", 
    labels={"Category": "Catégories", "Value": "Valeurs", "Subcategory": "Sous-catégories"},
    barmode="stack"
)
fig.update_traces(width=1)

# Affichage de la figure
st.write(fig)
st.markdown(
    "<p style='text-align: left; color: gray;'>"
    "Source : INSEE, Dossier Complet 2024</p>",
    unsafe_allow_html=True
)


# Sélection avec une regex pour récuperer les colonnes
pit = data.filter(regex = f"^[C]({year_pattern})_({pattern_sex})15P_CS[1-6]$")
retraites = data.filter(regex=fr'^C({year_pattern})_({pattern_sex})15P_CS7$')
if pattern_sex == "POP" :
    chomeurs = data.filter(regex=fr'^P({year_pattern})_CHOM1564')
else :
    chomeurs = data.filter(regex=fr'^P({year_pattern})_({pattern_sex})CHOM1564$')

actifs_mel = pit.T
actifs_mel["Année"] = "20"+actifs_mel.index.str[1:3]
actifs_mel = actifs_mel.groupby(by='Année').sum().apply(sum,axis=1)
#chomeurs = chomeurs.T.apply(sum,axis = 1)
#chomeurs.index = ["20" + year for year in reversed(selected_years)]
cotisant = actifs_mel#-chomeurs
cotisant = cotisant.sort_index()
retraites = retraites.T.apply(sum,axis=1)
retraites.index = ["20" + year for year in reversed(selected_years)]
retraites = retraites.sort_index()
rapport = cotisant/retraites

# Création de la figure avec des axes secondaires
fig = make_subplots(specs=[[{"secondary_y": True}]])
# Ajout de la première courbe (rapport démographique)
fig.add_trace(go.Scatter(
    x=rapport.index,
    y=rapport.values,
    mode='lines+markers',
    name='Rapport démographique **'
), secondary_y=True)

# Ajout de la deuxième courbe (actifs)
fig.add_trace(go.Scatter(
    x=rapport.index,
    y=cotisant.values,  # Assure la compatibilité avec les séries ou DataFrame
    mode='lines+markers',
    name="Cotisants *"
), secondary_y=False)

fig.add_trace(go.Scatter(
    x=rapport.index,
    y=retraites.values,  # Assure la compatibilité avec les séries ou DataFrame
    mode='lines+markers',
    name='Retraités'
), secondary_y=False)

# Mise en forme des titres et axes
fig.update_layout(
    title="Rapport des actifs occupés par rapport aux retraités",
    xaxis_title="Années",
    xaxis=dict(tickmode='array', tickvals=selected_years),
    yaxis=dict(range=[0, 1])
)

fig.update_yaxes(title_text="Proportion", range=[0, max(rapport.values)*1.5], secondary_y=True)
fig.update_yaxes(title_text="Population", range=[0, max(cotisant.values.flatten()) * 1.2], secondary_y=False)

# Affichage dans Streamlit
st.plotly_chart(fig)
st.markdown(
    "<p style='text-align: left; color: gray;'>"
    "* Le nombre de cotisants a été calculé avec les 6 catégories socio-professionnelles suivantes :<br>"
    "1. Agriculteurs exploitants<br>"
    "2. Artisans, commerçants et chefs d’entreprise<br>"
    "3. Cadres et professions intellectuelles supérieures<br>"
    "4. Professions Intermédiaires<br>"
    "5. Employés<br>"
    "6. Ouvriers<br>"
    "<br>"
    "** Le rapport démographique a été calculé en divisant le nombre de cotisants par le nombre de retraités.<br>"
    "<br>"
    "Source : INSEE, Dossier Complet 2024</p>",
    unsafe_allow_html=True
)

