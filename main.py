from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass
class Fleet:
    name: str
    destroyers: int = 0
    frigates: int = 0
    corvettes: int = 0
    submarines: int = 0
    cruisers: int = 0
    battleships: int = 0
    carriers: int = 0
    aircraft: int = 0
    modifier: int = 0

    @property
    def light(self) -> int:
        return self.destroyers + self.frigates + self.corvettes + self.submarines

    @property
    def moderate(self) -> int:
        return self.cruisers

    @property
    def heavy(self) -> int:
        return self.battleships

    @property
    def carrier_air_wings(self) -> int:
        # Carriers are support platforms. Each aircraft bought adds a 1d3 strike.
        return self.aircraft

    def has_surface_ships(self) -> bool:
        return self.light > 0 or self.moderate > 0 or self.heavy > 0


def roll_die(sides: int) -> int:
    return random.randint(1, sides)


def roll_pool(count: int, sides: int, modifier: int) -> tuple[int, list[int]]:
    rolls = [roll_die(sides) + modifier for _ in range(count)]
    return sum(rolls), rolls


def format_rolls(rolls: list[int], sides: int, modifier: int) -> str:
    if not rolls:
        return "0"
    mod_text = f"{modifier:+d}" if modifier else ""
    return f"{len(rolls)}d{sides}{mod_text} -> {rolls} = {sum(rolls)}"


def resolve_band(
    attackers: int,
    attacker_sides: int,
    attacker_modifier: int,
    defenders: int,
    defender_sides: int,
    defender_modifier: int,
    label: str,
) -> tuple[int, str]:
    attack_total, attack_rolls = roll_pool(attackers, attacker_sides, attacker_modifier)
    defense_total, defense_rolls = roll_pool(defenders, defender_sides, defender_modifier)
    damage = max(0, attack_total - defense_total)
    text = (
        f"{label}: attack {format_rolls(attack_rolls, attacker_sides, attacker_modifier)} "
        f"vs defense {format_rolls(defense_rolls, defender_sides, defender_modifier)} "
        f"=> damage {damage}"
    )
    return damage, text


def carrier_can_be_targeted(target: Fleet) -> bool:
    return not target.has_surface_ships()


def resolve_battle(attacker: Fleet, defender: Fleet) -> dict:
    attacker_lines: list[str] = []
    defender_lines: list[str] = []
    attacker_damage = 0
    defender_damage = 0

    # Light vs Light, else Light spills upward into Moderate, else into Heavy.
    if attacker.light > 0:
        if defender.light > 0:
            damage, text = resolve_band(
                attacker.light, 6, attacker.modifier,
                defender.light, 6, defender.modifier,
                "Attacker light vs Defender light",
            )
        elif defender.moderate > 0:
            damage, text = resolve_band(
                attacker.light, 6, attacker.modifier,
                defender.moderate, 8, defender.modifier,
                "Attacker light vs Defender moderate",
            )
        elif defender.heavy > 0:
            damage, text = resolve_band(
                attacker.light, 6, attacker.modifier,
                defender.heavy * 2, 8, defender.modifier,
                "Attacker light vs Defender heavy",
            )
        else:
            damage, text = (0, "Attacker light has no eligible surface target.")
        attacker_damage += damage
        attacker_lines.append(text)

    # Moderate vs Moderate, else spills upward into Heavy.
    if attacker.moderate > 0:
        if defender.moderate > 0:
            damage, text = resolve_band(
                attacker.moderate, 8, attacker.modifier,
                defender.moderate, 8, defender.modifier,
                "Attacker moderate vs Defender moderate",
            )
        elif defender.heavy > 0:
            damage, text = resolve_band(
                attacker.moderate, 8, attacker.modifier,
                defender.heavy * 2, 8, defender.modifier,
                "Attacker moderate vs Defender heavy",
            )
        else:
            damage, text = (0, "Attacker moderate has no eligible surface target.")
        attacker_damage += damage
        attacker_lines.append(text)

    # Heavy can engage Heavy, or if no enemy heavy then split against Light and Moderate.
    if attacker.heavy > 0:
        if defender.heavy > 0:
            damage, text = resolve_band(
                attacker.heavy * 2, 8, attacker.modifier,
                defender.heavy * 2, 8, defender.modifier,
                "Attacker heavy vs Defender heavy",
            )
            attacker_damage += damage
            attacker_lines.append(text)
        else:
            if defender.light > 0:
                damage, text = resolve_band(
                    attacker.heavy * 2, 8, attacker.modifier,
                    defender.light, 6, defender.modifier,
                    "Attacker heavy vs Defender light",
                )
                attacker_damage += damage
                attacker_lines.append(text)
            if defender.moderate > 0:
                damage, text = resolve_band(
                    attacker.heavy * 2, 8, attacker.modifier,
                    defender.moderate, 8, defender.modifier,
                    "Attacker heavy vs Defender moderate",
                )
                attacker_damage += damage
                attacker_lines.append(text)
            if defender.light == 0 and defender.moderate == 0:
                attacker_lines.append("Attacker heavy has no eligible surface target.")

    # Carriers add support and can strike carriers too. They can only be engaged if alone.
    if attacker.carrier_air_wings > 0:
        damage, text = resolve_band(
            attacker.carrier_air_wings, 3, attacker.modifier,
            max(1, defender.carrier_air_wings), 3, defender.modifier,
            "Attacker carrier air wing strike",
        )
        attacker_damage += damage
        attacker_lines.append(text)
        if carrier_can_be_targeted(defender):
            attacker_lines.append("Defender carriers are exposed because no surface ships remain in the fleet.")
        else:
            attacker_lines.append("Defender carriers stay screened behind surface ships.")

    # Defender attacks back simultaneously.
    if defender.light > 0:
        if attacker.light > 0:
            damage, text = resolve_band(
                defender.light, 6, defender.modifier,
                attacker.light, 6, attacker.modifier,
                "Defender light vs Attacker light",
            )
        elif attacker.moderate > 0:
            damage, text = resolve_band(
                defender.light, 6, defender.modifier,
                attacker.moderate, 8, attacker.modifier,
                "Defender light vs Attacker moderate",
            )
        elif attacker.heavy > 0:
            damage, text = resolve_band(
                defender.light, 6, defender.modifier,
                attacker.heavy * 2, 8, attacker.modifier,
                "Defender light vs Attacker heavy",
            )
        else:
            damage, text = (0, "Defender light has no eligible surface target.")
        defender_damage += damage
        defender_lines.append(text)

    if defender.moderate > 0:
        if attacker.moderate > 0:
            damage, text = resolve_band(
                defender.moderate, 8, defender.modifier,
                attacker.moderate, 8, attacker.modifier,
                "Defender moderate vs Attacker moderate",
            )
        elif attacker.heavy > 0:
            damage, text = resolve_band(
                defender.moderate, 8, defender.modifier,
                attacker.heavy * 2, 8, attacker.modifier,
                "Defender moderate vs Attacker heavy",
            )
        else:
            damage, text = (0, "Defender moderate has no eligible surface target.")
        defender_damage += damage
        defender_lines.append(text)

    if defender.heavy > 0:
        if attacker.heavy > 0:
            damage, text = resolve_band(
                defender.heavy * 2, 8, defender.modifier,
                attacker.heavy * 2, 8, attacker.modifier,
                "Defender heavy vs Attacker heavy",
            )
            defender_damage += damage
            defender_lines.append(text)
        else:
            if attacker.light > 0:
                damage, text = resolve_band(
                    defender.heavy * 2, 8, defender.modifier,
                    attacker.light, 6, attacker.modifier,
                    "Defender heavy vs Attacker light",
                )
                defender_damage += damage
                defender_lines.append(text)
            if attacker.moderate > 0:
                damage, text = resolve_band(
                    defender.heavy * 2, 8, defender.modifier,
                    attacker.moderate, 8, attacker.modifier,
                    "Defender heavy vs Attacker moderate",
                )
                defender_damage += damage
                defender_lines.append(text)
            if attacker.light == 0 and attacker.moderate == 0:
                defender_lines.append("Defender heavy has no eligible surface target.")

    if defender.carrier_air_wings > 0:
        damage, text = resolve_band(
            defender.carrier_air_wings, 3, defender.modifier,
            max(1, attacker.carrier_air_wings), 3, attacker.modifier,
            "Defender carrier air wing strike",
        )
        defender_damage += damage
        defender_lines.append(text)
        if carrier_can_be_targeted(attacker):
            defender_lines.append("Attacker carriers are exposed because no surface ships remain in the fleet.")
        else:
            defender_lines.append("Attacker carriers stay screened behind surface ships.")

    return {
        "attacker_damage": attacker_damage,
        "defender_damage": defender_damage,
        "attacker_lines": attacker_lines,
        "defender_lines": defender_lines,
    }


