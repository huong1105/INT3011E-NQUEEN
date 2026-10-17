"""Visualization module — generates publication-quality figures."""
import os
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 8.5,
    "figure.titlesize": 12,
})

ENCODING_COLORS = {
    "binomial": "#1f77b4",    # Blue
    "binary": "#ff7f0e",      # Orange
    "sequential": "#2ca02c",  # Green
    "commander": "#d62728",   # Red
    "product": "#9467bd",     # Purple
}

BASELINE_STYLES = {
    "CPLEX-CP":  {"color": "#e377c2", "marker": "s", "ls": "-",  "lw": 2.2, "label": "CPLEX-CP (IBM CP)"},
    "Gurobi":    {"color": "#bcbd22", "marker": "D", "ls": "-",  "lw": 2.2, "label": "Gurobi (MIP)"},
    "CPLEX-MIP": {"color": "#7f7f7f", "marker": "^", "ls": "-",  "lw": 1.8, "label": "CPLEX-MIP (IBM MIP)"},
    "CP-SAT":    {"color": "#8c564b", "marker": "o", "ls": "-.", "lw": 1.8, "label": "CP-SAT (Google CP)"},
}


def _prepare_df(df):
    d = df.copy()
    norm_map = {
        "cpsat": "CP-SAT",
        "cplexcp": "CPLEX-CP",
        "gurobi": "Gurobi",
        "cplexmip": "CPLEX-MIP",
    }
    def clean_solver_name(s):
        key = str(s).strip().lower().replace("-", "").replace("_", "")
        return norm_map.get(key, str(s).strip())

    if "solver" in d.columns:
        d["solver"] = d["solver"].apply(clean_solver_name)

    d = d.drop_duplicates(subset=["solver", "n"], keep="last")

    if "encoding" not in d.columns or d["encoding"].isna().all():
        def get_enc(row):
            if row["category"] == "SAT":
                s = str(row["solver"])
                return s.split("-")[0] if "-" in s else s
            return ""
        d["encoding"] = d.apply(get_enc, axis=1)

    if "sat_solver" not in d.columns or d["sat_solver"].isna().all():
        def get_backend(row):
            if row["category"] == "SAT":
                s = str(row["solver"])
                return s.split("-")[1] if "-" in s else "glucose3"
            return ""
        d["sat_solver"] = d.apply(get_backend, axis=1)

    if "solve_time_s" not in d.columns and "time_s" in d.columns:
        d["solve_time_s"] = d["time_s"]
    elif "time_s" not in d.columns and "solve_time_s" in d.columns:
        d["time_s"] = d["solve_time_s"]

    return d


def plot_clauses(df, output_dir):
    d = _prepare_df(df)
    df_sat = d[d["category"] == "SAT"]
    if df_sat.empty:
        return

    df_clauses = df_sat[df_sat["clauses"].notna()].copy()
    df_clauses["clauses"] = pd.to_numeric(df_clauses["clauses"], errors="coerce")
    df_clauses = df_clauses.dropna(subset=["clauses"]).drop_duplicates(subset=["encoding", "n"])

    fig, ax = plt.subplots(figsize=(8, 5))
    encodings = ["binomial", "binary", "sequential", "commander", "product"]
    markers = {"binomial": "o", "binary": "s", "sequential": "^", "commander": "D", "product": "v"}

    for enc in encodings:
        sub = df_clauses[df_clauses["encoding"] == enc].sort_values("n")
        if not sub.empty:
            ax.plot(
                sub["n"], sub["clauses"],
                color=ENCODING_COLORS.get(enc, "#333333"),
                marker=markers.get(enc, "o"),
                markersize=6,
                linewidth=1.8,
                label=enc.capitalize()
            )

    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("Board Size N")
    ax.set_ylabel("Number of CNF Clauses")
    ax.set_title("CNF Clause Scaling: 5 SAT AMO Encodings\n(Invariant to SAT Solver Backend)", fontsize=11, fontweight="bold")
    ax.grid(True, which="both", ls="--", alpha=0.4)
    ax.legend(loc="lower right", framealpha=0.9)
    plt.tight_layout()

    path = os.path.join(output_dir, "clauses_scaling.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: {path}")


