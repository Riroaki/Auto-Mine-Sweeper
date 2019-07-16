import time
from enum import Enum
from termcolor import colored
from map import Map

HEADING = colored("""
     ___  ___   _   __   _   _____        _____   _          __  _____   _____   _____   _____   _____   
    /   |/   | | | |  \ | | | ____|      /  ___/ | |        / / | ____| | ____| |  _  \ | ____| |  _  \  
   / /|   /| | | | |   \| | | |__        | |___  | |  __   / /  | |__   | |__   | |_| | | |__   | |_| |  
  / / |__/ | | | | | |\   | |  __|       \___  \ | | /  | / /   |  __|  |  __|  |  ___/ |  __|  |  _  /  
 / /       | | | | | | \  | | |___        ___| | | |/   |/ /    | |___  | |___  | |     | |___  | | \ \  
/_/        |_| |_| |_|  \_| |_____|      /_____/ |___/|___/     |_____| |_____| |_|     |_____| |_|  \_\ 
""", 'yellow')


class GAMESTATE(Enum):
    """State of game: win, lose, running and stopped."""
    WIN = 1
    LOSE = -2
    RUNNING = 0
    STOPPED = -1


class GRIDSTATE(Enum):
    """State of grid: unknown, known and marked."""
    UNKNOWN = 0
    KNOWN = 1
    MARKED = 2


class OPERATION(Enum):
    """Operation of player: uncover and mark."""
    UNCOVER = 1
    MARK = 2


