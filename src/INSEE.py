import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

codes_insee = [ # Pour limiter sur la métropole
    "38057", "38059", "38071", "38068", "38111", "38126", "38150", "38151", 
    "38158", "38169", "38170", "38179", "38185", "38188", "38200", "38516", 
    "38187", "38317", "38471", "38229", "38235", "38258", "38252", "38271", 
    "38277", "38279", "38281", "38309", "38325", "38328", "38364", "38382", 
    "38388", "38421", "38423", "38436", "38445", "38472", "38474", "38478", 
    "38485", "38486", "38524", "38528", "38529", "38533", "38540", "38545", 
    "38562"
]

gdf_iris = gpd.read_file('../data/iris_contours/iris_contours.shp')
#back_iris = gdf_iris#gpd.read_file('../data/iris_contours/iris_contours.shp')
# gdf_com = gpd.read_file('../data/iris_contours/communes-version-simplifiee.geojson')
# gdf_com = gdf_com[gdf_com["code"].isin(codes_insee)]
# gdf_com.to_file("../data/iris_contours/output_file.geojson")
gdf_com = gpd.read_file('../data/iris_contours/output_file.geojson')

def load_data(filepath: str,geo: str = "IRIS",filtre : bool = True):
    data = pd.read_csv(filepath, sep=",",dtype={geo: str})
    if filtre :
        return data[data[geo].str[:5].isin(codes_insee)]
    else : 
        return(data)

def update_data(filepath: str,geo: str = "IRIS"):
    data = load_data(filepath,geo)
    #print(data)
    os.remove(filepath)
    data.to_csv(filepath,index=False,encoding='utf-8')


def plot_iris(data_metro,obj: str,main: str = "Titre à changer",geo: str = "IRIS"):
    if geo == "IRIS" :
        gdf_new = gdf_iris.merge(data_metro[["IRIS", obj]], left_on="CODE_IRIS", right_on="IRIS", how="right")
        gdf_new[obj] = pd.to_numeric(gdf_new[obj], errors='coerce')
        back = gdf_iris
    else : 
        gdf_new = gdf_com.merge(data_metro[["CODGEO", obj]], left_on="code", right_on="CODGEO", how="right")
        gdf_new[obj] = pd.to_numeric(gdf_new[obj], errors='coerce')
        back = gdf_com

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    # Fond de carte gris
    back.plot(ax=ax, color='lightgrey', edgecolor='none')
    # Ajout des données et de la barre continue
    gdf_new.plot(
        column=obj,
        ax=ax,
        legend=True,
        cmap='viridis',
        legend_kwds={
            'shrink': 0.7, 
            'label': "Population", 
            'orientation': "vertical"
        }
    )

    ax.set_title(main)
    ax.set_axis_off()

    plt.show()

#plot_iris(load_data("../data_insee/revenus_disponibles/BASE_TD_FILO_IRIS_2021_DISP.csv"),"DISP_MED21","Médiane de revenu")
#plot_iris(load_data("../data_insee/revenus_declares/BASE_TD_FILO_IRIS_2021_DEC.csv"),"DEC_MED21","Médiane")
# data_metro = load_data("../data_insee/dossier_complet/dossier_complet.csv","CODGEO")
# print(data_metro["C21_POP55P_CS7"])
# plot_iris(data_metro,"C21_POP55P_CS7","Retraités","Commune")

#update_data("../data_insee/dossier_complet/dossier_complet.csv",geo= "CODGEO")

data = load_data("../data_insee/dossier_complet/dossier_complet.csv",geo = "CODGEO",filtre=False)
data['P21_POP0014_prop'] = data['P21_POP0014']/data['P21_POP']
plot_iris(data,"P21_POP0014_prop",geo = "CODGEO")
