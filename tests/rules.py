"""Independent integer model for the native Lisa 3D maze game.

Only the Python standard library is used.  Coordinates are zero based and the
flattened arrays are row major.  North, east, south, west are 0, 1, 2, 3.
"""
from collections import deque
import json
from pathlib import Path

SIZE = 15
DELTA = ((0, -1), (1, 0), (0, 1), (-1, 0))
LEVELS_PATH = Path(__file__).with_name("levels.json")


def load_levels():
    return json.loads(LEVELS_PATH.read_text(encoding="utf-8"))


def plan(level, x=None, y=None, direction=None, remaining=None):
    """Shortest sequence of turn/translation commands, found by BFS.

    A locked exit is an ordinary walkable cell.  Winning requires translating
    onto it with no remaining keys, so returning to an earlier exit is allowed.
    Wall bumps and redundant turns are omitted from planned routes.
    """
    world = "".join(level["rows"])
    x, y = level["start"] if x is None else (x, y)
    direction = level["facing"] if direction is None else direction
    points = [tuple(point) for point in level["keys"]]
    if remaining is not None:
        points = [point for point in points if remaining[point[1] * SIZE + point[0]]]
    key_bits = {point: 1 << i for i, point in enumerate(points)}
    mask = (1 << len(points)) - 1
    start = (x, y, direction, mask)
    queue = deque([start])
    previous = {start: None}
    while queue:
        state = queue.popleft()
        sx, sy, facing, keys = state
        for action in (1, 2, 3, 4):
            nx, ny, nf, nk = sx, sy, facing, keys
            translated = action in (3, 4)
            if action == 1:
                nf = (facing + 3) % 4
            elif action == 2:
                nf = (facing + 1) % 4
            else:
                dx, dy = DELTA[facing]
                sign = 1 if action == 3 else -1
                nx, ny = sx + dx * sign, sy + dy * sign
                if not (0 <= nx < SIZE and 0 <= ny < SIZE):
                    continue
                if world[ny * SIZE + nx] == "#":
                    continue
                nk &= ~key_bits.get((nx, ny), 0)
            following = (nx, ny, nf, nk)
            if translated and (nx, ny) == tuple(level["exit"]) and nk == 0:
                # The final action matters even if its resulting state has
                # already been visited (for example starting on an exit).
                suffix = [action]
                cursor = state
                while previous[cursor] is not None:
                    cursor, incoming = previous[cursor]
                    suffix.append(incoming)
                return list(reversed(suffix))
            if following not in previous:
                previous[following] = (state, action)
                queue.append(following)
    raise ValueError("No route can collect all keys and enter the exit")


class Game:
    def __init__(self, level=0):
        self.levels = load_levels()
        self.reset(level)

    def reset(self, level):
        if not 0 <= level < len(self.levels):
            raise ValueError("Unknown level")
        self.level = level
        definition = self.levels[level]
        self.world = "".join(definition["rows"])
        self.x, self.y = definition["start"]
        self.dir = definition["facing"]
        self.phase = 1
        self.keys = [0] * (SIZE * SIZE)
        for x, y in definition["keys"]:
            self.keys[y * SIZE + x] = 1
        self.seen = [0] * (SIZE * SIZE)
        self.total = len(definition["keys"])
        self.remaining = self.total
        self.actions = self.moves = self.turns = self.bumps = 0
        self.fullmap = True
        self.reveal()
        self.route_to_win = plan(definition)

    @property
    def exit(self):
        return tuple(self.levels[self.level]["exit"])

    def reveal(self):
        for dx, dy in ((0, 0),) + DELTA:
            x, y = self.x + dx, self.y + dy
            if 0 <= x < SIZE and 0 <= y < SIZE:
                self.seen[y * SIZE + x] = 1

    def toggle_map(self):
        self.fullmap = not self.fullmap

    def step(self, action):
        """Apply one command; return whether any accepted action was applied."""
        if self.phase != 1:
            return False
        if action not in (1, 2, 3, 4):
            raise ValueError("Actions are 1=left, 2=right, 3=forward, 4=back")
        self.actions += 1
        if action in (1, 2):
            self.dir = (self.dir + (3 if action == 1 else 1)) % 4
            self.turns += 1
            return True
        dx, dy = DELTA[self.dir]
        sign = 1 if action == 3 else -1
        x, y = self.x + dx * sign, self.y + dy * sign
        if not (0 <= x < SIZE and 0 <= y < SIZE) or self.world[y * SIZE + x] == "#":
            self.bumps += 1
            return True
        self.x, self.y = x, y
        self.moves += 1
        index = y * SIZE + x
        if self.keys[index]:
            self.keys[index] = 0
            self.remaining -= 1
        self.reveal()
        if (x, y) == self.exit and self.remaining == 0:
            self.phase = 2
        return True

    def snapshot(self):
        return {name: getattr(self, name) for name in
                ("level", "x", "y", "dir", "phase", "total", "remaining",
                 "actions", "moves", "turns", "bumps", "fullmap")} | {
                     "keys": self.keys.copy(), "seen": self.seen.copy()}
