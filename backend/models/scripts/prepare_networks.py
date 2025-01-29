
#config
from backend.models.scripts.path import PATH
debug = False

# System
import csv
import os
import time
from tqdm import tqdm

# Math/Data
import numpy as np

# Network
import networkx as nx

# Plotting
import matplotlib.pyplot as plt
from matplotlib import cm

print("PATH:", PATH)
# Geo
import osmnx as ox
ox.settings.log_file = True
ox.settings.requests_timeout = 300
ox.settings.logs_folder = PATH["logs"]
import fiona
import shapely

# Local
from backend.models.scripts.functions import fill_holes, extract_relevant_polygon, ox_to_csv, compress_file
from backend.models.parameters.parameters import  networktypes, osmnxparameters

def main(PATH, cities):

    for placeid, placeinfo in tqdm(cities.items(), desc="Cities"):

        if placeinfo["nominatimstring"] != '':
            location = ox.geocoder.geocode_to_gdf(placeinfo["nominatimstring"])
            location = fill_holes(extract_relevant_polygon(placeid, shapely.geometry.shape(location['geometry'][0])))
            if debug:  # Draw location polygons and their holes
                try:
                    color = cm.rainbow(np.linspace(0,1,len(location)))
                    for poly,c in zip(location, color):
                        plt.plot(*poly.exterior.xy, c=c)
                        for intr in poly.interiors:
                            plt.plot(*intr.xy, c="red")
                except:
                    plt.plot(*location.exterior.xy)
                plt.show()
        else:
            # Read shapefile
            shp = fiona.open(PATH["data"] + placeid / placeid + ".shp")
            first = next(iter(shp))
            location = shapely.geometry.shape(first['geometry'])
        
        Gs = {}
        for parameterid, parameterinfo in tqdm(osmnxparameters.items(), desc="Networks", leave=False):
            
            for i in range(0, 10):  # retry loop
                try:
                    Gs[parameterid] = ox.graph_from_polygon(location, 
                                        network_type=parameterinfo['network_type'],
                                        custom_filter=parameterinfo['custom_filter'],
                                        retain_all=parameterinfo['retain_all'],
                                        simplify=False)
                except ValueError:
                    Gs[parameterid] = nx.empty_graph(create_using=nx.MultiDiGraph)
                    print(placeid + ": No OSM data for graph " + parameterid + ". Created empty graph.")
                    break
                except (ConnectionError, UnboundLocalError):
                    print("ConnectionError or UnboundLocalError. Retrying.")
                    continue
                except Exception as e:
                    print(f"Other error: {e}. Retrying.")
                    continue
                break

            if parameterinfo['export']:
                ox_to_csv(Gs[parameterid], PATH["data"] / placeid, placeid, parameterid)

        # Compose special cases
        parameterid = 'biketrack'
        Gs[parameterid] = nx.compose_all([
            Gs['bike_cyclewaylefttrack'], Gs['bike_cyclewaytrack'], 
            Gs['bike_highwaycycleway'], Gs['bike_bicycleroad'], 
            Gs['bike_cyclewayrighttrack'], Gs['bike_designatedpath'], 
            Gs['bike_cyclestreet']
        ])
        ox_to_csv(Gs[parameterid], PATH["data"] / placeid, placeid, parameterid)

        parameterid = 'bikeable'
        Gs[parameterid] = nx.compose_all([Gs['biketrack'], Gs['car30'], Gs['bike_livingstreet']])
        ox_to_csv(Gs[parameterid], PATH["data"] / placeid, placeid, parameterid)

        parameterid = 'biketrackcarall'
        Gs[parameterid] = nx.compose(Gs['biketrack'], Gs['carall'])  # Order is important
        ox_to_csv(Gs[parameterid], PATH["data"] / placeid, placeid, parameterid)

        # Simplify and save graphs
        for parameterid in networktypes[:-2]:
            ox_to_csv(ox.simplify_graph(Gs[parameterid]), PATH["data"] / placeid, placeid, parameterid, "_simplified")

    # Compress all data files
    for folder, subfolders, files in os.walk(PATH["data"]):
        for file in files:
            if file.endswith('es.csv'):
                compress_file(folder, file.split(".")[0])
    pass

if __name__ == "__main__":
    main()
