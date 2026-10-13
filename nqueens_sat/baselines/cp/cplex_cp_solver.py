"""IBM CPLEX CP Optimizer for N-Queens."""
import os
import time
import shutil

_DEFAULT_PATHS = [
    r"C:\Program Files\IBM\ILOG\CPLEX_Studio222\cpoptimizer\bin\x64_win64",
    r"C:\Program Files\IBM\ILOG\CPLEX_Studio222\cplex\bin\x64_win64",
    r"C:\Program Files\IBM\ILOG\CPLEX_Studio_Community222\cpoptimizer\bin\x64_win64",
    r"C:\Program Files\IBM\ILOG\CPLEX_Studio_Community222\cplex\bin\x64_win64",
]
for _p in _DEFAULT_PATHS:
    if os.path.isdir(_p) and _p not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _p + ";" + os.environ.get("PATH", "")


def solve_n_queens_cplex_cp(n, time_limit=60):
    if not shutil.which("cpoptimizer") and not shutil.which("cpoptimizer.exe"):
        return {"sat": False, 
                "time_s": 0.0, 
                "solution": None, 
                "solver": "CPLEX-CP",
                "error": "IBM CPLEX Optimization Studio (cpoptimizer) runtime not installed"}

    try:
        from docplex.cp.model import CpoModel
    except ImportError:
        return {"sat": False,
                "time_s": 0.0,
                "solution": None,
                "solver": "CPLEX-CP",
                "error": "docplex not installed"}

    try:
        t_build_start = time.perf_counter()
        mdl = CpoModel(name=f"NQueens_CP_{n}")
        queens = [mdl.integer_var(0, n - 1, name=f"Q_{i}") for i in range(n)]

        mdl.add(mdl.all_diff(queens))
        mdl.add(mdl.all_diff([queens[i] + i for i in range(n)]))
        mdl.add(mdl.all_diff([queens[i] - i for i in range(n)]))
        build_time = time.perf_counter() - t_build_start

        start = time.perf_counter()
        res = mdl.solve(TimeLimit=time_limit, LogVerbosity="Quiet")
        elapsed = time.perf_counter() - start

        if res and res.is_solution():
            cols = [res.get_value(queens[i]) for i in range(n)]
            solution = [[1 if cols[i] == j else 0 for j in range(n)] for i in range(n)]
            return {"sat": True,
                    "time_s": round(elapsed, 6),
                    "solve_time_s": round(elapsed, 6),
                    "build_time_s": round(build_time, 6),
                    "solution": solution,
                    "solver": "CPLEX-CP"}
        return {"sat": False,
                "time_s": round(elapsed, 6),
                "solve_time_s": round(elapsed, 6),
                "build_time_s": round(build_time, 6),
                "solution": None,
                "solver": "CPLEX-CP"}
    except Exception as e:
        return {"sat": False, 
                "time_s": 0.0, 
                "solution": None, 
                "solver": "CPLEX-CP", 
                "error": str(e)}
