"""
Test codes for auto-playing.
"""
import tqdm
import logging
import matplotlib.pyplot as plt
from game import MineGame, STATUS
from auto import MineBot

BOT = MineBot()
GAME = MineGame()
logging.basicConfig(level=logging.INFO)


def test(shape: tuple, mines: int, total: int) -> float:
    win = 0
    progress_bar = tqdm.tqdm(total=total)
    for i in range(total):
        GAME.start(*shape, mines)
        while GAME.status == STATUS.RUNNING:
            moves = BOT.analyze(GAME)
            for move in moves:
                GAME.move(*move)
                if GAME.status != STATUS.RUNNING:
                    break
        win += GAME.status == STATUS.WIN
        progress_bar.update(1)
    progress_bar.close()
    return win / total


def main():
    win_rates = []
    shape = (40, 40)
    # Test mine dense from 0.05 to 0.25
    mine_denses = [0.025 * (i + 2) for i in range(9)]
    for dense in mine_denses:
        mines = int(dense * shape[0] * shape[1])
        logging.info('Test mine dense: {:.3f}'.format(dense))
        win_rates.append(test(shape, mines, 1000))
        logging.info(
            'Mine dense: {:.3f}, win rate: {:.3f}'.format(dense,
                                                          win_rates[-1]))
    plt.plot(mine_denses, win_rates)
    plt.savefig('test.png')
    plt.show()
    print('Win rates:', win_rates)


def classic_test():
    names = ['Primary', 'Medium', 'Advanced']
    shapes = [(8, 8), (16, 16), (30, 16)]
    mines = [10, 40, 99]
    win_rates = []
    for i in range(3):
        logging.info('Test {}'.format(names[i]))
        win_rates.append(test(shapes[i], mines[i], 1000))
        logging.info(
            'Mine count: {}, win rate: {}'.format(mines[i], win_rates[-1]))


if __name__ == '__main__':
    main()
    classic_test()
