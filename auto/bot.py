"""
Auto play mine-sweeper game bot.
"""
import random
import logging
from auto.union_find import union_find
from auto.find_solutions import find_solutions
from game import MineGame, STATUS, MASK, OPERATION

# Use logger to display information
logger = logging.getLogger('Bot')


class MineBot(object):
    """Automatically playing mine sweeping game."""
    rows: int
    cols: int
    board: list
    remain: int
    remain_mines: int
    probability_dict: dict
    # Threshold of mixing probabilistic or random algorithm
    threshold: float = 0.5

    def see(self, game: MineGame) -> STATUS:
        # See details of game
        self.remain = game.remain
        self.remain_mines = game.mines - game.marked
        self.rows, self.cols = game.rows, game.cols
        self.board = [[game.view(row, col) for col in range(self.cols)] for row
                      in range(self.rows)]
        return game.status

    def analyze(self, game: MineGame) -> list:
        # Strategy:
        # Naive -> advanced -> probabilistic / random -> (random)
        # See cells on board
        self.see(game)
        # Try naive inference
        moves = self.__naive_infer()
        # Try advanced inference
        if len(moves) == 0:
            self.probability_dict = {}
            moves = self.__advanced_infer()
            # Try probabilistic inference
            if len(moves) == 0:
                bound = self.threshold * self.rows * self.cols
                if self.remain > bound:
                    moves = self.__probabilistic_infer()
                    # Try random inference
                    if len(moves) == 0:
                        moves = self.__random_infer()
                        logger.debug(
                            'Random algorithm: inferred {} moves'.format(
                                len(moves)))
                    else:
                        logger.debug(
                            'Probabilistic algorithm: inferred {} moves'.format(
                                len(moves)))
                else:
                    moves = self.__random_infer()
                    logger.debug(
                        'Random algorithm: inferred {} moves'.format(
                            len(moves)))
            else:
                logger.debug(
                    'Advanced algorithm: inferred {} moves'.format(len(moves)))
        else:
            logger.debug(
                'Naive algorithm: inferred {} moves'.format(len(moves)))
        return list(moves)

    def __naive_infer(self) -> set:
        # Infer cells: naive algorithm
        moves = set()
        # Scan all known cells and infer mines / safe cells
        for row in range(self.rows):
            for col in range(self.cols):
                value = self.board[row][col]
                # Known cell
                if value >= 0:
                    unknowns, marks = [], []
                    for ri in range(max(row - 1, 0),
                                    min(self.rows, row + 2)):
                        for ci in range(max(col - 1, 0),
                                        min(self.cols, col + 2)):
                            if self.board[ri][ci] == MASK.UNKNOWN.value:
                                unknowns.append((ri, ci))
                            elif self.board[ri][ci] == MASK.MARKED.value:
                                marks.append((ri, ci))
                    # Uncover all unknowns
                    if len(marks) == value:
                        moves.update(
                            [(OPERATION.UNCOVER, r, c) for r, c in
                             unknowns])
                    # Mark all unknowns
                    elif len(unknowns) == value - len(marks):
                        moves.update(
                            [(OPERATION.MARK, r, c) for r, c in
                             unknowns])
        return moves

    def __advanced_infer(self) -> set:
        moves = set()
        # Extract relations
        constraint_keys, constraint_values = self.__extract_constraints()
        # Split relations into disjoint groups to reduce search space
        group_keys_list, group_values_list = self.__split_constraints(
            constraint_keys,
            constraint_values)
        group_count = len(group_keys_list)
        # Combine constraints of each group to infer mines
        for i in range(group_count):
            group_keys, group_values = group_keys_list[i], group_values_list[i]
            cells, all_solutions = find_solutions(group_keys, group_values)
            # Use a filter to remove impossible solutions:
            # total mines exceeds remains
            all_solutions = list(
                filter(lambda sol: sum(sol) < self.remain_mines,
                       all_solutions))
            clean_cells, mine_cells = self.__find_common_infer(cells,
                                                               all_solutions)
            moves.update([(OPERATION.UNCOVER, r, c) for r, c in clean_cells])
            moves.update([(OPERATION.MARK, r, c) for r, c in mine_cells])
        return moves

    def __extract_constraints(self) -> tuple:
        # Extract constraints to represent n cells containing m mines:
        # key: set(c1, c2, c3, ..., cn) <-> value: m
        # However set is not hashable in python, so I use two lists
        constraint_keys, constraint_values = [], []
        # Scan all known cells and infer mines / safe cells
        for row in range(self.rows):
            for col in range(self.cols):
                value = self.board[row][col]
                # Known cell
                if value >= 0:
                    unknowns, marks = [], []
                    for ri in range(max(row - 1, 0),
                                    min(self.rows, row + 2)):
                        for ci in range(max(col - 1, 0),
                                        min(self.cols, col + 2)):
                            if self.board[ri][ci] == MASK.UNKNOWN.value:
                                unknowns.append((ri, ci))
                            elif self.board[ri][ci] == MASK.MARKED.value:
                                marks.append((ri, ci))
                    # Add relation for unknown cells
                    if len(unknowns) > 0:
                        constraint_keys.append(set(unknowns))
                        constraint_values.append(value - len(marks))
        return constraint_keys, constraint_values

    @staticmethod
    def __split_constraints(constraint_keys: list,
                            constraint_values: list) -> tuple:
        # Split constraints into disjoint groups
        group_keys_list, group_values_list = [], []
        # Extract connect edges of relations
        # If two constraints are connected,
        # decision on one would influence on the other
        count = len(constraint_keys)
        connect_edges = []
        for i in range(count):
            for j in range(i + 1, count):
                # Have common cells
                if constraint_keys[i] & constraint_keys[j]:
                    connect_edges.append((i, j))
        # Use union find to get connected groups
        # group_indices_list: [[indices of group 0], [indices of group 1], ...]
        group_indices_list = union_find(connect_edges, count)
        # Convert each group of relations into dict
        for indices in group_indices_list:
            group_keys, group_values = [], []
            for index in indices:
                group_keys.append(constraint_keys[index])
                group_values.append(constraint_values[index])
            group_keys_list.append(group_keys)
            group_values_list.append(group_values)
        return group_keys_list, group_values_list

    def __find_common_infer(self, cells: list, all_solutions: list) -> tuple:
        # Analyze clean / mine cells by
        # finding common cells in ALL feasible solutions
        clean_cells, mine_cells = [], []
        # Get the sum of solution
        solution_count = len(all_solutions)
        if solution_count > 0:
            for i in range(len(cells)):
                cell, mine_probability = cells[i], 0
                for solution in all_solutions:
                    mine_probability += solution[i]
                mine_probability /= solution_count
                if mine_probability == 0:
                    clean_cells.append(cells[i])
                elif mine_probability == 1:
                    mine_cells.append(cells[i])
                else:
                    # Record probability of this cell being mine
                    self.probability_dict[cell] = mine_probability
        return clean_cells, mine_cells

    def __probabilistic_infer(self) -> set:
        # Generate random uncover moves based on probability calculated using
        # all solutions inferred in advanced_inferences
        moves = set()
        max_prob, max_cell = 0, None
        for cell, probability in self.probability_dict.items():
            if probability > max_prob:
                max_prob = probability
                max_cell = cell
        if max_cell is not None:
            moves.add((OPERATION.UNCOVER, *max_cell))
        return moves

    def __random_infer(self) -> set:
        # Final inference: generate a random uncover move
        row = random.randint(0, self.rows - 1)
        col = random.randint(0, self.cols - 1)
        while self.board[row][col] != MASK.UNKNOWN.value:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
        return {(OPERATION.UNCOVER, row, col)}
