import pygame as pg
import random
from agent import Agent
import sys
from tqdm import tqdm
from parse_arg import parse


class Snake:
    def __init__(self):
        self.head: tuple[int, int] = ()
        self.body: list[tuple[int, int]] = []
        self.head_x = None
        self.head_y = None
        self.alive = True
        self.win = False

    def _set_body(self):
        segments = 2
        x, y = self.head
        while len(self.body) < segments:
            possible_slot = []
            if x > 0 and board[y][x - 1] == "0" and (x - 1, y) not in self.body:
                possible_slot.append((x-1, y))
            if y > 0 and board[y - 1][x] == "0" and (x, y - 1) not in self.body:
                possible_slot.append((x, y - 1))
            if x < len(board[0]) - 1 and board[y][x + 1] == "0" and (x + 1, y) not in self.body:
                possible_slot.append((x+1, y))
            if y < len(board) - 1 and board[y + 1][x] == "0" and (x, y + 1) not in self.body:
                possible_slot.append((x, y + 1))
            if len(possible_slot) < 1:
                return False
            self.body.append(random.choice(possible_slot))
            x, y = self.body[-1]
        return True

    def move(self, dir):
        reward = -10
        new_x = self.head_x + dir[0]
        new_y = self.head_y + dir[1]
        if (new_x, new_y) in self.body:
            self.alive = False
            return -150
        if (
            new_x < 0
            or new_x >= len(board[0])
            or new_y < 0
            or new_y >= len(board)
        ):
            self.alive = False
            return -100
        previous_loc = self.head
        self.head_x = new_x
        self.head_y = new_y
        self.head = (new_x, new_y)
        self.check_wall()
        if self.alive:
            if board[self.head_y][self.head_x] == "G":
                self.grow(previous_loc)
                place_apple("G")
                reward = 100
                return reward
            if board[self.head_y][self.head_x] == "R":
                self.shrink()
                place_apple("R")
                reward = -50
        for i in range(len(self.body)):
            tmp = self.body[i]
            self.body[i] = previous_loc
            previous_loc = tmp
        self.check_in_body()
        if not self.alive:
            reward = -10
        return reward

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
        return len(self.body) >= 9


def setup():
    pg.init()
    screen = pg.display.set_mode((CELL_SIZE * len(board[0]) - len(board[0]),
                                  CELL_SIZE * len(board) - len(board)))
    clock = pg.time.Clock()
    running = True
    return screen, clock, running


def stop_loop(event, running):
    if event.type == pg.QUIT:
        running = False
    return running


def loop(screen, clock, running, snake, agent, max_session):
    session = 1
    score = 0
    max_length = 0
    all_length = []
    reached_10 = []
    all_life = []
    moved = 0
    max_step = 300
    while running and session <= max_session:
        events = pg.event.get()
        screen.fill("gray")
        for event in events:
            running = stop_loop(event, running)
        state = agent.state
        action_name = agent.choose_action()
        action = agent.actions[action_name]
        reward = snake.move(action)
        update_board(snake)
        moved += 1
        if snake.alive:
            agent.get_vision(board)
            agent.get_state()
            next_state = agent.state
        else:
            next_state = None
        agent.update_q_value(
            state, action_name,
            reward, next_state
        )
        score += reward
        max_length = max(max_length, len(snake.body) + 1)
        if moved >= max_step:
            reward = -3
            snake.alive = False
        draw_grid(screen)
        if not snake.alive or snake.win:
            all_length.append(max_length)
            reached_10.append(1 if max_length >= 10 else 0)
            all_life.append(moved)
            snake = restart(agent)
            agent.epsilon = max(0.01, agent.epsilon * 0.999)
            agent.get_vision(board)
            agent.get_state()
            moved = 0
            session += 1
            score = 0
            max_length = 0
        pg.display.flip()
        clock.tick(60)
    print(f"Model: {max_session} sessions")
    print("-" * 20)
    print(f"Average length : {(sum(all_length)/len(all_length))}")
    print(f"Max length     : {max(all_length)}")
    print(f"Reach 10       : {sum(reached_10)}/{len(reached_10)}")
    print(f"Average life   : {(sum(all_life)/len(all_life))}")
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
    for _ in range(2):
        x, y = get_random_o()
        board[y][x] = "G"
    x, y = get_random_o()
    board[y][x] = "R"


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
    snake.head = get_random_o()
    snake.head_x, snake.head_y = snake.head
    board[snake.head[1]][snake.head[0]] = "H"
    while not snake._set_body():
        board[snake.head[1]][snake.head[0]] = "0"
        snake.head = get_random_o()
        snake.head_x, snake.head_y = snake.head
        snake.body = []
        board[snake.head[1]][snake.head[0]] = "H"
    for segment in snake.body:
        x, y = segment
        board[y][x] = "S"
    return snake


