"""Registry of baseline solvers (CP + ILP) for comparison."""
from .cp.cpsat_solver import solve_n_queens_cpsat
from .cp.cplex_cp_solver import solve_n_queens_cplex_cp
from .ilp.gurobi_solver import solve_n_queens_gurobi
from .ilp.cplex_mip_solver import solve_n_queens_cplex_mip

BASELINE_SOLVERS = {
    "cp_sat":    solve_n_queens_cpsat,
    "cplex_cp":  solve_n_queens_cplex_cp,
    "gurobi":    solve_n_queens_gurobi,
    "cplex_mip": solve_n_queens_cplex_mip,
}
