import random


# Change these numbers to test battles.
# Anything you leave out defaults to 0.
ATTACKER = {"name": "Friendly Fleet", "destroyers": 3}
DEFENDER = {"name": "Enemy Fleet", "submarines": 2, "battleships": 1}

DEFAULT_FLEET = {
    "name": "Fleet",
    "destroyers": 0,
    "frigates": 0,
    "corvettes": 0,
    "submarines": 0,
    "cruisers": 0,
    "battleships": 0,
    "carriers": 0,
    "aircraft": 0,
    "modifier": 0,
}


def make_fleet(data):
    fleet = DEFAULT_FLEET.copy()
    fleet.update(data)
    fleet["light"] = (
        fleet["destroyers"]
        + fleet["frigates"]
        + fleet["corvettes"]
        + fleet["submarines"]
    )
    fleet["moderate"] = fleet["cruisers"]
    fleet["heavy"] = fleet["battleships"]
    fleet["surface"] = fleet["light"] + fleet["moderate"] + fleet["heavy"]
    return fleet


def roll_pool(count, sides, modifier):
    rolls = [random.randint(1, sides) + modifier for _ in range(count)]
    return sum(rolls), rolls


def pool_text(count, sides, modifier, rolls):
    if count == 0:
        return "0"
    bonus = f"{modifier:+d}" if modifier else ""
    return f"{count}d{sides}{bonus} -> {rolls} = {sum(rolls)}"


def duel(attacker_count, attacker_die, attacker_mod, defender_count, defender_die, defender_mod, label):
    attack_total, attack_rolls = roll_pool(attacker_count, attacker_die, attacker_mod)
    defense_total, defense_rolls = roll_pool(defender_count, defender_die, defender_mod)
    damage = max(0, attack_total - defense_total)
    line = (
        f"{label}: "
        f"{pool_text(attacker_count, attacker_die, attacker_mod, attack_rolls)} "
        f"vs {pool_text(defender_count, defender_die, defender_mod, defense_rolls)} "
        f"=> damage {damage}"
    )
    return damage, line


def resolve_side(side_name, attacker, defender):
    total_damage = 0
    lines = []
    mod_a = attacker["modifier"]
    mod_d = defender["modifier"]

    if attacker["light"] > 0:
        if defender["light"] > 0:
            damage, line = duel(
                attacker["light"], 6, mod_a,
                defender["light"], 6, mod_d,
                f"{side_name} light vs enemy light",
            )
        elif defender["moderate"] > 0:
            damage, line = duel(
                attacker["light"], 6, mod_a,
                defender["moderate"], 8, mod_d,
                f"{side_name} light vs enemy moderate",
            )
        elif defender["heavy"] > 0:
            damage, line = duel(
                attacker["light"], 6, mod_a,
                defender["heavy"] * 2, 8, mod_d,
                f"{side_name} light vs enemy heavy",
            )
        else:
            damage, line = 0, f"{side_name} light has no surface target."
        total_damage += damage
        lines.append(line)

    if attacker["moderate"] > 0:
        if defender["moderate"] > 0:
            damage, line = duel(
                attacker["moderate"], 8, mod_a,
                defender["moderate"], 8, mod_d,
                f"{side_name} moderate vs enemy moderate",
            )
        elif defender["heavy"] > 0:
            damage, line = duel(
                attacker["moderate"], 8, mod_a,
                defender["heavy"] * 2, 8, mod_d,
                f"{side_name} moderate vs enemy heavy",
            )
        else:
            damage, line = 0, f"{side_name} moderate has no surface target."
        total_damage += damage
        lines.append(line)

    if attacker["heavy"] > 0:
        if defender["heavy"] > 0:
            damage, line = duel(
                attacker["heavy"] * 2, 8, mod_a,
                defender["heavy"] * 2, 8, mod_d,
                f"{side_name} heavy vs enemy heavy",
            )
            total_damage += damage
            lines.append(line)
        else:
            if defender["light"] > 0:
                damage, line = duel(
                    attacker["heavy"] * 2, 8, mod_a,
                    defender["light"], 6, mod_d,
                    f"{side_name} heavy vs enemy light",
                )
                total_damage += damage
                lines.append(line)
            if defender["moderate"] > 0:
                damage, line = duel(
                    attacker["heavy"] * 2, 8, mod_a,
                    defender["moderate"], 8, mod_d,
                    f"{side_name} heavy vs enemy moderate",
                )
                total_damage += damage
                lines.append(line)
            if defender["light"] == 0 and defender["moderate"] == 0:
                lines.append(f"{side_name} heavy has no surface target.")

    if attacker["aircraft"] > 0:
        damage, line = duel(
            attacker["aircraft"], 3, mod_a,
            max(1, defender["aircraft"]), 3, mod_d,
            f"{side_name} carrier air strike",
        )
        total_damage += damage
        lines.append(line)
        if defender["surface"] == 0:
            lines.append("Enemy carriers are exposed because they are alone.")
        else:
            lines.append("Enemy carriers are screened by surface ships.")

    return total_damage, lines


def print_fleet(fleet):
    print(
        f"{fleet['name']}: "
        f"D={fleet['destroyers']} F={fleet['frigates']} C={fleet['corvettes']} "
        f"S={fleet['submarines']} CR={fleet['cruisers']} BB={fleet['battleships']} "
        f"CV={fleet['carriers']} AIR={fleet['aircraft']} MOD={fleet['modifier']:+d}"
    )
    print(
        f"  Totals -> Light={fleet['light']} Moderate={fleet['moderate']} "
        f"Heavy={fleet['heavy']}"
    )


def main():
    attacker = make_fleet(ATTACKER)
    defender = make_fleet(DEFENDER)

    print("Naval Fleet Dice Simulator")
    print("Edit ATTACKER and DEFENDER at the top of main.py to change ship counts.")
    print("Any ship type you leave out automatically counts as 0.\n")

    print_fleet(attacker)
    print_fleet(defender)

    attacker_damage, attacker_lines = resolve_side("Attacker", attacker, defender)
    defender_damage, defender_lines = resolve_side("Defender", defender, attacker)

    print("\nAttacker fire")
    for line in attacker_lines:
        print(f"- {line}")

    print("\nDefender fire")
    for line in defender_lines:
        print(f"- {line}")

    print("\nResult")
    print(f"{attacker['name']} deals {attacker_damage} damage.")
    print(f"{defender['name']} deals {defender_damage} damage.")

    if attacker_damage > defender_damage:
        print(f"{attacker['name']} wins the exchange.")
    elif defender_damage > attacker_damage:
        print(f"{defender['name']} wins the exchange.")
    else:
        print("The exchange is a draw.")


if __name__ == "__main__":
    main()
