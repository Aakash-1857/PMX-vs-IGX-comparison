# PMX vs IGX Crossover for TSP (Chandigarh–Mohali, 17 nodes): Re-run Results

## Setup
- The original `pmx_igx_chandigarh_mohali.py` was copied **unmodified** into this folder and run there. Existing files in `tsp_outputs/` were not touched.
- The only environment change was a `.venv` with numpy, pandas and matplotlib. The first run failed with `ModuleNotFoundError: matplotlib`.
- Problem: 1 depot + 16 stops. Distances are Haversine straight-line km, **not road distances**.
- GA: population 60, 250 generations, crossover prob 0.9, mutation prob 0.2 (swap or inversion), tournament size 3, elitism 2.
- 30 seeds (1000–1029) per operator. Both operators use the same distance matrix.
- Exact reference: Held-Karp, **33.1656 km** (computed in 0.73 s).
- Raw log: `run_log.txt`. Run-level data: `tsp_outputs/run_results.csv`. Best routes and exact route: `tsp_outputs/summary.json`.
- Figures: `tsp_outputs/fig1_route_distance.png`, `fig2_runtime.png`, `fig3_convergence.png`, `route_pmx.png`, `route_igx.png`.

## Results (30 runs per method)
| Metric | PMX | IGX |
|---|---|---|
| Mean best distance (km) | 33.3979 | 33.2658 |
| Std dev (km) | 0.3400 | 0.2623 |
| Median (km) | 33.1666 | 33.1656 |
| Min (km) | 33.1656 | 33.1656 |
| Max (km) | 33.9726 | 33.9726 |
| Mean gap to optimum | 0.700 % | 0.302 % |
| Runs hitting exact optimum | 13/30 | 26/30 |
| Runs within 0.01 % of optimum | 20/30 | 26/30 |
| Runs with gap > 0.5 % | 10/30 | 4/30 |
| Mean runtime per run (s) | 0.061 | 0.213 |

## Comparison
- IGX mean distance is 0.132 km (0.40 %) lower than PMX. Its mean gap to optimum is 0.302 % against 0.700 % for PMX, about 57 % lower.
- IGX hit the exact optimum in twice as many runs (26 vs 13).
- IGX is about 3.5× slower in this run (0.213 s vs 0.061 s per run).
- Both operators found the exact optimum at best, and both had the same worst-case run (33.9726 km).

## Agreement with the shipped README
- **Distances reproduced exactly.** The means (33.3979 and 33.2658 km), the optimum (33.1656 km) and the hit counts (13/30 and 26/30) all match.
- **Runtimes differ.** README reports 0.195 s (PMX) and 0.685 s (IGX), against 0.061 s and 0.213 s here. This is a hardware and environment effect. The IGX/PMX ratio is about 3.5× in both.

## Observations
- Failures are discrete local optima, not slow convergence. The suboptimal runs end at gaps of about 0.003 %, 1.77 % or 2.43 %. IGX has 4 such runs and PMX has 17.
- The mean convergence curves are in `fig3_convergence.png`. I did not extract per-generation numbers.
- The 17-node instance is small. Held-Karp solves it exactly in 0.73 s on this machine. That is slower than one GA run (0.06 s PMX, 0.21 s IGX), but the GA gives no guarantee of optimality, and one PMX or IGX run stays under 1 s. At this size the exact method is still cheap, so the GA has little practical advantage here.

## Not done
- The README's Wilcoxon tests (distance p=0.067, runtime p<0.001) were **not recomputed**. That would need new analysis code, which the task prohibits. No significance claim is made here.
- With p=0.067 reported, the distance advantage of IGX is not statistically significant at 0.05, so it should be called a trend.

## Conclusion
On this instance and under these settings, IGX gave better average solution quality and a higher exact-optimum rate than PMX (26/30 vs 13/30), at about 3.5× the runtime. The results are specific to this single 17-node Haversine instance and do not show that IGX generalises.
