import pygame as pg
import random


class Snake:
    def __init__(self):
        self.head: tuple[int, int] = ()
        self.body: list[tuple[int, int]] = []

    def _set_body(self, board):
        segments = 2
        x, y = self.head
        while len(self.body) < segments:
            if x > 0 and board[y][x - 1] == "0" and (x - 1, y) not in self.body:
                self.body.append((x-1, y))
                x, y = x - 1, y
            elif y > 0 and board[y - 1][x] == "0" and (x, y - 1) not in self.body:
                self.body.append((x, y - 1))
                x, y = x, y - 1
            elif x < len(board[0]) - 1 and board[y][x + 1] == "0" and (x + 1, y) not in self.body:
                self.body.append((x+1, y))
                x, y = x + 1, y
            elif y < len(board) - 1 and board[y + 1][x] == "0" and (x, y + 1) not in self.body:
                self.body.append((x, y + 1))
                x, y = x, y + 1


def setup():
    pg.init()
    screen = pg.display.set_mode((1280, 720))
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
    while green_apples[0] == green_apples[1]:
        green_apples[1] = (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
    red_apple = (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
    for apple in green_apples:
        while apple == red_apple:
            red_apple = (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
        board[apple[1]][apple[0]] = "G"
    board[red_apple[1]][red_apple[0]] = "R"
    return board


def setup_snake(board) -> tuple[Snake, list]:
    snake = Snake()
    snake.head = (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
    while board[snake.head[1]][snake.head[0]] != "0":
        snake.head = (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
    snake._set_body(board)
    board[snake.head[1]][snake.head[0]] = "H"
    for segment in snake.body:
        x, y = segment
        board[y][x] = "S"
    return snake, board



def main():
    # screen, clock, running = setup()
    board = init_board()
    board = setup_board(board)
    snake, board = setup_snake(board)
    for row in board:
        print(row)
    print(snake.head, snake.body)
    # loop(screen, clock, running)


if __name__ == "__main__":
    main()
