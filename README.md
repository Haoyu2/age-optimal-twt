# Age-Optimal Target Wake Time

**Provably Good Wake Schedules for Energy-Constrained Wi-Fi Status Updating**

Haoyu Wang, Bo Sheng (University of Massachusetts Boston);
Xiaoqian Zhang (University of Nebraska Omaha)

This repository is the reproducibility artifact for the paper. It contains the
ns-3 implementation of a Target Wake Time (TWT) mechanism, the
**Harmonic-Greedy** AoI-aware scheduler, every script needed to regenerate the
paper's results, and the **raw result data** from the reported sweeps.

- 📄 [Paper](paper/age-optimal-twt.pdf) · [Technical report (full proofs)](paper/age-optimal-twt-techreport.pdf)
- 📐 [Primer: the TWT AoI renewal-reward formula](docs/PRIMER-aoi-renewal.md)

## What's here

```
artifact/
  ns3-aoi-twt-module/   ns-3 contrib module: AoI model + schedulers + tests
  src-wifi/             TWT power-save manager (drops into ns-3 src/wifi)
  scratch/              single- and multi-station experiments
  scripts/              sweep drivers, lower bound, figure/macro generators
  results/              raw result CSVs + generated figures from the paper
paper/                  compiled paper and technical report
docs/                   primer + project landing page
```

## Requirements

- ns-3.48 (a stock checkout), CMake ≥ 3.25, a C++20 compiler
- Python 3 with `matplotlib` (for the figures only)

## Build

From a stock ns-3.48 tree:

```bash
# 1. install the mechanism and the module
cp artifact/src-wifi/twt-power-save-manager.{h,cc} ns-3/src/wifi/model/
#    register both files in src/wifi/CMakeLists.txt (SOURCE_FILES / HEADER_FILES)
cp -r artifact/ns3-aoi-twt-module ns-3/contrib/aoi-twt
cp artifact/scratch/*.cc ns-3/scratch/

# 2. configure + build
cd ns-3
./ns3 configure --enable-modules=aoi-twt,wifi,internet,applications \
                --enable-tests --enable-examples
./ns3 build
```

## Reproduce the results

```bash
# unit tests (closed-form AoI, schedule feasibility incl. the analyzed variant)
./test.py -s aoi-twt

# single-station model validation (renewal formula vs packet-level sim)
./ns3 run "twt-aoi-validation --simTime=300 --errorRate=0.4"

# the headline three-scheduler comparison (one regime)
./ns3 run "twt-aoi-multista --scheduler=ns3::HarmonicGreedyTwtScheduler \
           --weightSkew=8 --uniformBudget=0.12 --simTime=300"

# full sweep -> results.csv -> LaTeX macros + figures
python3 artifact/scripts/run_sweep.py 28
python3 artifact/scripts/make_macros.py results.csv results_macros.tex
python3 artifact/scripts/lower_bound.py 10 lb_macros.tex
python3 artifact/scripts/make_figs.py . figures
```

## Schedulers

All implement a common `TwtScheduler` interface (`artifact/ns3-aoi-twt-module/model/`):

- `EqualIntervalTwtScheduler` — naive baseline (one common period).
- `EnergyGreedyTwtScheduler` — strong baseline: shortest budget-feasible
  period per station, then harmonic packing (period-diverse, AoI-unaware).
- `HarmonicGreedyTwtScheduler` — ours: AoI-weighted square-root relaxation,
  anchor-optimized harmonic rounding, small-first best-fit packing,
  best-of-uniform safeguard. Set `DyadicReservations=true`, `DensityTarget=0.25`
  for the variant covered by the approximation theorems.

## Citation

```bibtex
@inproceedings{wang26aoitwt,
  author    = {Wang, Haoyu and Sheng, Bo and Zhang, Xiaoqian},
  title     = {Age-Optimal Target Wake Time: Provably Good Wake Schedules
               for Energy-Constrained {Wi-Fi} Status Updating},
  booktitle = {Proc. ACM MSWiM},
  year      = {2026}
}
```

## License

Code is GPL-2.0 (matching ns-3). See [LICENSE](LICENSE).