def prompt_int(label: str) -> int:
    while True:
        try:
            raw = input(f"{label}: ").strip()
        except EOFError as exc:
            raise SystemExit("\nInput ended before fleet setup was complete.") from exc
        try:
            value = int(raw)
        except ValueError:
            print("Enter a whole number.")
            continue
        if value < 0:
            print("Use 0 or a positive number.")
            continue
        return value


def build_fleet(name: str) -> Fleet:
    print(f"\n{name} fleet setup")
    return Fleet(
        name=name,
        destroyers=prompt_int("Destroyers"),
        frigates=prompt_int("Frigates"),
        corvettes=prompt_int("Corvettes"),
        submarines=prompt_int("Submarines"),
        cruisers=prompt_int("Cruisers"),
        battleships=prompt_int("Battleships"),
        carriers=prompt_int("Aircraft carriers"),
        aircraft=prompt_int("Aircraft wings"),
        modifier=prompt_int("Per-ship modifier (+0, +1, +2, etc.)"),
    )


def describe_fleet(fleet: Fleet) -> str:
    return (
        f"{fleet.name}: L={fleet.light} (D:{fleet.destroyers} F:{fleet.frigates} "
        f"C:{fleet.corvettes} S:{fleet.submarines}), M={fleet.moderate}, "
        f"H={fleet.heavy}, Carriers={fleet.carriers}, Aircraft={fleet.aircraft}, "
        f"Modifier={fleet.modifier:+d}"
    )


def main() -> None:
    print("Naval Fleet Dice Simulator")
    print("Light ships use d6, cruisers use d8, battleships use 2d8, aircraft use d3.")
    print("Submarines count as light ships. Carrier aircraft stack by aircraft wings bought.")

    attacker = build_fleet("Attacker")
    defender = build_fleet("Defender")

    print("\nFleet summary")
    print(describe_fleet(attacker))
    print(describe_fleet(defender))

    result = resolve_battle(attacker, defender)

    print("\nAttacker fire plan")
    for line in result["attacker_lines"]:
        print(f"- {line}")

    print("\nDefender fire plan")
    for line in result["defender_lines"]:
        print(f"- {line}")

    print("\nBattle result")
    print(f"{attacker.name} deals {result['attacker_damage']} total damage.")
    print(f"{defender.name} deals {result['defender_damage']} total damage.")
    if result["attacker_damage"] > result["defender_damage"]:
        print(f"{attacker.name} wins the exchange.")
    elif result["defender_damage"] > result["attacker_damage"]:
        print(f"{defender.name} wins the exchange.")
    else:
        print("The exchange is a draw.")


if __name__ == "__main__":
    main()
