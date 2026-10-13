"""Gurobi MIP solver for N-Queens."""
import time


def solve_n_queens_gurobi(n, time_limit=60):

    try:
        import gurobipy as gp
        from gurobipy import GRB
    except ImportError:
        return {"sat": False, 
                "time_s": 0.0, 
                "solution": None, 
                "solver": "Gurobi", 
                "error": "gurobipy not installed"}

    m = None
    last_err = None
    for attempt in range(3):
        try:
            m = gp.Model(f"NQueens_{n}")
            break
        except Exception as e:
            last_err = e
            time.sleep(1.0)

    if m is None:
        return {"sat": False,
                "time_s": 0.0,
                "solution": None,
                "solver": "Gurobi",
                "error": str(last_err)}

    try:
        m.setParam("OutputFlag", 0)
        m.setParam("TimeLimit", time_limit)

        t_build_start = time.perf_counter()
        x = m.addVars(n, n, vtype=GRB.BINARY, name="x")

        for r in range(n):
            m.addConstr(gp.quicksum(x[r, c] for c in range(n)) == 1)
        for c in range(n):
            m.addConstr(gp.quicksum(x[r, c] for r in range(n)) == 1)
        for d in range(-(n - 2), n - 1):
            diag = [x[r, r - d] for r in range(n) if 0 <= r - d < n]
            if len(diag) > 1:
                m.addConstr(gp.quicksum(diag) <= 1)
        for s in range(1, 2 * n - 2):
            anti = [x[r, s - r] for r in range(n) if 0 <= s - r < n]
            if len(anti) > 1:
                m.addConstr(gp.quicksum(anti) <= 1)
        m.update()
        build_time = time.perf_counter() - t_build_start

        start = time.perf_counter()
        m.optimize()
        elapsed = time.perf_counter() - start

        if m.status == GRB.OPTIMAL:
            solution = []
            for r in range(n):
                row = []
                for c in range(n):
                    val_gurobi = x[r, c].X 
                    val_int = int(val_gurobi > 0.5) 
                    row.append(val_int)
                solution.append(row)
            return {"sat": True, 
                    "time_s": round(elapsed, 6), 
                    "solve_time_s": round(elapsed, 6),
                    "build_time_s": round(build_time, 6),
                    "solution": solution, 
                    "solver": "Gurobi"}
        return {"sat": False, 
                "time_s": round(elapsed, 6), 
                "solve_time_s": round(elapsed, 6),
                "build_time_s": round(build_time, 6),
                "solution": None, 
                "solver": "Gurobi"}
    except Exception as e:
        return {"sat": False, 
                "time_s": 0.0, 
                "solution": None, 
                "solver": "Gurobi", 
                "error": str(e)}
