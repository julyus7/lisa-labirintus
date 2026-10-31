"""Host-only validation and legal replay generation for the Lisa maze model."""
from collections import Counter, deque
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time

from rules import DELTA, Game, SIZE, load_levels, plan

HERE = Path(__file__).resolve().parent
counts = Counter()


def check(group, condition, detail):
    if not condition:
        raise AssertionError(f"{group}: {detail}")
    counts[group] += 1


def reachable(world, start):
    visited = {tuple(start)}
    queue = deque(visited)
    while queue:
        x, y = queue.popleft()
        for dx, dy in DELTA:
            nx, ny = x + dx, y + dy
            if 0 <= nx < SIZE and 0 <= ny < SIZE and world[ny * SIZE + nx] == " " and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))
    return visited


def fog_at(x, y):
    return {ny * SIZE + nx for dx, dy in ((0, 0),) + DELTA
            if 0 <= (nx := x + dx) < SIZE and 0 <= (ny := y + dy) < SIZE}


def index_set(values):
    return {i for i, value in enumerate(values) if value}


def schema_tests(levels):
    check("schema", len(levels) == 3, "three levels")
    check("schema", len({definition["name"] for definition in levels}) == 3, "unique names")
    check("schema", len({"".join(definition["rows"]) for definition in levels}) == 3, "unique maps")
    for number, definition in enumerate(levels):
        rows = definition["rows"]
        check("schema", definition["name"].isascii() and 0 < len(definition["name"]) <= 20, number)
        check("schema", len(rows) == SIZE, number)
        for row in rows:
            check("schema", len(row) == SIZE and set(row) <= {"#", " "}, (number, row))
        check("schema", rows[0] == rows[-1] == "#" * SIZE, number)
        check("schema", all(row[0] == row[-1] == "#" for row in rows), number)
        check("schema", 0 <= definition["facing"] < 4, number)
        check("schema", len(definition["keys"]) == (1 if number == 0 else 3), number)
        points = [tuple(definition["start"]), tuple(definition["exit"])] + [tuple(p) for p in definition["keys"]]
        check("schema", len(set(points)) == len(points), number)
        for x, y in points:
            check("schema", 0 < x < SIZE - 1 and 0 < y < SIZE - 1 and rows[y][x] == " ", (number, x, y))
        world = "".join(rows)
        open_cells = {(x, y) for y in range(SIZE) for x in range(SIZE) if rows[y][x] == " "}
        check("connectivity", reachable(world, definition["start"]) == open_cells, number)
        for x, y in open_cells:
            check("connectivity", reachable(world, (x, y)) == open_cells, (number, x, y))


def geometry_and_command_tests(levels):
    """Exhaust all map coordinates/directions; execute all legal open-cell states."""
    for level, definition in enumerate(levels):
        base = Game(level)
        for y in range(SIZE):
            for x in range(SIZE):
                for direction in range(4):
                    for action in (1, 2, 3, 4):
                        dx, dy = DELTA[direction]
                        sign = 1 if action == 3 else -1
                        nx, ny = (x + sign * dx, y + sign * dy) if action in (3, 4) else (x, y)
                        in_bounds = 0 <= nx < SIZE and 0 <= ny < SIZE
                        check("coordinate_bounds", -1 <= nx <= SIZE and -1 <= ny <= SIZE, (level, x, y, direction, action))
                        if base.world[y * SIZE + x] == "#":
                            continue  # A wall is never a reachable player state.
                        game = deepcopy(base)
                        game.x, game.y, game.dir = x, y, direction
                        game.seen = [int(i in fog_at(x, y)) for i in range(SIZE * SIZE)]
                        before = game.snapshot()
                        accepted = game.step(action)
                        check("commands", accepted and game.actions == 1, (level, x, y, direction, action))
                        expected_turn = (direction + (3 if action == 1 else 1)) % 4 if action in (1, 2) else direction
                        check("commands", game.dir == expected_turn, "direction")
                        translated = action in (3, 4) and in_bounds and base.world[ny * SIZE + nx] != "#"
                        check("commands", (game.x, game.y) == ((nx, ny) if translated else (x, y)), "position")
                        check("commands", game.moves == int(translated), "move counter")
                        check("commands", game.turns == int(action in (1, 2)), "turn counter")
                        check("commands", game.bumps == int(action in (3, 4) and not translated), "bump counter")
                        removed = int(translated and before["keys"][ny * SIZE + nx] == 1)
                        check("commands", game.remaining == base.total - removed, "remaining key count")
                        expected_keys = before["keys"].copy()
                        if translated:
                            expected_keys[ny * SIZE + nx] = 0
                        check("commands", game.keys == expected_keys, "key array")
                        expected_fog = fog_at(x, y) | (fog_at(nx, ny) if translated else set())
                        check("fog", index_set(game.seen) == expected_fog, "reveal on translation only")
                        should_win = translated and (nx, ny) == game.exit and game.remaining == 0
                        check("commands", game.phase == (2 if should_win else 1), "win only by translation")
                        check("commands", game.actions == game.moves + game.turns + game.bumps, "counter partition")
                        check("commands", 0 <= game.x < SIZE and 0 <= game.y < SIZE, "state bounded")
                        check("commands", game.world == base.world, "immutable map")


