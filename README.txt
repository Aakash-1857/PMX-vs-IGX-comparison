SUPPLEMENTARY MATERIAL: PMX vs IGX CHANDIGARH-MOHALI TSP CASE STUDY

Contents
- pmx_igx_chandigarh_mohali.py: Python implementation of the Genetic Algorithm comparison and Held-Karp exact reference.
- tsp_outputs/location_data.csv: 17 public location nodes (one depot + 16 destinations) and coordinates.
- tsp_outputs/distance_matrix_km.csv: Haversine geographic-distance matrix used by both algorithms.
- tsp_outputs/run_results.csv: all 60 run-level outcomes (30 per method), with route distance, runtime, exact reference distance, and optimality gap.
- tsp_outputs/summary.json: exact optimum and best route details.
- tsp_outputs/fig1_route_distance.png through fig4_best_route.png: figures included in the paper.

Experiment settings
Population = 60; generations = 250; crossover probability = 0.90; mutation probability = 0.20; tournament selection size = 3; elitism = 2; 30 seeds (1000-1029) per operator. Both algorithms use the same distance matrix and a fixed depot.

IMPORTANT LIMITATION
The case study uses coordinates of public places in Chandigarh and Mohali, but the objective uses Haversine straight-line distances. It is NOT a road-network distance matrix, driving-time model, or turn-by-turn route. The reported optimum is exact only for this coordinate-distance matrix. Do not present 33.1656 km as real driving mileage.

Reported results
- Exact Haversine-matrix optimum: 33.1656 km.
- PMX: mean best distance 33.3979 km; mean runtime 0.195 s; 13/30 exact-optimum hits.
- IGX: mean best distance 33.2658 km; mean runtime 0.685 s; 26/30 exact-optimum hits.
- Two-sided paired Wilcoxon test for distance: p = 0.067 (not significant at 0.05).
- Paired Wilcoxon test for runtime: p < 0.001.

Re-running
Requirements: Python 3, numpy, pandas, and matplotlib. Run from the folder containing this file:
    python pmx_igx_chandigarh_mohali.py
The script writes its data and results into the local tsp_outputs folder. Absolute runtime results may differ across hardware and software environments. The script is designed to reproduce run-level results; final paper figures have additional formatting and are included in the archive.
