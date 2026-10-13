"""Benchmark engine — runs all solvers and collects results.
Supports both SAT encodings and baseline solvers (CP, ILP).
"""
import os
import statistics
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FuturesTimeout

from .encoders import solve as sat_solve, list_encodings
from .baselines import BASELINE_SOLVERS
from .utils import verify_solution

def _run_sat(encoding_name, n, sat_solver="glucose3"):
    result = sat_solve(encoding_name, n, solver_name=sat_solver)
    return {
        "n": n,
        "category": "SAT",
        "encoding": encoding_name,
        "sat_solver": sat_solver,
        "solver": f"{encoding_name}-{sat_solver}",
        "time_s": result["time_s"],
        "solve_time_s": result.get("solve_time_s", result["time_s"]),
        "build_time_s": result.get("build_time_s", 0.0),
        "status": "SAT" if result["sat"] else "UNSAT",
        "clauses": result.get("clauses", ""),
        "vars": result.get("vars", ""),
        "runs": 1,
        "error": "",
    }


BASELINE_DISPLAY_NAMES = {
    "cp_sat": "CP-SAT",
    "cplex_cp": "CPLEX-CP",
    "gurobi": "Gurobi",
    "cplex_mip": "CPLEX-MIP",
}


def _matches_solver(saved_name, target_name):
    def norm(s):
        return str(s).strip().lower().replace("-", "").replace("_", "")
    return norm(saved_name) == norm(target_name)


def _run_baseline(solver_name, n, time_limit):
    solver_func = BASELINE_SOLVERS[solver_name]
    result = solver_func(n, time_limit=time_limit)

    status = "SAT" if result.get("sat") else "FAIL"
    if result.get("error"):
        status = "ERROR"
    elif status == "FAIL" and result.get("time_s", 0) >= time_limit * 0.95:
        status = "TIMEOUT"

    if result.get("sat") and result.get("solution"):
        valid, msg = verify_solution(result["solution"], n)
        if not valid:
            status = "INVALID"

    canonical_name = BASELINE_DISPLAY_NAMES.get(solver_name, result.get("solver", solver_name))
    return {
        "n": n,
        "category": "ILP" if "mip" in solver_name.lower() or "gurobi" in solver_name.lower() else "CP",
        "encoding": "",
        "sat_solver": "",
        "solver": result.get("solver", canonical_name),
        "time_s": result.get("time_s", 0.0),
        "solve_time_s": result.get("solve_time_s", result.get("time_s", 0.0)),
        "build_time_s": result.get("build_time_s", 0.0),
        "status": status,
        "clauses": "",
        "vars": "",
        "runs": 1,
        "error": result.get("error", ""),
    }


def _run_with_timeout(runner_func, args, timeout):
    pool = ProcessPoolExecutor(max_workers=1)
    future = pool.submit(runner_func, *args)
    try:
        rec = future.result(timeout=timeout)
        pool.shutdown(wait=False)
        return rec
    except FuturesTimeout:
        for p in pool._processes.values():
            try:
                p.terminate()
            except Exception:
                pass
        pool.shutdown(wait=False, cancel_futures=True)
        return "TIMEOUT"
    except Exception as e:
        for p in pool._processes.values():
            try:
                p.terminate()
            except Exception:
                pass
        pool.shutdown(wait=False, cancel_futures=True)
        return e


def _run_repeated(runner_func, args, timeout, runs=3):
    collected = []
    for r_idx in range(runs):
        res = _run_with_timeout(runner_func, args, timeout)
        if res == "TIMEOUT":
            collected.append("TIMEOUT")
            break
        elif isinstance(res, Exception):
            collected.append(res)
            break
        else:
            collected.append(res)

    if all(r == "TIMEOUT" for r in collected):
        return "TIMEOUT"

    errs = [r for r in collected if isinstance(r, Exception)]
    if errs and len(errs) == len(collected):
        return errs[0]

    sat_runs = [r for r in collected if isinstance(r, dict) and r.get("status") == "SAT"]
    if not sat_runs:
        valid_runs = [r for r in collected if isinstance(r, dict)]
        return valid_runs[0] if valid_runs else collected[0]

    solve_times = [r["solve_time_s"] for r in sat_runs]
    build_times = [r["build_time_s"] for r in sat_runs]

    final_rec = sat_runs[0].copy()
    final_rec["solve_time_s"] = round(statistics.median(solve_times), 6)
    final_rec["time_s"] = final_rec["solve_time_s"]
    final_rec["build_time_s"] = round(statistics.median(build_times), 6)
    final_rec["runs"] = len(sat_runs)
    return final_rec


