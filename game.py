import pygame as pg
import random


class Snake:
    def __init__(self):
        self.head: tuple[int, int] = ()
        self.body: list[tuple[int, int]] = []
        self.head_x = None
        self.head_y = None
        self.alive = True

    def _set_body(self):
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

    def move(self, dir):
        previous_loc = self.head
        self.head_x += dir[0]
        self.head_y += dir[1]
        self.head = (self.head_x, self.head_y)
        self.check_wall()
        if self.alive:
            if board[self.head_y][self.head_x] == "G":
                self.grow(previous_loc)
                place_apple("G")
                return
            if board[self.head_y][self.head_x] == "R":
                self.shrink()
                place_apple("R")
        for i in range(len(self.body)):
            tmp = self.body[i]
            self.body[i] = previous_loc
            previous_loc = tmp
        self.check_in_body()
        print(self.alive)

    def grow(self, loc):
        self.body.insert(0, loc)

    def shrink(self):
        if len(self.body) >= 1:
            self.body.pop()
        elif len(self.body) == 0:
            self.alive = False

    def check_wall(self):
        if (self.head[0] < 0 or self.head[0] >= len(board[0])
            or self.head[1] < 0 or self.head[1] >= len(board)):
            self.alive = False

    def check_in_body(self):
        if self.head in self.body:
            self.alive = False

    def check_win(self):
        return len(self.body) >= len(board) * len(board[0]) - 1        


def setup():
    pg.init()
    screen = pg.display.set_mode((1280, 720))
    clock = pg.time.Clock()
    running = True
    return screen, clock, running


def stop_loop(event, running):
    if event.type == pg.QUIT:
        running = False
    return running


def loop(screen, clock, running, snake):
    while running:
        events = pg.event.get()
        screen.fill("gray")
        for event in events:
            running = stop_loop(event, running)
            check_move(event, snake)
        update_board(snake)
        draw_grid(screen)
        if snake.check_win():
            print("Win")
            running = False
        if not snake.alive:
            snake = restart()
        pg.display.flip()
        clock.tick(60)
    pg.quit()


def check_move(event, snake):
    if event.type == pg.KEYDOWN:
        if event.key == pg.K_q:
            snake.move((-1, 0))
        elif event.key == pg.K_d:
            snake.move((1, 0))
        elif event.key == pg.K_z:
            snake.move((0, -1))
        elif event.key == pg.K_s:
            snake.move((0, 1))


def init_board():
    grid = [['0' for _ in range(10)] for _ in range(10)]
    return grid 


def setup_board():
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


def update_board(snake):
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == "S" or board[y][x] == "H":
                board[y][x] = "0"
            if (x, y) == snake.head:
                board[y][x] = "H"
            if (x, y) in snake.body:
                board[y][x] = "S"


def setup_snake():
    snake = Snake()
    snake.head = (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
    while board[snake.head[1]][snake.head[0]] != "0":
        snake.head = (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
    snake.head_x, snake.head_y = snake.head
    snake._set_body()
    board[snake.head[1]][snake.head[0]] = "H"
    for segment in snake.body:
        x, y = segment
        board[y][x] = "S"
    return snake


def draw_grid(screen):
    starting_x = int(screen.width / 4)
    starting_y = int(screen.height / 5)
    square_size = 48
    curr_x = starting_x
    curr_y = starting_y
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == "G":
                pg.draw.rect(screen, "green", (curr_x, curr_y, square_size, square_size))
            elif board[y][x] == "R":
                pg.draw.rect(screen, "red", (curr_x, curr_y, square_size, square_size))
            elif board[y][x] == "H":
                pg.draw.rect(screen, "blue", (curr_x, curr_y, square_size, square_size))
            elif board[y][x] == "S":
                pg.draw.rect(screen, "cyan", (curr_x, curr_y, square_size, square_size))
            pg.draw.rect(screen, "black", (curr_x, curr_y, square_size, square_size), width=1)
            curr_x += square_size - 1
        curr_x = starting_x
        curr_y += square_size - 1


def place_apple(apple):
    available_place = 0
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == "0":
                available_place += 1
    if available_place < 1:
        return
    loc = (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
    while board[loc[1]][loc[0]] != "0":
        loc = (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
    board[loc[1]][loc[0]] = apple


def restart():
    reset_board()
    setup_board()
    snake = setup_snake()
    return snake


def reset_board():
    for y in range(len(board)):
        for x in range(len(board[0])):
            board[y][x] = "0"


board = init_board()


def main():
    screen, clock, running = setup()
    setup_board()
    snake = setup_snake()
    loop(screen, clock, running, snake)


if __name__ == "__main__":
    main()
