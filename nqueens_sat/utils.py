"""Utility functions: solution verification and board display."""
def verify_solution(solution, n):
    if solution is None:
        return False, "Solution is None"

    queens = []
    for r in range(n):
        for c in range(n):
            if solution[r][c]:
                queens.append((r, c))

    if len(queens) != n:
        return False, f"Expected {n} queens, found {len(queens)}"

    rows, cols, diag1, diag2 = set(), set(), set(), set()
    for r, c in queens:
        if r in rows:
            return False, f"Row {r} conflict"
        rows.add(r)
        if c in cols:
            return False, f"Column {c} conflict"
        cols.add(c)
        if (r - c) in diag1:
            return False, f"Main diagonal (r-c={r - c}) conflict"
        diag1.add(r - c)
        if (r + c) in diag2:
            return False, f"Anti-diagonal (r+c={r + c}) conflict"
        diag2.add(r + c)

    return True, "Valid"


def print_board(solution, n):
    """Pretty-print a chessboard solution."""
    if solution is None:
        print("No solution found.")
        return
    print(f"\n{'─' * (2 * n - 1)}")
    for row in solution:
        print(" ".join("♛" if cell else "·" for cell in row))
    print(f"{'─' * (2 * n - 1)}\n")