def run(sizes, timeout=60, output_csv="results/benchmark_results.csv",
        skip_binomial_above=64, sat_solver="glucose3", runs=3, force=False):
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    if os.path.exists(output_csv):
        try:
            df_old = pd.read_csv(output_csv)
            df_old = df_old.drop_duplicates(subset=["solver", "n"], keep="last")
            records = df_old.to_dict('records')
            records = [r for r in records if not ("[" in str(r.get("sat_solver", "")) or str(r.get("status")) == "ERROR")]
            print(f"[*] Found existing data at {output_csv} ({len(records)} valid records).")
        except Exception:
            records = []
    else:
        records = []

    sat_solvers = [sat_solver] if isinstance(sat_solver, str) else list(sat_solver)
    print(f"Starting benchmark: Sizes={sizes}, Timeout={timeout}s, SAT Solvers={sat_solvers}, Runs={runs}, Force={force}")

    for n in sizes:
        # SAT Encodings for each backend solver
        for s_backend in sat_solvers:
            for enc_name in list_encodings():
                if enc_name == "binomial" and n > skip_binomial_above:
                    continue

                solver_full_name = f"{enc_name}-{s_backend}"
                if not force and any(r.get("n") == n and r.get("solver") == solver_full_name and r.get("status") != "ERROR" for r in records):
                    print(f"  [SAT] {solver_full_name:20s}  (Skipping, already computed for N={n})")
                    continue

                records = [r for r in records if not (r.get("n") == n and r.get("solver") == solver_full_name)]

                res = _run_repeated(_run_sat, (enc_name, n, s_backend), timeout, runs=runs)
                if res == "TIMEOUT":
                    records.append({
                        "n": n,
                        "category": "SAT",
                        "encoding": enc_name,
                        "sat_solver": s_backend,
                        "solver": solver_full_name,
                        "time_s": timeout,
                        "solve_time_s": timeout,
                        "build_time_s": 0.0,
                        "status": "TIMEOUT",
                        "clauses": "",
                        "vars": "",
                        "runs": 1,
                        "error": "",
                    })
                elif isinstance(res, Exception):
                    records.append({
                        "n": n,
                        "category": "SAT",
                        "encoding": enc_name,
                        "sat_solver": s_backend,
                        "solver": solver_full_name,
                        "time_s": 0.0,
                        "solve_time_s": 0.0,
                        "build_time_s": 0.0,
                        "status": "ERROR",
                        "clauses": "",
                        "vars": "",
                        "runs": 1,
                        "error": str(res),
                    })
                else:
                    records.append(res)

        # Baseline Solvers
        for solver_name in BASELINE_SOLVERS:
            cat = "CP" if "cp" in solver_name.lower() else "ILP"
            display_name = BASELINE_DISPLAY_NAMES.get(solver_name, solver_name)
            
            if not force and any(r.get("n") == n and _matches_solver(r.get("solver"), solver_name) and r.get("status") != "ERROR" for r in records):
                print(f"  [{cat:3s}] {display_name:20s}  (Skipping, already computed for N={n})")
                continue

            records = [r for r in records if not (r.get("n") == n and _matches_solver(r.get("solver"), solver_name))]

            res = _run_repeated(_run_baseline, (solver_name, n, timeout), timeout + 5, runs=runs)
            if res == "TIMEOUT":
                records.append({
                    "n": n,
                    "category": cat,
                    "encoding": "",
                    "sat_solver": "",
                    "solver": display_name,
                    "time_s": timeout,
                    "solve_time_s": timeout,
                    "build_time_s": 0.0,
                    "status": "TIMEOUT",
                    "clauses": "",
                    "vars": "",
                    "runs": 1,
                    "error": "",
                })
            elif isinstance(res, Exception):
                records.append({
                    "n": n,
                    "category": cat,
                    "encoding": "",
                    "sat_solver": "",
                    "solver": display_name,
                    "time_s": 0.0,
                    "solve_time_s": 0.0,
                    "build_time_s": 0.0,
                    "status": "ERROR",
                    "clauses": "",
                    "vars": "",
                    "runs": 1,
                    "error": str(res),
                })
            else:
                records.append(res)

        cols = ["n", "category", "encoding", "sat_solver", "solver", "time_s", "solve_time_s", "build_time_s", "status", "clauses", "vars", "runs", "error"]
        df = pd.DataFrame(records).reindex(columns=cols)
        saved = False
        for _ in range(3):
            try:
                df.to_csv(output_csv, index=False)
                saved = True
                print(f"N = {n}: Finished successfully, updated {output_csv}")
                break
            except PermissionError:
                import time
                time.sleep(0.5)

        if not saved:
            fallback = output_csv.replace(".csv", "_backup.csv")
            try:
                df.to_csv(fallback, index=False)
                print(f"\n[!] WARNING: '{output_csv}' is currently locked by another program (e.g. Microsoft Excel)!")
                print(f"[!] Please close Excel. Data has been saved to fallback file: {fallback}\n")
            except Exception as e:
                print(f"[!] Could not save data: {e}")

    print(f"Benchmark finished! Results saved to {output_csv}")
    return pd.DataFrame(records)