def draw_grid(screen):
    starting_x = 0
    starting_y = 0
    square_size = CELL_SIZE
    curr_x = starting_x
    curr_y = starting_y
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == "G":
                pg.draw.rect(screen, "green", (curr_x, curr_y,
                                               square_size, square_size))
            elif board[y][x] == "R":
                pg.draw.rect(screen, "red", (curr_x, curr_y,
                                             square_size, square_size))
            elif board[y][x] == "H":
                pg.draw.rect(screen, "blue", (curr_x, curr_y,
                                              square_size, square_size))
            elif board[y][x] == "S":
                pg.draw.rect(screen, "cyan", (curr_x, curr_y,
                                              square_size, square_size))
            pg.draw.rect(screen, "black", (curr_x, curr_y,
                                           square_size, square_size), width=1)
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
    loc = get_random_o()
    board[loc[1]][loc[0]] = apple


def restart(agent):
    reset_board()
    setup_board()
    snake = setup_snake()
    agent.snake = snake
    agent.last_action = None
    return snake


def reset_board():
    for y in range(len(board)):
        for x in range(len(board[0])):
            board[y][x] = "0"


def get_random_o():
    available_loc = []
    for j in range(len(board)):
        for i in range(len(board[0])):
            if board[j][i] == "0":
                available_loc.append((i, j))
    return random.choice(available_loc)


board = init_board()
CELL_SIZE = 48


def train(snake, agent, max_session):
    session = 1
    score = 0
    max_length = 0
    all_length = []
    reached_10 = []
    all_life = []
    moved = 0
    max_step = 300
    pbar = tqdm(total=max_session)
    while session <= max_session:
        state = agent.state
        action_name = agent.choose_action()
        action = agent.actions[action_name]
        reward = snake.move(action)
        update_board(snake)
        moved += 1
        if snake.alive:
            agent.get_vision(board)
            agent.get_state()
            next_state = agent.state
        else:
            next_state = None
        if snake.check_win():
            snake.win = True
        agent.update_q_value(
            state, action_name,
            reward, next_state
        )
        score += reward
        max_length = max(max_length, len(snake.body) + 1)
        if moved >= max_step:
            reward = -3
            snake.alive = False
        if not snake.alive or snake.win:
            all_length.append(max_length)
            reached_10.append(1 if max_length >= 10 else 0)
            all_life.append(moved)
            snake = restart(agent)
            agent.epsilon = max(0.01, agent.epsilon * 0.999)
            agent.get_vision(board)
            agent.get_state()
            moved = 0
            session += 1
            score = 0
            max_length = 0
            pbar.update(1)
    pbar.close()
    print(f"Model: {max_session} sessions")
    print("-" * 20)
    print(f"Average length : {(sum(all_length)/len(all_length))}")
    print(f"Max length     : {max(all_length)}")
    print(f"Reach 10       : {sum(reached_10)}/{len(reached_10)}")
    print(f"Average life   : {(sum(all_life)/len(all_life))}")


