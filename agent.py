import random
import json
import pathlib


class Agent:
    def __init__(self, snake):
        self.snake = snake
        self.state = None
        self.vision = None
        self.actions = {
            "North": (0, -1),
            "South": (0, 1),
            "East": (1, 0),
            "West": (-1, 0)
        }
        self.q_table = {}
        # Randomness
        self.epsilon = 1.0
        self.learning_rate = 1
        # Importancy of future rewards
        self.gamma = 0.7
        self.learning = True
        self.last_action = None

    def get_vision(self, board):
        x, y = self.snake.head
        vision = [[' ' for _ in range(len(board[0]))]
                  for _ in range(len(board))]
        for j in range(len(board)):
            for i in range(len(board[0])):
                if x == i or y == j:
                    vision[j][i] = board[j][i]
        self.vision = vision

    def get_state(self):
        x, y = self.snake.head
        north = self.get_closest_object(x, y, 0, -1)
        south = self.get_closest_object(x, y, 0, 1)
        west = self.get_closest_object(x, y, -1, 0)
        east = self.get_closest_object(x, y, 1, 0)
        self.state = (
            north,
            south,
            west,
            east
        )
        return self.state

    def get_closest_object(self, x, y, dx, dy):
        x += dx
        y += dy
        if (x < 0 or x >= len(self.vision[0])
           or y < 0 or y >= len(self.vision)):
            return "D"
        while (
            0 <= x < len(self.vision[0])
            and 0 <= y < len(self.vision)
        ):
            cell = self.vision[y][x]

            if cell in ("G", "R"):
                return cell
            elif cell == "S":
                return "D"

            x += dx
            y += dy

        return "0"

    def get_available_actions(self):
        actions = list(self.actions)

        if self.last_action is None:
            return actions

        opposite = {
            "North": "South",
            "South": "North",
            "East": "West",
            "West": "East"
        }

        actions.remove(opposite[self.last_action])

        return actions

    def choose_action(self):
        q_values = self.get_q_values(self.state)

        if random.random() < self.epsilon:
            action = random.choice(list(self.actions))
        else:
            max_value = max(q_values.values())

            best_actions = [
                action
                for action, value in q_values.items()
                if value == max_value
            ]

            action = random.choice(best_actions)

        return action

    def get_q_values(self, state):
        if state not in self.q_table:
            self.q_table[state] = {
                "North": 0.0,
                "South": 0.0,
                "East": 0.0,
                "West": 0.0
            }

        return self.q_table[state]

    def update_q_value(self, state, action, reward, next_state):
        if not self.learning:
            return
        q_values = self.get_q_values(state)
        current_q = q_values[action]
        if next_state is None:
            target = reward
        else:
            next_q_values = self.get_q_values(next_state)
            available_actions = self.get_available_actions()
            best_next_q = max(
                next_q_values[a]
                for a in available_actions
            )
            target = reward + self.gamma * best_next_q

        q_values[action] = current_q + self.learning_rate * (
            target - current_q)

    def save(self, filename):
        tree = filename.split("/")
        files = None
        if len(tree) > 1:
            files = tree[:len(tree) - 1]
        if files:
            pathlib.Path("/".join(files)).mkdir(exist_ok=True, parents=True)
        data = {
            "epsilon": self.epsilon,
            "learning_rate": self.learning_rate,
            "gamma": self.gamma,
            "q_table": [
                {
                    "state": list(state),
                    "q_values": q_values
                }
                for state, q_values in self.q_table.items()
            ]
        }

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load(self, filename):
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.epsilon = data["epsilon"]
        self.learning_rate = data["learning_rate"]
        self.gamma = data["gamma"]

        self.q_table = {
            tuple(entry["state"]): entry["q_values"]
            for entry in data["q_table"]
        }
