
#config
from scripts.path import PATH
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
from scripts.functions import fill_holes, extract_relevant_polygon, ox_to_csv, compress_file
from parameters.parameters import  networktypes, osmnxparameters



def main(PATH, cities):
    
    # Initialize a list to store timing information
    timing_data = []

    # File to store the timing information
    timing_file = PATH["data"] / "01_download_times.csv"

    for placeid, placeinfo in tqdm(cities.items(), desc="Cities"):
        start_time_city = time.time()  # Start timing for the city
        
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
            start_time_network = time.time()  # Start timing for the network type
            
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

            end_time_network = time.time()  # End timing for the network type
            network_duration = end_time_network - start_time_network
            timing_data.append([placeid, parameterid, network_duration])  # Record timing data

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

        end_time_city = time.time()  # End timing for the city
        city_duration = end_time_city - start_time_city
        timing_data.append([placeid, "total_city_time", city_duration])  # Record total time for the city

    # Write timing data to CSV
    with open(timing_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["PlaceID", "NetworkType", "Time (seconds)"])  # CSV header
        writer.writerows(timing_data)

    print(f"Timing information saved to {timing_file}")

    # Compress all data files
    for folder, subfolders, files in os.walk(PATH["data"]):
        for file in files:
            if file.endswith('es.csv'):
                compress_file(folder, file.split(".")[0])
    pass

if __name__ == "__main__":
    main()