def main():
    args = parse(sys.argv[1:-1])
    setup_board()
    snake = setup_snake()
    agent = Agent(snake)
    agent.get_vision(board)
    agent.get_state()
    max_session = args.session
    if args.dontlearn:
        agent.learning = False
    if args.load:
        agent.load(args.load)
    if args.visual == "on":
        screen, clock, running = setup()
        loop(screen, clock, running, snake, agent, max_session)
    else:
        train(snake, agent, max_session)
    if args.save:
        agent.save(args.save)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        aperture = [
            "⠀⠀⠀⠀⢀⡠⣤⣶⣶⣶⣦⡄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
            "⠀⠀⢀⣴⣿⣿⣶⣝⡻⣿⣿⣇⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
            "⠀⣠⡿⠿⢿⣛⠛⠋⠉⠈⠙⠿⢸⣿⣿⡷⣀⣀⠀⠀⠀⢀⣀⣀⣀⡀⠀⠀⣀⣀⣀⣀⡀⠀⣀⣀⣀⣀⠀⢀⣀⣀⣀⣀⣀⠀⣀⣀⠀⠀⣀⡀⠀⢀⣀⣀⣀⡀⠀⠀⣀⣀⣀⣀⡀",
            "⠀⣶⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠘⣿⢟⣼⣿⣿⡆⠀⠀⣾⣿⠛⣻⣿⠀⢸⣿⠟⠛⠛⠀⢸⣿⠟⢻⣿⡇⠘⠛⣿⣿⠛⠛⢀⣿⡟⠀⢰⣿⡇⠀⣿⡿⠛⣿⣿⠀⢰⣿⠟⠛⠛⠀",
            "⠠⣿⣿⣟⡆⠀⠀⠀⠀⠀⠀⠀⠀⢋⣾⣿⣬⣿⣇⠀⢠⣿⡿⠿⠿⠋⠀⣾⡿⠛⠛⠇⠀⣾⣿⠿⣿⣯⠀⠀⢠⣿⡏⠀⠀⢸⣿⠃⠀⣼⣿⠀⢰⣿⡿⢿⣿⡅⠀⣾⣿⠛⠛⠇⠀",
            "⠀⣿⢯⣾⣿⠀⠀⠀⠀⠀⠀⠀⠠⠿⠟⠉⠉⠿⠿⠀⠸⠿⠃⠀⠀⠀⠰⠿⠿⠿⠿⠃⠠⠿⠇⠠⠿⠯⠀⠀⠸⠿⠁⠀⠀⠘⠿⣷⡾⠿⠃⠀⠼⠿⠀⠸⠿⠅⠠⠿⠿⠿⠿⠃⠀",
            "⠀⠀⣿⣿⣿⡼⣦⣄⢀⣀⣤⣤⣴⣶⣶⡿⠁⠀⡆⠀⠀⢀⣶⡄⠀⢰⣖⣲⠀⢠⡖⠒⡆⠀⢰⣖⡦⠀⢀⣴⡄⠀⠒⣶⠒⠀⣰⠖⢲⠀⠀⣶⣲⠄⠀⡆⠀⢰⣒⡂⠀⣶⣒⡆⠀",
            "⠀⠀⠈⠻⣿⡇⣿⣿⣷⣮⣻⢿⣿⡿⠏⠀⠀⠀⠓⠲⠀⠞⠉⠹⠀⠘⠓⠚⠀⠈⠳⠖⠃⠀⠸⠀⠗⠀⠞⠉⠹⠂⠀⠻⠀⠀⠘⠲⠞⠀⠀⠇⠘⠆⠀⠇⠀⠘⠒⠆⠀⠓⠶⠃⠀",
            "⠀⠀⠀⠀⠈⠙⠘⠿⠿⠿⠟⠓⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
        ]
        print("Bip~ boop..., you.. killed me.. ~biiip")
        for line in aperture:
            print(line)
