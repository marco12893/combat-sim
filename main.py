from dataclasses import dataclass
import random


GRID_SIZE = 5
MAX_HULL = 12
MAX_AMMO = 6
SEA_STATES = ["calm", "breezy", "rough"]
DIRECTIONS = {
    "n": (0, -1),
    "s": (0, 1),
    "e": (1, 0),
    "w": (-1, 0),
}


@dataclass
class Ship:
    name: str
    x: int
    y: int
    hull: int = MAX_HULL
    ammo: int = MAX_AMMO
    repair_kits: int = 2

    def is_sunk(self) -> bool:
        return self.hull <= 0

    def position(self) -> tuple[int, int]:
        return self.x, self.y


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def manhattan_distance(a: Ship, b: Ship) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def move_ship(ship: Ship, direction: str) -> str:
    dx, dy = DIRECTIONS[direction]
    old_x, old_y = ship.x, ship.y
    ship.x = clamp(ship.x + dx, 0, GRID_SIZE - 1)
    ship.y = clamp(ship.y + dy, 0, GRID_SIZE - 1)

    if (ship.x, ship.y) == (old_x, old_y):
        return f"{ship.name} is already at the edge of the map."
    return f"{ship.name} sails to sector {format_sector(ship.x, ship.y)}."


def fire(attacker: Ship, defender: Ship, sea_state: str) -> str:
    if attacker.ammo <= 0:
        return f"{attacker.name} has no cannonballs left."

    attacker.ammo -= 1
    distance = manhattan_distance(attacker, defender)
    hit_chance = 0.85 - (distance * 0.15)

    if sea_state == "breezy":
        hit_chance -= 0.05
    elif sea_state == "rough":
        hit_chance -= 0.15

    hit_chance = max(0.2, min(0.9, hit_chance))
    if random.random() > hit_chance:
        return f"{attacker.name} fires and misses."

    damage = random.randint(2, 4)
    if sea_state == "calm":
        damage += 1
    defender.hull = max(0, defender.hull - damage)
    if defender.is_sunk():
        return f"{attacker.name} lands a devastating hit for {damage} damage and sinks {defender.name}!"
    return f"{attacker.name} hits {defender.name} for {damage} damage."


def repair(ship: Ship) -> str:
    if ship.repair_kits <= 0:
        return f"{ship.name} has no repair kits remaining."
    if ship.hull >= MAX_HULL:
        return f"{ship.name} is already at full strength."

    ship.repair_kits -= 1
    restored = min(3, MAX_HULL - ship.hull)
    ship.hull += restored
    return f"{ship.name} repairs {restored} hull."


def format_sector(x: int, y: int) -> str:
    return f"{chr(65 + x)}{y + 1}"


def draw_map(player: Ship, enemy: Ship) -> None:
    print("\nSea map:")
    header = "   " + " ".join(chr(65 + i) for i in range(GRID_SIZE))
    print(header)
    for y in range(GRID_SIZE):
        row = ["."] * GRID_SIZE
        if player.y == y:
            row[player.x] = "P"
        if enemy.y == y:
            row[enemy.x] = "X" if row[enemy.x] == "." else "!"
        print(f"{y + 1}  " + " ".join(row))


def print_status(player: Ship, enemy: Ship, sea_state: str) -> None:
    print(f"\nSea state: {sea_state}")
    print(
        f"Your ship: hull {player.hull}/{MAX_HULL}, ammo {player.ammo}/{MAX_AMMO}, "
        f"repairs {player.repair_kits}, position {format_sector(player.x, player.y)}"
    )
    print(
        f"Enemy ship: hull {enemy.hull}/{MAX_HULL}, ammo {enemy.ammo}/{MAX_AMMO}, "
        f"position {format_sector(enemy.x, enemy.y)}"
    )
    print(f"Range to target: {manhattan_distance(player, enemy)}")


def choose_sea_state() -> str:
    return random.choice(SEA_STATES)


def player_turn(player: Ship, enemy: Ship, sea_state: str) -> None:
    while True:
        command = input(
            "\nChoose action: move [n/s/e/w], fire, repair, status, quit\n> "
        ).strip().lower()

        if command == "quit":
            raise SystemExit("You abandon the battle.")

        if command == "status":
            draw_map(player, enemy)
            print_status(player, enemy, sea_state)
            continue

        if command.startswith("move "):
            _, _, direction = command.partition(" ")
            if direction in DIRECTIONS:
                print(move_ship(player, direction))
                return
            print("Use move n, move s, move e, or move w.")
            continue

        if command == "fire":
            print(fire(player, enemy, sea_state))
            return

        if command == "repair":
            print(repair(player))
            return

        print("Unknown command.")


def enemy_turn(enemy: Ship, player: Ship, sea_state: str) -> None:
    if enemy.is_sunk():
        return

    distance = manhattan_distance(enemy, player)
    if enemy.hull <= 4 and enemy.repair_kits > 0 and random.random() < 0.5:
        print(repair(enemy))
        return

    if distance <= 2 and enemy.ammo > 0:
        print(fire(enemy, player, sea_state))
        return

    dx = player.x - enemy.x
    dy = player.y - enemy.y
    if abs(dx) > abs(dy):
        direction = "e" if dx > 0 else "w"
    else:
        direction = "s" if dy > 0 else "n"
    print(move_ship(enemy, direction))


def intro() -> None:
    print("Simple Naval Combat Simulator")
    print("Sink the enemy raider before it sinks you.")
    print("P = your ship, X = enemy ship, ! = same sector")


def run_game() -> None:
    player = Ship("Frigate Valor", 0, GRID_SIZE - 1)
    enemy = Ship("Raider Viper", GRID_SIZE - 1, 0)
    turn = 1

    intro()
    while True:
        sea_state = choose_sea_state()
        print(f"\n--- Turn {turn} ---")
        draw_map(player, enemy)
        print_status(player, enemy, sea_state)

        player_turn(player, enemy, sea_state)
        if enemy.is_sunk():
            print("\nVictory! The enemy ship slips beneath the waves.")
            return

        enemy_turn(enemy, player, sea_state)
        if player.is_sunk():
            print("\nDefeat. Your ship has been sunk.")
            return

        turn += 1


if __name__ == "__main__":
    try:
        run_game()
    except SystemExit as exc:
        print(exc)
