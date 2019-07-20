import tqdm
import logging
import matplotlib.pyplot as plt
from game import MineGame, STATUS
from auto import MineBot

BOT = MineBot()
GAME = MineGame()
SHAPE = (40, 40)
logging.basicConfig(level=logging.INFO)


def test(mine_rate: float, total: int) -> float:
    win = 0
    progress_bar = tqdm.tqdm(total=total)
    for i in range(total):
        GAME.start(*SHAPE, int(SHAPE[0] * SHAPE[1] * mine_rate))
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
    # Test mine rate from 0.05 to 0.95
    mine_rates = [0.025 * (i + 2) for i in range(37)]
    for rate in mine_rates:
        logging.info('Test mine rate: {}'.format(rate))
        win_rates.append(test(rate, 1000))
        logging.info('Mine rate: {}, win rate: {}'.format(rate, win_rates[-1]))
    plt.plot(mine_rates, win_rates)
    plt.show()
    print('Win rates:', win_rates)


if __name__ == '__main__':
    main()
