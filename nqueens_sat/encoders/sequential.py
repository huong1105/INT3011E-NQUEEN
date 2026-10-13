"""Sequential Counter AMO encoding for N-Queens.
Based on nQueens-SAT-main/sequential.py — original algorithm preserved.
"""
from pysat.solvers import Glucose3


def generate_variables(n):
    return [[i * n + j + 1 for j in range(n)] for i in range(n)]


def generate_new_variables(n, new_variables_count, length):
    start = n ** 2 + new_variables_count
    return [i for i in range(start + 1, start + length)]


def at_most_one(clauses, variables, n, new_variables_count):
    new_variables = generate_new_variables(n, new_variables_count, len(variables))
    new_variables_count += (len(variables) - 1)
    clauses.append([-variables[0], new_variables[0]])
    for i in range(1, len(variables) - 1):
        clauses.append([-variables[i], new_variables[i]])
        clauses.append([-new_variables[i - 1], new_variables[i]])
        clauses.append([-new_variables[i - 1], -variables[i]])
    clauses.append([-new_variables[len(variables) - 2], -variables[len(variables) - 1]])
    return new_variables_count


def exactly_one(clauses, variables, n, new_variables_count):
    clauses.append(variables)
    return at_most_one(clauses, variables, n, new_variables_count)


def generate_clauses(n, variables):
    clauses = []
    nvc = 0

    # Exactly one queen in each row
    for row in range(n):
        nvc = exactly_one(clauses, variables[row], n, nvc)

    # Exactly one queen in each column
    for col in range(n):
        nvc = exactly_one(clauses, [variables[row][col] for row in range(n)], n, nvc)

    # At most one queen in each diagonal
    for i in range(1, n):
        diagonal = []
        row = i
        col = 0
        while row >= 0 and col < n:
            diagonal.append(variables[row][col])
            row -= 1
            col += 1
        nvc = at_most_one(clauses, diagonal, n, nvc)

    for j in range(1, n - 1):
        diagonal = []
        row = n - 1
        col = j
        while row >= 0 and col < n:
            diagonal.append(variables[row][col])
            row -= 1
            col += 1
        nvc = at_most_one(clauses, diagonal, n, nvc)

    for i in range(n - 1):
        diagonal = []
        row = i
        col = 0
        while row < n and col < n:
            diagonal.append(variables[row][col])
            row += 1
            col += 1
        nvc = at_most_one(clauses, diagonal, n, nvc)

    for j in range(1, n - 1):
        diagonal = []
        row = 0
        col = j
        while row < n and col < n:
            diagonal.append(variables[row][col])
            row += 1
            col += 1
        nvc = at_most_one(clauses, diagonal, n, nvc)

    return clauses


def solve_n_queens(n):
    variables = generate_variables(n)
    clauses = generate_clauses(n, variables)

    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)

    if solver.solve():
        model = solver.get_model()
        return [[int(model[i * n + j] > 0) for j in range(n)] for i in range(n)]
    else:
        return None


def print_solution(solution):
    if solution is None:
        print("No solution found.")
    else:
        for row in solution:
            print(" ".join("Q" if cell else "." for cell in row))


if __name__ == "__main__":
    n = 64
    solution = solve_n_queens(n)
    print_solution(solution)
