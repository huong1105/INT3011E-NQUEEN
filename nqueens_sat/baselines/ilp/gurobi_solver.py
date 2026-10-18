"""Gurobi MIP solver for N-Queens."""
import time


def solve_n_queens_gurobi(n, time_limit=60):

    try:
        import gurobipy as gp
        from gurobipy import GRB
    except ImportError:
        return {"sat": False, 
                "solve_time_s": 0.0, 
                "build_time_s": 0.0,
                "solution": None, 
                "solver": "Gurobi", 
                "error": "gurobipy not installed"}

    max_attempts = 5
    last_err = None

    for attempt in range(max_attempts):
        env = None
        m = None
        try:
            env = gp.Env(params={"OutputFlag": 0})
            m = gp.Model(f"NQueens_{n}", env=env)
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
                return {
                    "sat": True,
                    "solve_time_s": round(elapsed, 6),
                    "build_time_s": round(build_time, 6),
                    "solution": solution,
                    "solver": "Gurobi",
                }
            return {
                "sat": False,
                "solve_time_s": round(elapsed, 6),
                "build_time_s": round(build_time, 6),
                "solution": None,
                "solver": "Gurobi",
            }

        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            if any(k in err_str for k in ["license", "wls", "token", "connect", "10009", "10010"]):
                time.sleep(2.0 * (attempt + 1))
            else:
                break
        finally:
            if m is not None:
                try:
                    m.dispose()
                except Exception:
                    pass
            if env is not None:
                try:
                    env.dispose()
                except Exception:
                    pass
            try:
                gp.disposeDefaultEnv()
            except Exception:
                pass

    return {
        "sat": False,
        "solve_time_s": 0.0,
        "build_time_s": 0.0,
        "solution": None,
        "solver": "Gurobi",
        "error": str(last_err),
    }
