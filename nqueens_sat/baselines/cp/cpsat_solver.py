"""Google OR-Tools CP-SAT solver for N-Queens."""
import time
from ortools.sat.python import cp_model


def solve_n_queens_cpsat(n, time_limit=60):
    t_build_start = time.perf_counter()
    model = cp_model.CpModel()
    queens = [model.NewIntVar(0, n - 1, f"Q_{i}") for i in range(n)]

    model.AddAllDifferent(queens)
    model.AddAllDifferent([queens[i] + i for i in range(n)])
    model.AddAllDifferent([queens[i] - i for i in range(n)])
    build_time = time.perf_counter() - t_build_start

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit)

    start = time.perf_counter()
    status = solver.Solve(model)
    elapsed = time.perf_counter() - start

    is_sat = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    solution = None
    if is_sat:
        solution = [[1 if solver.Value(queens[i]) == j else 0 for j in range(n)] for i in range(n)]

    return {"sat": is_sat,
            "solve_time_s": round(elapsed, 6),
            "build_time_s": round(build_time, 6),
            "solution": solution,
            "solver": "CP-SAT"}
