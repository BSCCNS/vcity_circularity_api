#from scripts.initialize import *


#config
from pathlib import Path
from backend.models.scripts.path import PATH
debug = True

# System
import csv
import os
import pickle
import warnings
import time
from tqdm import tqdm
import copy

# Network
import igraph as ig
from shapely.geometry import Polygon

# Local
from backend.models.scripts.functions import csv_to_ig, calculate_metrics_parallel, delete_overlaps, intersect_igraphs, calculate_metrics_additively, write_result
from backend.models.parameters import poi_source, prune_measure, networktypes, buffer_walk, numnodepairs


def main(PATH, cities):
        
    warnings.filterwarnings('ignore')
    rerun_existing = True


    for placeid, placeinfo in cities.items():
        print(placeid + ": Analyzing existing infrastructure.")
        
        # Filename check
        rerun_check = rerun_existing or not os.path.isfile(PATH["results"] + placeid + "/" + filename)


        if rerun_check:
            empty_metrics = {
                            "length":0,
                            "length_lcc":0,
                            "coverage": 0,
                            "directness": 0,
                            "directness_lcc": 0,
                            "poi_coverage": 0,
                            "components": 0,
                            "efficiency_global": 0,
                            "efficiency_local": 0,
                            "efficiency_global_routed": 0,
                            "efficiency_local_routed": 0,
                            "directness_lcc_linkwise": 0,
                            "directness_all_linkwise": 0
                            }
            output_place = {}
            for networktype in networktypes:
                output_place[networktype] = copy.deepcopy(empty_metrics)

            # Analyze all networks
            Gs = {}
            for networktype in networktypes:
                if networktype != "biketrack_onstreet" and networktype != "bikeable_offstreet":
                    Gs[networktype] = csv_to_ig(PATH["data"] / placeid, placeid, networktype)
                    Gs[networktype + "_simplified"] = csv_to_ig(PATH["data"] / placeid , placeid, networktype + "_simplified")
                elif networktype == "biketrack_onstreet":
                    Gs[networktype] = intersect_igraphs(Gs["biketrack"], Gs["carall"])
                    Gs[networktype + "_simplified"] = intersect_igraphs(Gs["biketrack_simplified"], Gs["carall_simplified"])
                elif networktype == "bikeable_offstreet":
                    G_temp = copy.deepcopy(Gs["bikeable"])
                    delete_overlaps(G_temp, Gs["carall"])
                    Gs[networktype] = G_temp
                    G_temp = copy.deepcopy(Gs["bikeable_simplified"])
                    delete_overlaps(G_temp, Gs["carall_simplified"])
                    Gs[networktype + "_simplified"] = G_temp


            # Load POIs

            with open(Path(PATH["data"]) / placeid / f"{placeid}_poi_{poi_source}_nnidscarall.csv") as f:
                nnids = [int(line.rstrip()) for line in f]


            # Metrics calculation

            covs = {}
            for networktype in tqdm(networktypes, desc="Networks", leave=False):
                if debug: print(placeid + ": Analyzing results: " + networktype)
                metrics, cov = calculate_metrics_parallel(Gs[networktype], Gs[networktype + "_simplified"], Gs['carall'], nnids, empty_metrics, buffer_walk, numnodepairs, debug)
                for key, val in metrics.items():
                    output_place[networktype][key] = val
                covs[networktype] = cov

            # Save covers
            write_result(covs, "pickle", placeid, "", "", "existing_covers.pickle")

            # Write to CSV
            write_result(output_place, "dictnested", placeid, "", "", "existing.csv", empty_metrics)



    for placeid, placeinfo in cities.items():
        print(placeid + ": Analyzing results")


        G_carall = csv_to_ig(PATH["data"] / placeid , placeid, 'carall')
        Gexisting = {}
        for networktype in ["biketrack", "bikeable"]:
            Gexisting[networktype] = csv_to_ig(PATH["data"] / placeid , placeid, networktype)


        # Load POIs

        file_path = Path(PATH["data"]) / placeid / f"{placeid}_poi_{poi_source}_nnidscarall.csv"
        with open(file_path) as f:
            nnids = [int(line.rstrip()) for line in f]

        # Load results
        filename = f"{placeid}_poi_{poi_source}_{prune_measure}.pickle"
        resultfile_path = PATH["results"] / placeid / filename
        with open(resultfile_path, 'rb') as resultfile:
            res = pickle.load(resultfile)


        # Calculate metrics
        start_time_metrics = time.time()
        output, covs = calculate_metrics_additively(
            res["GTs"], res["GT_abstracts"], res["prune_quantiles"], G_carall, nnids,
            buffer_walk, numnodepairs, debug, True, Gexisting
        )
        output_MST, cov_MST = calculate_metrics_parallel(
            res["MST"], res["MST_abstract"], G_carall, nnids, output,
            buffer_walk, numnodepairs, debug, True, ig.Graph(), Polygon(), False, Gexisting
        )
        end_time_metrics = time.time()
        metrics_calculation_duration = end_time_metrics - start_time_metrics

        # Save the covers
        write_result(covs, "pickle", placeid, poi_source, prune_measure, "_covers.pickle")
        write_result(cov_MST, "pickle", placeid, poi_source, prune_measure, "_cover_mst.pickle")


        write_result(output, "dict", placeid, poi_source, prune_measure, ".csv")
        write_result(output_MST, "dict", placeid, poi_source, "", "mst.csv")



    
    pass

if __name__ == "__main__":
    main()