import random
from game import MineGame, STATUS, MASK, OPERATION


class MineBot(object):
    """Automatically playing mine sweeping game."""
    rows: int
    cols: int
    board: list

    def see(self, game: MineGame) -> STATUS:
        # See details of game
        self.rows, self.cols = game.rows, game.cols
        self.board = [[game.view(row, col) for col in range(self.cols)] for row
                      in range(self.rows)]
        return game.status

    def analyze(self, game: MineGame) -> list:
        # See cells on board
        self.see(game)
        # Use simple inferring
        moves = self.__naive_infer()
        # Use advanced inferring
        if len(moves) == 0:
            moves = self.__advanced_infer()
        # No cell could be inferred, use random guess
        if len(moves) == 0:
            moves.add(self.__rand_move())
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
                    unknowns, marks = set(), set()
                    for ri in range(max(row - 1, 0),
                                    min(self.rows, row + 2)):
                        for ci in range(max(col - 1, 0),
                                        min(self.cols, col + 2)):
                            if self.board[ri][ci] == MASK.UNKNOWN.value:
                                unknowns.add((ri, ci))
                            elif self.board[ri][ci] == MASK.MARKED.value:
                                marks.add((ri, ci))
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
        # TODO: use union infer / permutation
        pass

    def __rand_move(self) -> tuple:
        # Generate a random uncover move
        row = random.randint(0, self.rows - 1)
        col = random.randint(0, self.cols - 1)
        while self.board[row][col] != MASK.UNKNOWN.value:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
        return OPERATION.UNCOVER, row, col


def main():
    game = MineGame()
    bot = MineBot()
    game.start(10, 10, 10)
    while True:
        game.show()
        # Game is over
        if game.status != STATUS.RUNNING:
            break
        # Game is running
        move = bot.analyze(game)
        game.move(*move)


if __name__ == '__main__':
    main()