def plot_runtime(df, output_dir):
    """Figure 2: Single plot comparing 5 SAT encodings (Glucose3) vs CP and ILP baselines."""
    d = _prepare_df(df)
    df_ok = d[d["status"] == "SAT"].copy()

    fig, ax = plt.subplots(figsize=(8.5, 5))
    encodings = ["binomial", "binary", "sequential", "commander", "product"]

    # 1. SAT encodings with Glucose3
    df_sat = df_ok[(df_ok["category"] == "SAT") & (df_ok["sat_solver"] == "glucose3")]
    sat_markers = {"binomial": "o", "binary": "s", "sequential": "^", "commander": "D", "product": "v"}

    for enc in encodings:
        sub = df_sat[df_sat["encoding"] == enc].sort_values("n")
        if not sub.empty:
            ax.plot(
                sub["n"], sub["solve_time_s"],
                color=ENCODING_COLORS.get(enc, "#333333"),
                marker=sat_markers.get(enc, "o"),
                ls="-",
                linewidth=1.8,
                markersize=6,
                label=f"SAT: {enc.capitalize()} (Glucose3)"
            )

    # 2. Baseline solvers (CP & ILP)
    for b_name, style in BASELINE_STYLES.items():
        sub = df_ok[df_ok["solver"] == b_name].sort_values("n")
        if not sub.empty:
            ax.plot(
                sub["n"], sub["solve_time_s"],
                color=style["color"],
                marker=style["marker"],
                ls=style["ls"],
                linewidth=style["lw"],
                markersize=6,
                label=style["label"]
            )

    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("Board Size N", fontweight="bold")
    ax.set_ylabel("Solving Time (seconds)", fontweight="bold")
    ax.set_title("Runtime Comparison: SAT (Glucose3) vs CP vs ILP", fontweight="bold")
    ax.grid(True, which="both", ls="--", alpha=0.4)
    ax.legend(loc="lower right", fontsize=8, framealpha=0.9, ncol=2)

    plt.tight_layout()
    path = os.path.join(output_dir, "runtime_comparison.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: {path}")


def plot_solver_comparison(df, output_dir):
    """Figure 3: Dual plot comparing 5 SAT encodings across Glucose3 (left) and CaDiCaL153 (right)."""
    d = _prepare_df(df)
    df_ok = d[d["status"] == "SAT"].copy()
    df_sat = df_ok[df_ok["category"] == "SAT"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    encodings = ["binomial", "binary", "sequential", "commander", "product"]
    markers = {"binomial": "o", "binary": "s", "sequential": "^", "commander": "D", "product": "v"}

    # Subplot 1: Glucose3
    df_gluc = df_sat[df_sat["sat_solver"] == "glucose3"]
    for enc in encodings:
        sub = df_gluc[df_gluc["encoding"] == enc].sort_values("n")
        if not sub.empty:
            ax1.plot(
                sub["n"], sub["solve_time_s"],
                color=ENCODING_COLORS.get(enc, "#333333"),
                marker=markers.get(enc, "o"),
                ls="-",
                linewidth=1.8,
                markersize=6,
                label=enc.capitalize()
            )

    ax1.set_xscale("log", base=2)
    ax1.set_yscale("log")
    ax1.set_xlabel("Board Size N", fontweight="bold")
    ax1.set_ylabel("Solving Time (seconds)", fontweight="bold")
    ax1.set_title("(a) Glucose3 Backend", fontweight="bold", fontsize=11)
    ax1.grid(True, which="both", ls="--", alpha=0.4)
    ax1.legend(loc="lower right", fontsize=8.5, framealpha=0.9)

    # Subplot 2: CaDiCaL 153
    df_cadi = df_sat[df_sat["sat_solver"] == "cadical153"]
    for enc in encodings:
        sub = df_cadi[df_cadi["encoding"] == enc].sort_values("n")
        if not sub.empty:
            ax2.plot(
                sub["n"], sub["solve_time_s"],
                color=ENCODING_COLORS.get(enc, "#333333"),
                marker=markers.get(enc, "o"),
                ls="--",
                linewidth=1.8,
                markersize=6,
                label=enc.capitalize()
            )

    ax2.set_xscale("log", base=2)
    ax2.set_xlabel("Board Size N", fontweight="bold")
    ax2.set_title("(b) CaDiCaL 153 Backend", fontweight="bold", fontsize=11)
    ax2.grid(True, which="both", ls="--", alpha=0.4)
    ax2.legend(loc="lower right", fontsize=8.5, framealpha=0.9)

    plt.tight_layout()
    path = os.path.join(output_dir, "solver_comparison.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: {path}")


def plot_cactus(df, output_dir):
    d = _prepare_df(df)
    df_ok = d[d["status"] == "SAT"].copy()

    fig, ax = plt.subplots(figsize=(10, 5.5))
    
    df_sat = df_ok[df_ok["category"] == "SAT"]
    for solver_name in df_sat["solver"].unique():
        sub = df_sat[df_sat["solver"] == solver_name]
        times = sorted(sub["solve_time_s"].dropna().tolist())
        if not times:
            continue
        enc = sub["encoding"].iloc[0]
        backend = sub["sat_solver"].iloc[0]
        color = ENCODING_COLORS.get(enc, "#333333")
        ls = "-" if backend == "glucose3" else "--"
        marker = "o" if backend == "glucose3" else "s"
        label = f"{enc.capitalize()} ({backend})"
        ax.plot(
            range(1, len(times) + 1), times,
            color=color, ls=ls, marker=marker,
            markersize=5, linewidth=1.5, label=label
        )

    for b_name, style in BASELINE_STYLES.items():
        sub = df_ok[df_ok["solver"] == b_name]
        times = sorted(sub["solve_time_s"].dropna().tolist())
        if times:
            ax.plot(
                range(1, len(times) + 1), times,
                color=style["color"],
                marker=style["marker"],
                ls=style["ls"],
                linewidth=style["lw"],
                markersize=6,
                label=style["label"]
            )

    ax.set_yscale("log")
    ax.set_xlabel("Number of Solved Instances")
    ax.set_ylabel("Time (seconds)")
    ax.set_title("Cactus Plot: Solver Performance & Instance Coverage", fontweight="bold")
    ax.grid(True, which="both", ls="--", alpha=0.4)
    
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0., fontsize=8.5)
    plt.tight_layout()

    path = os.path.join(output_dir, "cactus_plot.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: {path}")


