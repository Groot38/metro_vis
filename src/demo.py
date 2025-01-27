import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

codes_insee = [ # Pour limiter sur la métropole
    "38057", "38059", "38071", "38068", "38111", "38126", "38150", "38151", 
    "38158", "38169", "38170", "38179", "38185", "38188", "38200", "38516", 
    "38187", "38317", "38471", "38229", "38235", "38258", "38252", "38271", 
    "38277", "38279", "38281", "38309", "38325", "38328", "38364", "38382", 
    "38388", "38421", "38423", "38436", "38445", "38472", "38474", "38478", 
    "38485", "38486", "38524", "38528", "38529", "38533", "38540", "38545", 
    "38562"
]
gdf = gpd.read_file('../data/iris_contours/iris_contours.shp')
back = gpd.read_file('../data/iris_contours/iris_contours.shp')

def load_data(filepath: str,geo: str = "IRIS"):
    data = pd.read_csv(filepath, sep=";", dtype={geo: str})
    return data[data[geo].str[:5].isin(codes_insee)]

def plot_iris(data_metro,obj: str,main: str,geo: str = "IRIS"):
    if geo == "IRIS" :
        gdf_new = gdf.merge(data_metro[["IRIS", obj]], left_on="CODE_IRIS", right_on="IRIS", how="right")
        gdf_new[obj] = pd.to_numeric(gdf_new[obj], errors='coerce')
        print("erreur")
    else : 
        gdf_new = gdf.merge(data_metro[["CODGEO", obj]], left_on="INSEE_COM", right_on="CODGEO", how="right")
        gdf_new[obj] = pd.to_numeric(gdf_new[obj], errors='coerce')
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
plot_iris(load_data("../data_insee/revenus_declares/BASE_TD_FILO_IRIS_2021_DEC.csv"),"DEC_MED21","Médiane")
# data_metro = load_data("../data_insee/dossier_complet/dossier_complet.csv","CODGEO")
# print(data_metro["C21_POP55P_CS7"])
# plot_iris(data_metro,"C21_POP55P_CS7","Retraités","Commune")

