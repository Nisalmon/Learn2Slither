import pygame as pg
import random


class Snake:
    def __init__(self):
        self.head: tuple[int, int] = ()
        self.body: list[tuple[int, int]] = []


def setup():
    pg.init()
    screen = pg.display.set_mode()
    clock = pg.time.Clock()
    running = True
    return screen, clock, running


def stop_loop(running):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    return running


def loop(screen, clock, running):
    while running:
        running = stop_loop(running)
        screen.fill("gray")
        pg.display.flip()
        clock.tick(60)
    pg.quit()


def init_board():
    board = [['0' for _ in range(10)] for _ in range(10)]
    return board


def setup_board(board):
    green_apples = [
        (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1)),
        (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
    ]
    red_apple = (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
    for apple in green_apples:
        board[apple[1]][apple[0]] = "G"
    board[red_apple[1]][red_apple[0]] = "R"
    return board


def main():
    # screen, clock, running = setup()
    board = init_board()
    board = setup_board(board)
    for row in board:
        print(row)
    # loop(screen, clock, running)


if __name__ == "__main__":
    main()
