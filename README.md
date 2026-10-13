# N-Queens: SAT Encodings vs CP vs ILP

A comprehensive empirical study comparing **5 SAT AMO encodings** against **Constraint Programming** and **Integer Linear Programming** for scalable N-Queens solving.

## Quick Start

```bash
pip install -r requirements.txt
python run_benchmark.py --sizes 8 16 32 64 128 256 --timeout 60
```

## Project Structure

```
nqueens/
├── nqueens_sat/                 # Python package
│   ├── encoders/                # 5 SAT AMO encodings (from nQueens-SAT-main)
│   │   ├── binomial.py          #   Pairwise — O(n²) clauses
│   │   ├── binary.py            #   Bitwise — O(n·log n) clauses
│   │   ├── sequential.py        #   Sequential counter — 3n−4 clauses
│   │   ├── commander.py         #   Commander variable
│   │   └── product.py           #   2D grid decomposition
│   ├── baselines/               # Comparison methods
│   │   ├── cp/                  #   CP-SAT (Google) · CPLEX CP (IBM)
│   │   └── ilp/                 #   Gurobi · CPLEX MIP (IBM)
│   ├── benchmark.py             # ProcessPool benchmark engine
│   ├── visualize.py             # Publication-quality plotting
│   └── utils.py                 # Solution verification
├── results/                     # Experimental output (CSV + figures)
├── report/                      # LaTeX manuscript (Elsevier cas-sc)
├── run_benchmark.py             # Entry point
└── requirements.txt
```

## Methods

| Category | Solver | Encoding / Approach |
|----------|--------|-------------------|
| **SAT** | PySAT (Glucose3) | Binomial, Binary, Sequential, Commander, Product |
| **CP** | Google CP-SAT | `AllDifferent` global constraint |
| **CP** | IBM CPLEX CP | `all_diff` constraint |
| **ILP** | Gurobi | Binary variables + linear inequalities |
| **ILP** | IBM CPLEX MIP | Binary variables + linear inequalities |

## Report

Scientific paper in Elsevier `cas-sc` format: [`report/`](report/)

## Data Availability

All source code, benchmark scripts, and raw experimental data are available in this repository.
