"""5 SAT encodings from nQueens-SAT-main"""
import time
from . import binomial, binary, sequential, commander, product
from ..utils import verify_solution

_MODULES = {
    "binomial":   binomial,
    "binary":     binary,
    "sequential": sequential,
    "commander":  commander,
    "product":    product,
}


def solve(encoding_name, n, solver_name="glucose3"):
    mod = _MODULES[encoding_name]
    
    t_build_start = time.perf_counter()
    variables = mod.generate_variables(n)
    clauses = mod.generate_clauses(n, variables)
    num_clauses = len(clauses)
    
    solution = None
    from pysat.solvers import Solver
    with Solver(name=solver_name) as solver:
        solver.append_formula(clauses)
        build_time = time.perf_counter() - t_build_start
        num_vars = solver.nof_vars()
        
        t_solve_start = time.perf_counter()
        is_sat = solver.solve()
        solve_time = time.perf_counter() - t_solve_start
        
        if is_sat:
            model = solver.get_model()
            solution = [[int(model[i * n + j] > 0) for j in range(n)] for i in range(n)]
            
    is_sat = solution is not None

    if is_sat:
        valid, msg = verify_solution(solution, n)
        if not valid:
            raise RuntimeError(f"[{encoding_name}] Invalid solution for N={n}: {msg}")

    return {
        "sat": is_sat,
        "solve_time_s": round(solve_time, 6),
        "build_time_s": round(build_time, 6),
        "solution": solution,
        "encoding": encoding_name,
        "clauses": num_clauses,
        "vars": num_vars,
    }


def build_formula(encoding_name, n, solver_name="glucose3"):
    mod = _MODULES[encoding_name]
    t_build_start = time.perf_counter()
    variables = mod.generate_variables(n)
    clauses = mod.generate_clauses(n, variables)
    num_clauses = len(clauses)
    
    from pysat.solvers import Solver
    with Solver(name=solver_name) as solver:
        solver.append_formula(clauses)
        build_time = time.perf_counter() - t_build_start
        num_vars = solver.nof_vars()
        
    return {
        "clauses": num_clauses,
        "vars": num_vars,
        "build_time_s": round(build_time, 6),
    }


def list_encodings():
    return list(_MODULES.keys())
