# N-Queens: SAT Encodings vs CP vs ILP

A comprehensive empirical study comparing **5 SAT At-Most-One (AMO) encodings** against **Constraint Programming (CP)** and **Integer Linear Programming (ILP)** for solving the N-Queens problem at scale (*N* ∈ [8, 1024]).

This repository contains the full source code, benchmarking suite, visualization tools, and technical report for **Assignment 1** in *Modern Issues in Computer Science (INT3011E)*, VNU University of Engineering and Technology (VNU-UET).

---

## Key Findings

- **Best SAT Encoding:** The **Product (2D Grid) encoding** achieves the highest SAT scalability, solving *N* = 1024 in **13.37s** with Glucose3, outperforming Binary (22.36s) and Commander (19.44s).
- **Sequential Counter Pathology:** Despite producing the fewest clauses (Θ(*N*²)), the Sequential Counter encoding suffers from deep linear implication chains (s₁ → s₂ → ...), causing severe timeouts on Glucose3 from *N* ≥ 128. However, **CaDiCaL 153** solves Sequential up to *N* = 512 thanks to chronological backtracking.
- **Global Constraints vs. Flat CNF:** Commercial solvers leveraging global propagation—**Gurobi** (0.64s at *N* = 1024) and **IBM CPLEX CP Optimizer** (0.88s at *N* = 1024)—outperform SAT encodings by 1–2 orders of magnitude due to native domain filtering (Régin's bipartite matching).

---

## Solvers & Encodings Evaluated

| Paradigm | Solver Engine | Formulation / Approach |
|:---|:---|:---|
| **SAT** | **Glucose3** & **CaDiCaL 153** (PySAT) | **Binomial** (Pairwise, Θ(*n*²) clauses per line) |
| **SAT** | **Glucose3** & **CaDiCaL 153** (PySAT) | **Binary** (Bitwise, Θ(*n* log *n*) clauses) |
| **SAT** | **Glucose3** & **CaDiCaL 153** (PySAT) | **Sequential Counter** (Linear chain, 3*n* − 4 clauses) |
| **SAT** | **Glucose3** & **CaDiCaL 153** (PySAT) | **Commander Variable** (Hierarchical groups) |
| **SAT** | **Glucose3** & **CaDiCaL 153** (PySAT) | **Product** (2D grid decomposition) |
| **CP** | **Google OR-Tools CP-SAT** | Integer variables + `AllDifferent` global constraints |
| **CP** | **IBM CPLEX CP Optimizer** | Integer variables + `all_diff` global constraints |
| **ILP** | **Gurobi Optimizer** | Binary variables + linear inequalities + presolve |
| **ILP** | **IBM CPLEX MIP** | Binary variables + linear inequalities + presolve |

---

## Project Structure

```
.
├── nqueens_sat/                 # Core Python package
│   ├── encoders/                # 5 SAT AMO encodings
│   │   ├── binomial.py          #   Binomial (Pairwise)
│   │   ├── binary.py            #   Binary (Bitwise)
│   │   ├── sequential.py        #   Sequential counter
│   │   ├── commander.py         #   Commander variable
│   │   └── product.py           #   Product (2D Grid)
│   ├── baselines/               # Comparison baselines
│   │   ├── cp/                  #   CP-SAT (Google) & CPLEX CP (IBM)
│   │   └── ilp/                 #   Gurobi & CPLEX MIP (IBM)
│   ├── benchmark.py             # Isolated ProcessPool benchmark engine
│   ├── visualize.py             # Publication-quality plotting routines
│   └── utils.py                 # Independent solution correctness validator
├── results/                     # Experimental results
│   ├── benchmark_results.csv    # Raw benchmark data (runtimes, clauses, vars)
│   └── figures/                 # Generated plots (cactus, scaling, comparisons)
├── report/
│   └── main.pdf                 # Full technical report (Elsevier cas-sc format)
├── run_benchmark.py             # CLI entry point to run benchmarks
└── requirements.txt             # Python dependencies
```

---

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/huong1105/INT3011E-NQUEEN.git
cd INT3011E-NQUEEN

# Install dependencies
pip install -r requirements.txt
```

> **Note on Solvers:** 
> - PySAT (Glucose3, CaDiCaL) and Google OR-Tools are installed via `pip`.
> - Gurobi requires an active license (e.g., free Academic WLS license via `gurobi.lic`).
> - IBM CPLEX requires `cplex` and `docplex` with a valid installation/license.

### 2. Run Benchmarks

Run the complete benchmark suite across desired board sizes:

```bash
# Default quick run (N in [8, 16, 32, 64, 128])
python run_benchmark.py

# Full evaluation matching the paper (N up to 1024, 120s timeout)
python run_benchmark.py --sizes 8 16 32 64 128 256 512 1024 --timeout 120 --runs 3
```

Available CLI arguments:
- `--sizes`: List of board sizes *N* (e.g., `8 16 32 64 128 256 512 1024`).
- `--timeout`: Timeout in seconds per solver run (default: `60`).
- `--sat-solvers`: PySAT solver backends (`glucose3`, `cadical153`, etc.).
- `--runs`: Number of repeated runs to compute median runtime (default: `3`).
- `--force`: Force re-computation of existing cached results in CSV.
- `--output`: Path to output CSV file (default: `results/benchmark_results.csv`).

### 3. Generate Visualizations

Re-generate all publication-quality figures from benchmark CSV:

```bash
python -m nqueens_sat.visualize
```

Generated plots will be saved to `results/figures/`:
- `cactus_plot.png`: Cumulative solved instances vs. runtime across all solvers.
- `clauses_scaling.png`: Theoretical vs. empirical clause growth (log-log scale).
- `runtime_comparison.png`: SAT encodings runtime comparison.
- `solver_comparison.png`: Side-by-side comparison of Glucose3 vs. CaDiCaL 153.
- `encoding_overhead.png`: Encoding generation time vs. solving time.

---

## Technical Report

The comprehensive scientific report is compiled in Elsevier `cas-sc` format:
- **PDF Report:** [`report/main.pdf`](report/main.pdf)

---

## Author

- **Pham Van Huong** (24021510@vnu.edu.vn)
- Faculty of Information Technology, VNU University of Engineering and Technology (VNU-UET)
- Course: *Modern Issues in Computer Science (INT3011E)*, Fall 2026
