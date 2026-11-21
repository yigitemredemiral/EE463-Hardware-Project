# RevF4 simulation and thermal analysis

Scripts behind the final report (`reports/FinalReport`). Run from this folder with `OUT` set to an output folder.

1. `gen.py` – makes the netlist variants from `base.net` (steady state, light load, load/line step, start-up, overload, FRA) and runs LTspice in batch mode.
2. `analyze.py` – efficiency, ripple and loss breakdown → `results.json`.
3. `figs_circuit.py`, `fra_plot.py` – circuit figures, loop gain.
4. `th_export.py` (KiCad Python, board file as argument) – copper raster of the board → `cu.npz`, `cu.json`.
5. `figs_thermal.py` – 4-layer thermal model (`thermal.py`, `pcbmodel.py`): 5-minute and steady-state temperatures; DC current flow (`irdrop.py`).
6. `make_values.py` – all numbers used in the report → `values.tex`.
