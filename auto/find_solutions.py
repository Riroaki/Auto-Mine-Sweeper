"""
Find all feasible solutions for a group of constraints using backtracking.
Set threshold of a locality to avoid too much computation...
"""

# If number of cells exceeds it, we give up trying to find a solution...
MAX_CELLS = 48


def find_solutions(constraint_keys: list, constraint_values: list) -> tuple:
    # Find all feasible solutions
    all_solutions = []
    # Extract all cells' positions
    cells = set()
    for cell_set in constraint_keys:
        cells.update(cell_set)
    cells = list(cells)
    count = len(cells)
    is_mine = [False for _ in range(count)]
    if count <= MAX_CELLS:
        # Use backtracking to discover all feasible solutions
        backtracking(all_solutions, constraint_keys, constraint_values, 0,
                     cells, is_mine)
    return cells, all_solutions


def backtracking(all_solutions: list, constraint_keys: list,
                 constraint_values: list, curr_index: int, cell_list: list,
                 is_mine: list) -> None:
    def feasible(exact: bool = False) -> bool:
        # Check whether current decision stays consistent with constraints
        violate = False
        # Check each constraint
        for i in range(len(constraint_keys)):
            cell_set, total_mines = constraint_keys[i], constraint_values[i]
            mine_count, cell_count = 0, 0
            # mine_count: number of mines in cells already decided
            # cell_count: number of cells already decided
            for j in range(curr_index + 1):
                if cell_list[j] in cell_set:
                    mine_count += is_mine[j]
                    cell_count += 1
            if not exact:
                # Check whether violates constraint
                # If current number of mines is too large
                if mine_count > total_mines:
                    violate = True
                # If current number of mines is too small
                elif mine_count < total_mines - (len(cell_set) - cell_count):
                    violate = True
            elif mine_count != total_mines:  # Exact satisfy all constraints
                violate = True
            if violate:
                break
        return not violate

    # A feasible solution is generated
    if curr_index == len(cell_list):
        all_solutions.append(is_mine.copy())
    else:
        # Requires exactly match for last cell
        exact_match = curr_index == len(cell_list) - 1
        # Search 2 possibilities: current cell is mine or not?
        is_mine[curr_index] = True
        if feasible(exact_match):
            backtracking(all_solutions, constraint_keys, constraint_values,
                         curr_index + 1,
                         cell_list, is_mine)
        is_mine[curr_index] = False
        if feasible(exact_match):
            backtracking(all_solutions, constraint_keys, constraint_values,
                         curr_index + 1,
                         cell_list, is_mine)


def test():
    # Test codes
    keys = [{(1, 2), (2, 3), (3, 4)}, {(1, 2), (2, 3)}]
    values = [2, 1]
    items, solutions = find_solutions(keys, values)
    print(items)
    for solution in solutions:
        print(solution)


if __name__ == '__main__':
    test()
