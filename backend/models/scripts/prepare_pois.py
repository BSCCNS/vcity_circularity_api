#config
from scripts.path import PATH
debug = False

# System
import csv
from tqdm.notebook import tqdm
import time
from tqdm import tqdm

# Math/Data
import math
import numpy as np
import pandas as pd

# Plotting
import matplotlib.pyplot as plt

# Geo
import osmnx as ox
ox.settings.log_file = True
ox.settings.requests_timeout = 300
ox.settings.logs_folder = PATH["logs"]
import fiona
import shapely
from haversine import haversine
import pyproj
from shapely.geometry import Polygon

# Local
from scripts.functions import fill_holes, extract_relevant_polygon, csv_to_ox, count_and_merge, rotate_grid, reverse_bearing
from parameters.parameters import  gridl, bearingbins, poiparameters, osmnxparameters, snapthreshold



def main(PATH, cities):
    # Load all carall graphs in OSMNX format
    G_caralls = {}
    G_caralls_simplified = {}
    locations = {}
    parameterinfo = osmnxparameters['carall']


    timing_data = []

    timing_file = PATH["data"] / "02_download_times.csv"


    # Iterate through cities to load polygons and graphs
    for placeid, placeinfo in tqdm(cities.items(), desc="Cities"):
        start_time_load = time.time()
        
        print(f"{placeid}: Loading location polygon and carall graph")
        
        # Check if 'nominatimstring' exists
        if placeinfo["nominatimstring"]:
            # Geocode to get the location geometry and extract relevant polygon
            location = ox.geocoder.geocode_to_gdf(placeinfo["nominatimstring"])
            location = fill_holes(extract_relevant_polygon(placeid, shapely.geometry.shape(location['geometry'][0])))
        else:
            # If shapefile is available, read and extract geometry
            with fiona.open(PATH["data"] / placeid / f"{placeid}.shp") as shp:
                first = next(iter(shp))
                try:
                    location = Polygon(shapely.geometry.shape(first['geometry']))  # Handle if LineString is present
                except:
                    location = shapely.geometry.shape(first['geometry'])  # Otherwise, it's likely a polygon
        locations[placeid] = location
        
        # Load and assign carall graphs for each city
        G_caralls[placeid] = csv_to_ox(PATH["data"] / placeid, placeid, 'carall')
        G_caralls[placeid].graph["crs"] = 'epsg:4326'  # Assign CRS for OSMNX compatibility
        G_caralls_simplified[placeid] = csv_to_ox(PATH["data"] / placeid, placeid, 'carall_simplified')
        G_caralls_simplified[placeid].graph["crs"] = 'epsg:4326'
        
        end_time_load = time.time()  # End timing for the network type
        load_duration = end_time_load - start_time_load
        timing_data.append([placeid, parameterinfo, load_duration])  # Record timing data


    for placeid, placeinfo in tqdm(cities.items(), desc="Cities"):
        start_time_download_POI = time.time()  # Start timing for the whole city
        print(f"{placeid}: Creating POIs")
        
        # Retrieve location geometry and simplified carall graph
        location = locations[placeid]
        G_carall = G_caralls_simplified[placeid]
        
        # Loop through POI parameters and process each tag
        for poiid, poitag in poiparameters.items():
            start_time_tags_POI = time.time()  # Start timing for each POI tag
            try:
                # Extract relevant geometries (Points only) from the location polygon
                gdf = ox.geometries.geometries_from_polygon(location, poitag)
                gdf = gdf[gdf['geometry'].type == "Point"]  # Only consider Points (exclude polygons)
                
                # Snap points to the nearest nodes in the network
                nnids = set()
                for g in gdf['geometry']:
                    n = ox.distance.nearest_nodes(G_carall, g.x, g.y)
                    # Only snap if within the defined threshold
                    if n not in nnids and haversine((g.y, g.x), (G_carall.nodes[n]["y"], G_carall.nodes[n]["x"]), unit="m") <= snapthreshold:
                        nnids.add(n)
                
                # Save nearest node ids for POIs in a CSV file
                output_file_path = PATH["data"] / placeid / f"{placeid}_poi_{poiid}_nnidscarall.csv"
                with output_file_path.open('w', newline='', encoding='utf-8') as f:
                    for item in nnids:
                        f.write(f"{item}\n")
                        
                # Convert the gdf to string type for writing, and save locally (if feasible)
                gdf = gdf.apply(lambda c: c.astype(str) if c.name != 'geometry' else c, axis=0)
                try:
                    gdf.to_file(PATH["data"] / placeid / f"{placeid}_poi_{poiid}.gpkg", driver='GPKG')
                except:
                    print(f"Notice: Writing the gdf did not work for {placeid}")
                
                if debug: gdf.plot(color='red')
            
            except Exception as e:
                print(f"No stations in {placeinfo['name']}. No POIs created. Error: {e}")
            
            # End timing for POI processing
            end_time_tags_POI = time.time()
            tags_duration = end_time_tags_POI - start_time_tags_POI
            timing_data.append([placeid, poiid, "POI Processing", tags_duration])
        
        # End timing for the whole download and processing for this city
        end_time_download_POI = time.time()
        download_POI_duration = end_time_download_POI - start_time_download_POI
        timing_data.append([placeid, None, "Download and Match", download_POI_duration])  # Record timing data




    # Create a grid for each city
    for placeid, placeinfo in tqdm(cities.items(), desc="Cities"):
        start_time_grid_creation = time.time()  # Start timing for grid creation
        print(f"{placeid}: Creating grid")
        
        location = locations[placeid]
        
        # First step: Calculate the most common bearing to orient the grid
        start_time_bearing_calc = time.time()  # Start timing for bearing calculation
        G = G_caralls[placeid]
        bearings = {}
        
        # Add edge bearings and calculate them for the network
        Gu = ox.bearing.add_edge_bearings(ox.get_undirected(G))
        city_bearings = []
        
        # Weight bearings by edge lengths
        for u, v, k, d in Gu.edges(keys=True, data=True):
            city_bearings.extend([d['bearing']] * int(d['length']))
        b = pd.Series(city_bearings)
        
        # Combine bearings for both directions and calculate bins
        bearings = pd.concat([b, b.map(reverse_bearing)]).reset_index(drop=True)
        bins = np.arange(bearingbins + 1) * 360 / bearingbins
        count = count_and_merge(bearingbins, bearings)
        
        # Determine the principal bearing for grid orientation
        principalbearing = bins[np.argmax(count)]
        if debug:
            print(f"Principal bearing: {principalbearing}")
        
        end_time_bearing_calc = time.time()  # End timing for bearing calculation
        bearing_calc_duration = end_time_bearing_calc - start_time_bearing_calc
        timing_data.append([placeid, "Bearing Calculation", bearing_calc_duration])  # Save timing data
        
        # Second step: Generate the grid with the calculated orientation
        start_time_grid_gen = time.time()  # Start timing for grid generation
        G = G_caralls_simplified[placeid]
        
        # Calculate buffer for snapping POIs to nodes outside the grid
        buf = max(((2 * snapthreshold) / 6378000) * (180 / math.pi),
                ((2 * snapthreshold) / 6378000) * (180 / math.pi) / math.cos(location.centroid.y * math.pi / 180))
        cities[placeid]["bbox"] = location.buffer(buf).bounds
        
        # Define projection for grid creation
        p_ll = pyproj.Proj('+proj=longlat +datum=WGS84')
        aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
        p_mt = pyproj.Proj(aeqd_proj.format(lat=location.centroid.y, lon=location.centroid.x))
        
        # Enlarge grid boundaries to account for rotation
        deltax = cities[placeid]["bbox"][2] - cities[placeid]["bbox"][0]
        deltay = cities[placeid]["bbox"][3] - cities[placeid]["bbox"][1]
        enlargefactor = 10
        sw = shapely.geometry.Point(cities[placeid]["bbox"][:2])
        ne = shapely.geometry.Point(cities[placeid]["bbox"][2:] + np.array([enlargefactor * deltax, enlargefactor * deltay]))
        
        # Project the SW and NE points
        transformed_sw = pyproj.transform(p_ll, p_mt, sw.x, sw.y)
        transformed_ne = pyproj.transform(p_ll, p_mt, ne.x, ne.y)
        
        # Define the principal bearing
        principalbearing %= 90
        if principalbearing > 45:
            principalbearing -= 90
        
        # Generate grid points
        xcoords = np.arange(transformed_sw[0], transformed_ne[0], gridl)
        ycoords = np.arange(transformed_sw[1], transformed_ne[1], gridl)
        
        gridpoints = np.dstack(np.meshgrid(xcoords, ycoords)).reshape(-1, 2)
        new_points = rotate_grid(gridpoints, origin=transformed_sw, degrees=principalbearing)
        
        # Project back to lat-lon
        fx, fy = pyproj.transform(p_mt, p_ll, new_points[:, 0], new_points[:, 1])
        gridpoints = np.vstack([fx, fy]).T
        
        # Adjust grid points based on rotation
        if principalbearing >= 0:
            gridpoints[:, 0] -= 0.4 * enlargefactor * deltax * np.sin(np.deg2rad(principalbearing))
        else:
            gridpoints[:, 0] += 0.4 * enlargefactor * deltax * np.sin(np.deg2rad(principalbearing))
            gridpoints[:, 1] -= 0.4 * enlargefactor * deltay
        
        # Filter grid points back to bounding box
        mask = (gridpoints[:, 0] >= cities[placeid]["bbox"][0]) & (gridpoints[:, 0] <= cities[placeid]["bbox"][2]) & \
            (gridpoints[:, 1] >= cities[placeid]["bbox"][1]) & (gridpoints[:, 1] <= cities[placeid]["bbox"][3])
        gridpoints_cut = gridpoints[mask]
        
        end_time_grid_gen = time.time()  # End timing for grid generation
        grid_gen_duration = end_time_grid_gen - start_time_grid_gen
        timing_data.append([placeid, "Grid Generation", grid_gen_duration])  # Save timing data
        
        # Optionally plot the grid points
        if debug:
            plt.figure(figsize=[12.8, 9.6])
            plt.plot(gridpoints_cut[:, 0], gridpoints_cut[:, 1], ".", color="red")
        
        # Start timing for snapping grid points
        start_time_snapping = time.time()
        
        # Snap grid points to the nearest nodes in the street network
        nnids = set()
        for g in gridpoints_cut:
            n = ox.distance.nearest_nodes(G, g[0], g[1])
            if n not in nnids and haversine((g[1], g[0]), (G.nodes[n]["y"], G.nodes[n]["x"]), unit="m") <= snapthreshold:
                nnids.add(n)
        
        # Save the snapped nodes to a CSV
        with (PATH["data"] / placeid / f"{placeid}_poi_grid_nnidscarall.csv").open('w', newline='', encoding='utf-8') as f:
            for item in nnids:
                f.write(f"{item}\n")
        
        # End timing for snapping grid points
        end_time_snapping = time.time()
        snapping_duration = end_time_snapping - start_time_snapping
        timing_data.append([placeid, "Snapping Grid Points", snapping_duration])  # Save timing data
        
        # End timing for overall grid creation for the city
        end_time_grid_creation = time.time()
        grid_creation_duration = end_time_grid_creation - start_time_grid_creation
        timing_data.append([placeid, "Total Grid Creation", grid_creation_duration])

    # Write timing data to CSV
    with open(timing_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["PlaceID", "NetworkType","ProcessStep", "Time (seconds)"])  # CSV header
        writer.writerows(timing_data)

    print(f"Timing information saved to {timing_file}")
    
    pass

if __name__ == "__main__":
    main()