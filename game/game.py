"""
Mine-sweeper game class.
"""
import time
from enum import Enum
from termcolor import colored
from game.map import Map


class STATUS(Enum):
    """Status of game: win, lose, running and stopped."""
    WIN = 1
    LOSE = -1
    RUNNING = 0


class MASK(Enum):
    """Mask of grid: unknown, known and marked."""
    MARKED = -2
    UNKNOWN = -1
    KNOWN = 0


class OPERATION(Enum):
    """Operation of player: uncover and mark."""
    UNCOVER = 1
    MARK = 2


class MineGame(object):
    """Mine sweeper game object."""

    rows, cols, mines, marked, remain, moves = 0, 0, 0, 0, 0, 0
    status = STATUS.WIN
    start_time, __duration = 0., 0.
    __map, __mask = None, None

    def start(self, rows: int, columns: int, mines: int):
        assert columns > 0 and rows > 0 and 0 < mines < rows * columns
        # Initialize game data
        self.rows, self.cols, self.mines = rows, columns, mines
        self.remain = rows * columns
        self.marked, self.moves, self.status = 0, 0, STATUS.RUNNING
        self.start_time, self.__duration = time.time(), 0.
        self.__map = Map(rows, columns, self.mines)
        self.__mask = [[MASK.UNKNOWN for _ in range(columns)] for _ in
                       range(rows)]

    def view(self, row: int, col: int) -> int:
        # See the cell at [row, col]
        assert 0 <= col < self.cols and 0 <= row < self.rows
        if self.__mask[row][col] == MASK.KNOWN:
            value = self.__map[row][col]
        else:
            value = self.__mask[row][col].value
        return value

    def move(self, operation: OPERATION, row: int, col: int):
        assert self.status == STATUS.RUNNING
        assert 0 <= col < self.cols and 0 <= row < self.rows
        self.moves += 1
        # Operations: uncover and mark / unmark
        do = {OPERATION.UNCOVER: self.__uncover,
              OPERATION.MARK: self.__mark}[operation]
        # Perform operation
        if self.__mask[row][col] != MASK.KNOWN:
            value = do(row, col)
        else:
            value = self.__map[row][col]
        if self.status != STATUS.RUNNING:
            self.__end_game()
        return value

    def __uncover(self, row: int, col: int) -> int:
        # Uncover grid
        direct = [[1, 0], [-1, 0], [0, 1], [0, -1],
                  [-1, -1], [1, 1], [-1, 1], [1, -1]]
        value = self.__map.uncover(row, col)
        if self.__mask[row][col] == MASK.UNKNOWN:  # New grid
            self.__mask[row][col] = MASK.KNOWN
            self.remain -= 1
            if value == -1:
                self.status = STATUS.LOSE
            elif self.remain == self.mines:
                self.status = STATUS.WIN
            elif value == 0:
                # Recursively uncover neighborhood grids
                for dr, dc in direct:
                    new_r = row + dr
                    new_c = col + dc
                    if 0 <= new_c < self.cols:
                        if 0 <= new_r < self.rows:
                            if self.__mask[new_r][new_c] == MASK.UNKNOWN:
                                self.__uncover(new_r, new_c)
        return value

    def __mark(self, row: int, col: int) -> int:
        # Mark grid
        if self.__mask[row][col] == MASK.UNKNOWN:
            self.__mask[row][col] = MASK.MARKED
            self.marked += 1
        elif self.__mask[row][col] == MASK.MARKED:  # Unmark
            self.__mask[row][col] = MASK.UNKNOWN
            self.marked -= 1
        return 0

    def __end_game(self):
        # Show prompt
        if self.status == STATUS.LOSE:
            # Uncover all grids
            for row in range(self.rows):
                for col in range(self.cols):
                    self.__mask[row][col] = MASK.KNOWN
        # Freeze time if game is over
        self.__duration = time.time() - self.start_time

    @property
    def duration(self) -> float:
        if self.status == STATUS.RUNNING:
            return time.time() - self.start_time
        else:
            return self.__duration

    def show(self):
        signs = {MASK.UNKNOWN: '█',
                 MASK.MARKED: colored('ⓜ', 'yellow')}
        if self.__map is None:
            print(colored(' * * * No game to show, please start game:( * * *',
                          'red'))
            return
        elif self.status == STATUS.RUNNING:
            print(' * * * Game is running... * * *')
        elif self.status == STATUS.WIN:
            print(colored(' * * * Congratulations! You win:) * * *', 'yellow'))
        else:
            print(colored(' * * * Oops, you lose:( * * *', 'red'))
        print(colored('    ♣ Time: {:.2f}s\n'
                      '    ♣ Mines: {}\n'
                      '    ♣ Remain: {}\n'
                      '    ♣ Marked: {}\n'
                      '    ♣ Moves: {}'.format(self.duration,
                                               self.mines,
                                               self.remain,
                                               self.marked,
                                               self.moves),
                      'yellow'))
        # Show grid line
        index_row = '    '
        for col in range(self.cols):
            index_row += str(col % 10) + ' '
        sep_row = '  ╔' + '═' * (len(index_row) - 3) + '╗'
        print(index_row + '\n' + sep_row, end='')
        print('\n', end='')
        for row in range(self.rows):
            print('{:2d}║ '.format(row), end='')
            for col in range(self.cols):
                state = self.__mask[row][col]
                value = self.__map[row][col]
                if state in signs:
                    c = signs[state]
                elif value == -1:
                    c = colored('*', 'red')
                elif value == 0:
                    c = ' '
                else:
                    c = str(value)
                print(c, end=' ')
            print('║\n', end='')
        sep_row = '  ╚' + '═' * (len(index_row) - 3) + '╝'
        print(sep_row)
