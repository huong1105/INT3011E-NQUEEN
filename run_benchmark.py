"""Entry point — run the complete N-Queens benchmark suite."""
import argparse
from nqueens_sat.benchmark import run
from nqueens_sat.visualize import generate_all


def main():
    parser = argparse.ArgumentParser(
        description="N-Queens: SAT Encodings vs CP vs ILP Benchmark")
    parser.add_argument(
        "--sizes", nargs="+", type=int,
        default=[8, 16, 32, 64, 128],
        help="Board sizes to evaluate (default: 8 16 32 64 128)")
    parser.add_argument(
        "--timeout", type=int, default=60,
        help="Timeout per solver run in seconds (default: 60)")
    parser.add_argument(
        "--output", type=str, default="results/benchmark_results.csv",
        help="CSV output path")
    parser.add_argument(
        "--sat-solvers", "--sat-solver", nargs="+", default=["glucose3", "cadical153"],
        help="PySAT solver backends to evaluate (e.g. glucose3 cadical153 minisat22)")
    parser.add_argument(
        "--runs", type=int, default=3,
        help="Number of runs per configuration to compute median runtime (default: 3)")
    parser.add_argument(
        "--force", action="store_true",
        help="Force recomputation of existing benchmark records")
    args = parser.parse_args()

    run(
        sizes=args.sizes,
        timeout=args.timeout,
        output_csv=args.output,
        sat_solver=args.sat_solvers,
        runs=args.runs,
        force=args.force
    )

    generate_all(csv_path=args.output)

if __name__ == "__main__":
    main()
