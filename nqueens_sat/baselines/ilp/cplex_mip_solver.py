"""IBM CPLEX MIP solver for N-Queens."""
import time
import shutil


def solve_n_queens_cplex_mip(n, time_limit=60):
    try:
        import cplex
    except ImportError:
        if not shutil.which("cplex") and not shutil.which("cplex.exe"):
            return {"sat": False,
                    "time_s": 0.0,
                    "solution": None,
                    "solver": "CPLEX-MIP",
                    "error": "cplex not installed"}

    try:
        from docplex.mp.model import Model
    except ImportError:
        return {"sat": False,
                "time_s": 0.0, 
                "solution": None,
                "solver": "CPLEX-MIP",
                "error": "docplex not installed"}

    try:
        mdl = Model(name=f"NQueens_MIP_{n}")
        mdl.set_time_limit(time_limit)
        mdl.context.solver.log_output = False

        t_build_start = time.perf_counter()
        x = {(r, c): mdl.binary_var(name=f"x_{r}_{c}") for r in range(n) for c in range(n)}

        for r in range(n):
            mdl.add_constraint(mdl.sum(x[r, c] for c in range(n)) == 1)
        for c in range(n):
            mdl.add_constraint(mdl.sum(x[r, c] for r in range(n)) == 1)
        for d in range(-(n - 2), n - 1):
            diag = [x[r, r - d] for r in range(n) if 0 <= r - d < n]
            if len(diag) > 1:
                mdl.add_constraint(mdl.sum(diag) <= 1)
        for s in range(1, 2 * n - 2):
            anti = [x[r, s - r] for r in range(n) if 0 <= s - r < n]
            if len(anti) > 1:
                mdl.add_constraint(mdl.sum(anti) <= 1)
        build_time = time.perf_counter() - t_build_start

        start = time.perf_counter()
        sol = mdl.solve()
        elapsed = time.perf_counter() - start

        if sol is not None:
            solution = [[int(sol.get_value(x[r, c]) > 0.5) for c in range(n)] for r in range(n)]
            return {"sat": True, 
                    "time_s": round(elapsed, 6),
                    "solve_time_s": round(elapsed, 6),
                    "build_time_s": round(build_time, 6),
                    "solution": solution, 
                    "solver": "CPLEX-MIP"}
        return {"sat": False, 
                "time_s": round(elapsed, 6),
                "solve_time_s": round(elapsed, 6),
                "build_time_s": round(build_time, 6),
                "solution": None, 
                "solver": "CPLEX-MIP"}
    except Exception as e:
        return {"sat": False, 
                "time_s": 0.0, 
                "solution": None, 
                "solver": "CPLEX-MIP", "error": str(e)}
