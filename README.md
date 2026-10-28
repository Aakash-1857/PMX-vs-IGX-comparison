# PMX vs IGX Crossover for the Traveling Salesman Problem

Performed a comparison of two genetic-algorithm crossover operators, Partially Mapped Crossover (PMX) and Distance-Guided Crossover (IGX), on a 17-node Chandigarh–Mohali TSP case study. The GA results are checked against an exact Held-Karp optimum.

### Members in the Project

| Name | Roll No. |
|---|---|
| Aakash Gupta | 2024UCM2848 |
| Himanshi | 2024UCM2331 |
| Navratan | 2024UCM2321 |
| Jhanvi | 2024UCM2848 |

## Repository Structure

```
.
├── pmx_igx_chandigarh_mohali.py   # GA (PMX, IGX) + Held-Karp exact solver + plotting
├── tsp_outputs/                   # Original outputs supplied with the paper
│   ├── location_data.csv          # 17 nodes (1 depot + 16 stops) with coordinates
│   ├── distance_matrix_km.csv     # Haversine distance matrix
│   ├── run_results.csv            # 60 run-level results (30 per method)
│   ├── summary.json               # Exact optimum and best routes
│   └── fig1–fig4 *.png            # Figures from the paper
└── results_rerun/                 # Independent re-execution of the unmodified script
    ├── RESULTS.md                 # Setup, results and conclusions of the re-run
    ├── run_log.txt
    └── tsp_outputs/               # Re-run data and figures
```

## Experimental Setup

| Parameter | Value |
|---|---|
| Instance | 17 locations (fixed depot: Chandigarh Railway Station) |
| Population / generations | 60 / 250 |
| Crossover / mutation probability | 0.90 / 0.20 (swap or inversion) |
| Selection | Tournament (size 3) |
| Elitism | 2 |
| Runs | 30 seeds (1000–1029) per operator |
| Exact reference | Held-Karp dynamic programming |

## Results

The figures below come from the re-run in `results_rerun/`. Distance results match the original outputs.

| Metric | PMX | IGX |
|---|---|---|
| Mean best distance (km) | 33.3979 | 33.2658 |
| Std. dev. (km) | 0.3400 | 0.2623 |
| Mean gap to optimum | 0.70 % | 0.30 % |
| Exact-optimum hits | 13/30 | 26/30 |
| Mean runtime per run (s) | 0.061 | 0.213 |

- IGX reaches the exact optimum in twice as many runs as PMX and has a lower mean gap, at about 3.5× the runtime.
- The paper reports a paired Wilcoxon test on distance of p = 0.067, which is not significant at 0.05. That test was not recomputed in the re-run.
- Runtimes depend on hardware. The shipped README reports 0.195 s (PMX) and 0.685 s (IGX), while the re-run measured about 3× lower values with the same IGX/PMX ratio.
- Results are for one small instance and do not show that IGX generalises.

See [`results_rerun/RESULTS.md`](results_rerun/RESULTS.md) for details.

## Reproducing

Requirements: Python 3, `numpy`, `pandas`, `matplotlib`.

```bash
pip install numpy pandas matplotlib
python pmx_igx_chandigarh_mohali.py
```

The script writes data and results to `tsp_outputs/`, **overwriting existing files**. To keep the originals, run a copy of the script from a separate folder, as done in `results_rerun/`. The final paper figures have extra formatting, so regenerated plots will look slightly different.

## Citation

If you use this material, please cite the accompanying paper (details to be added).