def plot_encoding_overhead(df, output_dir):
    """Figure 5: Build/Encoding Time vs Solve Time analysis across SAT encodings."""
    d = _prepare_df(df)
    if "build_time_s" not in d.columns or d["build_time_s"].isna().all():
        return

    df_sat = d[(d["category"] == "SAT") & (d["status"] == "SAT")].copy()
    if df_sat.empty:
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    encodings = ["binomial", "binary", "sequential", "commander", "product"]
    markers = {"binomial": "o", "binary": "s", "sequential": "^", "commander": "D", "product": "v"}

    # Subplot 1: Build Time vs N
    for enc in encodings:
        sub = df_sat[df_sat["encoding"] == enc].drop_duplicates(subset=["encoding", "n"]).sort_values("n")
        if not sub.empty:
            ax1.plot(
                sub["n"], sub["build_time_s"],
                color=ENCODING_COLORS.get(enc, "#333333"),
                marker=markers.get(enc, "o"),
                ls="-",
                linewidth=1.8,
                markersize=6,
                label=enc.capitalize()
            )

    ax1.set_xscale("log", base=2)
    ax1.set_yscale("log")
    ax1.set_xlabel("Board Size N", fontweight="bold")
    ax1.set_ylabel("Build / Encoding Time (seconds)", fontweight="bold")
    ax1.set_title("(a) CNF Generation Time vs Board Size", fontweight="bold", fontsize=11)
    ax1.grid(True, which="both", ls="--", alpha=0.4)
    ax1.legend(loc="lower right", fontsize=8.5, framealpha=0.9)

    # Subplot 2: Build Time vs Solve Time (Product vs Sequential on Glucose3)
    df_gluc = df_sat[df_sat["sat_solver"] == "glucose3"]
    key_encs = ["product", "sequential", "binary"]
    for enc in key_encs:
        sub = df_gluc[df_gluc["encoding"] == enc].sort_values("n")
        if not sub.empty:
            c = ENCODING_COLORS.get(enc, "#333333")
            ax2.plot(sub["n"], sub["build_time_s"], color=c, ls="--", marker="o", markersize=5,
                     label=f"{enc.capitalize()} (Build Time)")
            ax2.plot(sub["n"], sub["solve_time_s"], color=c, ls="-", marker="s", markersize=5,
                     label=f"{enc.capitalize()} (Solve Time)")

    ax2.set_xscale("log", base=2)
    ax2.set_yscale("log")
    ax2.set_xlabel("Board Size N", fontweight="bold")
    ax2.set_ylabel("Time (seconds)", fontweight="bold")
    ax2.set_title("(b) Build Time (dashed) vs Pure Solve Time (solid)", fontweight="bold", fontsize=11)
    ax2.grid(True, which="both", ls="--", alpha=0.4)
    ax2.legend(loc="lower right", fontsize=7.5, framealpha=0.9, ncol=2)

    plt.tight_layout()
    path = os.path.join(output_dir, "encoding_overhead.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: {path}")


def generate_all(csv_path="results/benchmark_results.csv",
                 output_dir="results/figures"):
    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}")
        return

    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(csv_path)

    print("\nGenerating optimized figures...")
    plot_clauses(df, output_dir)
    plot_runtime(df, output_dir)
    plot_solver_comparison(df, output_dir)
    plot_cactus(df, output_dir)
    plot_encoding_overhead(df, output_dir)
    print("Done.\n")


if __name__ == "__main__":
    generate_all()