class MineGame(object):
    """Mine sweeper game object."""

    def __init__(self):
        # Game map and board
        self.__map = None
        self.__board = None
        # Mines
        self.__total = -1
        self.__remain = -1
        self.__marked = -1
        self.__moves = -1
        # Board shape
        self.__rows = 0
        self.__cols = 0
        # Game status
        self.__state = GAMESTATE.STOPPED
        self.__duration = 0.
        self.__start_time = 0.

    def start(self, rows: int, columns: int, mine_rate: float = 0.2):
        assert columns > 0 and rows > 0 and 0. < mine_rate < 1.
        self.__rows = rows
        self.__cols = columns
        self.__remain = rows * columns
        self.__total = int(rows * columns * mine_rate)
        self.__marked = 0
        self.__moves = 0
        self.__map = Map(rows, columns, self.__total)
        # Use digit 9 as cover mark
        self.__board = [[GRIDSTATE.UNKNOWN for _ in range(columns)] for _ in
                        range(rows)]
        self.__state = GAMESTATE.RUNNING
        self.__start_time = time.time()
        self.__duration = 0.

    def show(self):
        signs = {GRIDSTATE.UNKNOWN: '█',
                 GRIDSTATE.MARKED: colored('ⓜ', 'yellow')}
        print(colored('    ♣ Time: {:.2f}s\n'
                      '    ♣ Total mines:{}\n'
                      '    ♣ Remain grids:{}\n'
                      '    ♣ Marked grids:{}\n'
                      '    ♣ Total moves: {}'.format(self.duration,
                                                     self.total_mines,
                                                     self.remain,
                                                     self.marked,
                                                     self.total_moves),
                      'yellow'))
        # Show grid line
        index_row = '    '
        for col in range(self.__cols):
            index_row += str(col % 10) + ' '
        sep_row = '  ╔' + '═' * (len(index_row) - 3) + '╗'
        print(index_row + '\n' + sep_row, end='')
        print('\n', end='')
        for row in range(self.__rows):
            print('{:2d}║ '.format(row), end='')
            for col in range(self.__cols):
                state = self.__board[row][col]
                value = self.__map.data[row][col]
                if state in signs:
                    c = signs[state]
                elif value == -1:
                    c = colored('*', 'red')
                else:
                    c = str(value)
                print(c, end=' ')
            print('║\n', end='')
        sep_row = '  ╚' + '═' * (len(index_row) - 3) + '╝'
        print(sep_row)

    def move(self, operation: OPERATION, row: int, col: int):
        assert self.__state == GAMESTATE.RUNNING
        assert 0 <= col < self.__cols and 0 <= row < self.__rows
        self.__moves += 1
        if operation == OPERATION.UNCOVER:
            # Uncover grids
            value = self.__uncover(row, col)
            if self.__state != GAMESTATE.RUNNING:
                self.__end_game()
        else:  # Mark grids
            value = self.__mark(row, col)
        return value

    def __uncover(self, row: int, col: int) -> int:
        # Uncover grid
        direct = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        value = self.__map.uncover(row, col)
        if self.__board[row][col] == GRIDSTATE.UNKNOWN:  # New grid
            self.__board[row][col] = GRIDSTATE.KNOWN
            self.__remain -= 1
            if value == -1:
                self.__state = GAMESTATE.LOSE
            elif self.__remain == self.__total:
                self.__state = GAMESTATE.WIN
            elif value == 0:
                # Recursively uncover neighborhood grids
                for i in range(4):
                    new_r = row + direct[i][0]
                    new_c = col + direct[i][1]
                    if 0 <= new_c < self.__cols and 0 <= new_r < self.__rows:
                        if self.__map.data[new_r][new_c] != -1:
                            self.__uncover(new_r, new_c)
        return value

    def __mark(self, row: int, col: int) -> int:
        # Mark grid
        if self.__board[row][col] == GRIDSTATE.UNKNOWN:
            self.__board[row][col] = GRIDSTATE.MARKED
            self.__marked += 1
        elif self.__board[row][col] == GRIDSTATE.MARKED:  # Unmark
            self.__board[row][col] = GRIDSTATE.UNKNOWN
            self.__marked -= 1
        return 0

    def __end_game(self):
        # Show prompt
        if self.__state == GAMESTATE.WIN:
            print(colored(' * * * Congratulations! You win:) * * *', 'yellow'))
        else:
            print(colored(' * * * Oops, you lose:( * * *', 'red'))
            # Uncover all grids
            for row in range(self.__rows):
                for col in range(self.__cols):
                    self.__board[row][col] = GRIDSTATE.KNOWN
        # Freeze time if game is over
        self.__state = GAMESTATE.STOPPED
        self.__duration = time.time() - self.__start_time
        self.show()

    @property
    def state(self) -> GAMESTATE:
        return self.__state

    @property
    def remain(self) -> int:
        return self.__remain - self.__marked

    @property
    def total_mines(self) -> int:
        return self.__total

    @property
    def marked(self) -> int:
        return self.__marked

    @property
    def total_moves(self) -> int:
        return self.__moves

    @property
    def duration(self) -> float:
        if self.__state == GAMESTATE.RUNNING:
            dur = time.time() - self.__start_time
        else:
            dur = self.__duration
        return dur


def main():
    # Start game
    print(HEADING)
    game = MineGame()
    while True:
        try:
            params = input('Starting a new game...\n'
                           'Input rows, columns and mine rate:\n'
                           'e.g., `20 30 0.2`\n'
                           'Press `ctrl + c` to quit.\n> ').split()
            params = int(params[0]), int(params[1]), float(params[2])
            game.start(*params)
            # Continuously interact
            while True:
                try:
                    game.show()
                    move = input(
                        'Input row and column position to uncover or mark:\n'
                        'e.g., `1 3 5` as to uncover grid[3][5];\n'
                        '`2 4 6` as to mark grid[4][6])\n'
                        'Press `ctrl + c` to quit.\n> ').split()
                    move = OPERATION(int(move[0])), int(move[1]), int(move[2])
                    game.move(*move)
                    if game.state != GAMESTATE.RUNNING:
                        break
                except (IndexError, ValueError, AssertionError):
                    print('Illegal move. Input again.')
                except KeyboardInterrupt:
                    print('Quit this game...')
                    break
        except AssertionError:
            print('Illegal paramaters. Input again.')
        except KeyboardInterrupt:
            print('Have a nice day:)')
            break


if __name__ == '__main__':
    main()
