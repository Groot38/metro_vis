import streamlit as st
import matplotlib.pyplot as plt
from utils import load_data
import pandas as pd
import re
import plotly.express as px

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

# filtered_data_geo = data[["CODGEO"] + selected_columns]
# filtered_data_geo = filtered_data_geo.merge(nom_commune[["code_insee", "nom_commune"]], 
#                                      left_on="CODGEO", right_on="code_insee", 
#                                      how="left").drop(columns=["code_insee"])

filtered_data_global = pd.DataFrame(data[selected_columns].apply(sum,axis = 0))
filtered_data_global["subcat"] = filtered_data_global.index.str[-3:]
filtered_data_global["Catégorie"] = filtered_data_global.index.str[:3]
filtered_data_global["Valeur"] = filtered_data_global[0]
CSP = pd.DataFrame(filtered_meta_data["CSP"].drop_duplicates())
CSP["indice"] = range(1,9)
filtered_data_global["indice"] = filtered_data_global["subcat"].str[2].astype(int)
resultat = pd.merge(filtered_data_global, CSP, on="indice", how="left").sort_values(by = "Catégorie",ascending=True)
st.write(resultat)
resultat["Année"] = "20"+resultat["Catégorie"].str[1:]
# Création du barplot empilé avec Plotly Express
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








































































































import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Données fournies
actifs = data[["P10_ACTOCC15P", "P15_ACTOCC15P", "P21_ACTOCC15P"]]
retraites = data[["C10_POP15P_CS7", "C15_POP15P_CS7", "C21_POP15P_CS7"]]
prop_actifs_retraites = pd.DataFrame(index=range(49), columns=["2010", "2015", "2020"])

# Calcul des proportions actifs/retraités
for i in range(len(actifs)):
    for j in range(3):
        act = actifs.iloc[i, j]
        ret = retraites.iloc[i, j]
        prop_actifs_retraites.iloc[i, j] = act / (act + ret) if (act + ret) != 0 else 0

# Moyennes des proportions par année
sum_prop_ar = prop_actifs_retraites.apply(pd.Series.mean, axis=0)

# Création de la figure avec Plotly
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[2010, 2015, 2020],
    y=sum_prop_ar.values,
    mode='lines+markers',
    name='Proportion Actifs/Retraites'
))

# Mise en forme du graphique
fig.update_layout(
    title="Proportion d'actifs par rapport aux retraités",
    xaxis_title="Années",
    yaxis_title="Proportion",
    xaxis=dict(tickmode='array', tickvals=[2010, 2015, 2020]),
    yaxis=dict(range=[0, 1])
)

# Affichage
st.write(fig)