def state_tests(levels):
    for level, definition in enumerate(levels):
        game = Game(level)
        check("initial", game.phase == 1 and game.fullmap, level)
        check("initial", index_set(game.seen) == fog_at(game.x, game.y), level)
        check("initial", sum(game.keys) == game.total == game.remaining, level)
        original_fog = game.seen.copy()
        game.toggle_map()
        check("fog", not game.fullmap and game.seen == original_fog, "hide assistance preserves fog")
        game.toggle_map()
        check("fog", game.fullmap and game.seen == original_fog, "show assistance preserves fog")
        for _ in range(4):
            game.step(2)
            check("fog", game.seen == original_fog, "rotation does not reveal distant cells")
        check("rotation", game.dir == definition["facing"] and game.turns == 4, "four quarter turns")
        for _ in range(4):
            game.step(1)
        check("rotation", game.dir == definition["facing"] and game.turns == 8, "four reverse quarter turns")
        for bad in (-1, 0, 5, 99):
            before = game.snapshot()
            try:
                game.step(bad)
            except ValueError:
                pass
            else:
                raise AssertionError("Invalid action was accepted")
            check("invalid", game.snapshot() == before, bad)
        game.reset(level)
        check("reset", game.snapshot() == Game(level).snapshot(), level)
        # A host-only constructed exit state catches the blocked-move win bug.
        game.x, game.y = game.exit
        game.keys = [0] * (SIZE * SIZE)
        game.remaining = 0
        blocked_direction = next(d for d, (dx, dy) in enumerate(DELTA)
                                 if game.world[(game.y + dy) * SIZE + game.x + dx] == "#")
        game.dir = blocked_direction
        game.step(3)
        check("exit_semantics", game.phase == 1 and game.bumps == 1, "blocked move on unlocked exit does not win")
        game.step(1)
        check("exit_semantics", game.phase == 1, "turn on unlocked exit does not win")


def trace_state(game, action):
    return {"action": action, **{name: getattr(game, name) for name in
            ("x", "y", "dir", "phase", "remaining", "actions", "moves", "turns", "bumps")},
            "seen_count": sum(game.seen),
            "checksum": sum((i + 1) * (game.keys[i] + game.seen[i]) for i in range(SIZE * SIZE)) % 30011}


