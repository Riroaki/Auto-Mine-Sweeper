import random


class Map(object):
    """Map of mine sweeper game."""

    def __init__(self, rows: int, columns: int, total: int):
        self.__cols = columns
        self.__rows = rows
        self.__total = total
        self.__data = [[0 for _ in range(columns)] for _ in range(rows)]
        self.__flag = True

    def uncover(self, row: int, col: int) -> int:
        if self.__flag:
            self.__init_map(col, row)
            self.__flag = False
        return self.__data[row][col]

    def __init_map(self, row: int, col: int):
        # Initialize mines at first attempt to avoid collision
        for i in range(self.__total):
            pos_x = random.randint(0, self.__cols - 1)
            pos_y = random.randint(0, self.__rows - 1)
            while (pos_x == col and pos_y == row) \
                    or self.__data[pos_y][pos_x] != 0:
                pos_x = random.randint(0, self.__cols - 1)
                pos_y = random.randint(0, self.__rows - 1)
            self.__data[pos_y][pos_x] = -1
        # Initialize grids around mines
        for row in range(self.__rows):
            for col in range(self.__cols):
                if self.__data[row][col] == 0:
                    for ri in range(max(0, row - 1),
                                    min(self.__rows, row + 2)):
                        for ci in range(max(0, col - 1),
                                        min(self.__cols, col + 2)):
                            if self.__data[ri][ci] == -1:
                                self.__data[row][col] += 1

    @property
    def data(self) -> list:
        return self.__data


if __name__ == '__main__':
    m = Map(10, 5, 15)
