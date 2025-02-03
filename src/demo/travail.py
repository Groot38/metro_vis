import streamlit as st
import matplotlib.pyplot as plt
from utils import load_data
import pandas as pd

data,meta_data,nom_commune= load_data()

#Évolution de la proportion actifs/retraités

actifs = data[["P10_ACTOCC15P", "P15_ACTOCC15P", "P21_ACTOCC15P"]]
retraites = data[["C10_POP15P_CS7", "C15_POP15P_CS7", "C21_POP15P_CS7"]]
prop_actifs_retraites = pd.DataFrame(index=range(49),columns=["2010","2015","2020"])
for i in range(len(actifs)):
    for j in range(3):
        act = actifs.iloc[i,j]
        ret = retraites.iloc[i,j]
        prop_actifs_retraites.iloc[i,j] = act/(act+ret)

sum_prop_ar = prop_actifs_retraites.apply(pd.Series.mean,axis = 0)

fig, ax = plt.subplots(figsize=(8, 3))  

ax.plot(sum_prop_ar.values)

# Éléments de mise en forme
annees = [2010, 2015, 2021]
ax.set_xticks(range(len(annees)))
ax.set_xticklabels(annees)
ax.set_title("Proportion d'actifs par rapport aux retraités")
ax.set_xlabel("Années")
ax.set_ylabel("Pourcentage")
ax.legend()
ax.set_ylim(bottom=0,top = 1)

# Affichage avec Streamlit
st.pyplot(fig)