def complete_replays(levels):
    replays = []
    for level, definition in enumerate(levels):
        game = Game(level)
        actions = game.route_to_win.copy()
        check("replay", len(actions) < (40 if level == 0 else 180), "manageable native replay length")
        trace = []
        for number, action in enumerate(actions):
            check("replay", game.phase == 1, "no commands after early victory")
            before_keys = game.remaining
            before_fog = index_set(game.seen)
            game.step(action)
            trace.append(trace_state(game, action))
            check("replay", game.remaining <= before_keys, "keys monotone")
            check("replay", index_set(game.seen) >= before_fog, "fog monotone")
            check("replay", sum(game.keys) == game.remaining, "array/count consistency")
            check("replay", game.bumps == 0, "BFS route has no wall bumps")
            check("replay", game.phase == (2 if number == len(actions) - 1 else 1), "win on final action")
        check("replay", game.phase == 2 and game.remaining == 0 and (game.x, game.y) == game.exit, "complete level win")
        frozen = deepcopy(game.snapshot())
        for action in (1, 2, 3, 4) * 4:
            check("freeze", game.step(action) is False and game.snapshot() == frozen, "win freezes all later commands")
        replays.append({"level": level, "name": definition["name"], "actions": actions,
                        "expected": game.snapshot(), "trace": trace})
        game.reset((level + 1) % len(levels))
        check("reset", game.phase == 1 and game.actions == 0 and game.moves == 0 and game.turns == 0 and game.bumps == 0,
              "reset after win starts clean")
    return replays


def route_to_exit_ignoring_keys(game):
    start = (game.x, game.y, game.dir)
    queue = deque([start])
    previous = {start: None}
    while queue:
        state = queue.popleft()
        x, y, direction = state
        if (x, y) == game.exit:
            result = []
            while previous[state] is not None:
                state, action = previous[state]
                result.append(action)
            return list(reversed(result))
        for action in (1, 2, 3, 4):
            nx, ny, nd = x, y, direction
            if action == 1:
                nd = (direction + 3) % 4
            elif action == 2:
                nd = (direction + 1) % 4
            else:
                dx, dy = DELTA[direction]
                sign = 1 if action == 3 else -1
                nx, ny = x + sign * dx, y + sign * dy
                if not (0 <= nx < SIZE and 0 <= ny < SIZE) or game.world[ny * SIZE + nx] == "#":
                    continue
            following = (nx, ny, nd)
            if following not in previous:
                previous[following] = (state, action)
                queue.append(following)
    raise AssertionError("No path to exit")


def locked_exit_replay(levels):
    for level in range(1, len(levels)):
        game = Game(level)
        prefix = route_to_exit_ignoring_keys(game)
        trace = []
        for action in prefix:
            game.step(action)
            trace.append(trace_state(game, action))
        if game.remaining == 0:
            continue
        check("locked_exit", game.phase == 1 and (game.x, game.y) == game.exit and game.remaining > 0,
              "legal entry to locked exit remains playable")
        entry_state = game.snapshot()
        suffix = plan(levels[level], game.x, game.y, game.dir, game.keys)
        for number, action in enumerate(suffix):
            check("locked_exit", game.phase == 1, "no early win after locked exit")
            game.step(action)
            trace.append(trace_state(game, action))
            check("locked_exit", game.phase == (2 if number == len(suffix) - 1 else 1), "collect then re-enter")
        check("locked_exit", game.phase == 2 and game.remaining == 0, "eventual win")
        return {"level": level, "actions": prefix + suffix,
                "entry_index": len(prefix) - 1, "entry_state": entry_state,
                "expected": game.snapshot(), "trace": trace}
    raise AssertionError("Need one legal locked-exit example")


def main():
    started = time.perf_counter()
    levels = load_levels()
    schema_tests(levels)
    geometry_and_command_tests(levels)
    state_tests(levels)
    replays = complete_replays(levels)
    locked_exit = locked_exit_replay(levels)
    replay_data = {"schema": 1, "levels": replays, "locked_exit": locked_exit}
    (HERE / "model-replays.json").write_text(json.dumps(replay_data, indent=2) + "\n", encoding="utf-8")
    report = {"schema": 1, "status": "passed", "checks": sum(counts.values()),
              "groups": dict(sorted(counts.items())), "seconds": round(time.perf_counter() - started, 3),
              "level_count": len(levels), "replay_lengths": [len(item["actions"]) for item in replays],
              "locked_exit_replay_length": len(locked_exit["actions"]),
              "source_sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                for name in ("levels.json", "rules.py", "test_rules.py")},
              "scope": "Independent host model only; no native binary or physical Lisa validation is implied."}
    (HERE / "model-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
