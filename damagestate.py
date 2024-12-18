import random

from player import Player

from colorama import Fore, Style

red = Fore.RED
green = Fore.GREEN
blue = Fore.BLUE
white = Fore.WHITE

def log(color, text):
    print(color + text + Style.RESET_ALL)
    return text

def debug_log(text):
    with open("debug_log.txt", "a") as f:
        f.write(f"\n{text}")
    
    return text

def apply_damage_item_effects(source: Player, target: Player, mited_damage_dealt: float):
        
        for item in source.Items:
            if not item:
                continue
            try:
                before_damage = mited_damage_dealt
                mited_damage_dealt = item.on_damage_dealt(mited_damage_dealt)
                source.DamageDealt += int(mited_damage_dealt)
                # log(white, f"Damage Buff effect from {source.PlayerName}: {item.name}, Item Power: {item.power}, Damage Diff: {mited_damage_dealt - before_damage}")
            except Exception as error:
                continue

        for item in target.Items:
            if not item:
                continue
            try:
                before_damage = mited_damage_dealt
                mited_damage_dealt = item.on_damage_taken(mited_damage_dealt)
                target.DamageTaken += int(mited_damage_dealt)
                # log(white, f"Damage Mit effect from {target.PlayerName}: {item.name}, Item Power: {item.power}, Damage Diff: {mited_damage_dealt - before_damage}")
            except Exception as error:
                continue

        return mited_damage_dealt

def take_damage(source: Player, target: Player, fight_env_list: list, def_mod: float):
    """
    Handles a player taking damage from another player.

    Args:
        source (Player): The Player object inflicting the damage.
        target (Player): The Player object receiving the damage.
        fight_env_list (List): A list of unchangeable outside vars to inpact damage.
    """

    enrage_buff = fight_env_list[0]
    enrage_timer = fight_env_list[1]

    if (target.DodgeOdds / enrage_buff) >= random.random():
        text_to_log = log(green, f"{target.PlayerName} dodged!")
    else:
        mited_damage_dealt = float(0)
        source_vit = max((source.Vitality / def_mod) ** 4, 0.005)
        target_vit = max((target.Vitality / def_mod) ** 4, 0.005)
        def_val = ((target.Def / def_mod) ** 2)
        damage_dealt = ((1 * (source.Atk * source_vit)) * 2)
        # text_to_log = log(white, f"pre mitigated dmg: {damage_dealt}, target Vit: {target_vit}, source Vit: {source_vit}, target def: {def_val}")

        if source.CritRate >= random.random():
            damage_dealt = apply_damage_item_effects(source, target, damage_dealt * (enrage_buff * (source.CritDamageMod * max(1, source.CritRate)) * def_mod))
            mited_damage_dealt = float(damage_dealt / max(def_val * target_vit, 2))
            mited_damage_dealt = mited_damage_dealt * random.uniform(0.95, 1.05)
            

            if enrage_timer.timed_out:
                text_to_log = log(blue, f"Crit! {source.PlayerName} crits {target.PlayerName} for {mited_damage_dealt:.2f} damage! Enraged")
            else:
                text_to_log = log(blue, f"Crit! {source.PlayerName} crits {target.PlayerName} for {mited_damage_dealt:.2f} damage!")
        else:
            damage_dealt = apply_damage_item_effects(source, target, damage_dealt * (enrage_buff * def_mod))
            mited_damage_dealt = float(damage_dealt / max(def_val * target_vit, 2))
            mited_damage_dealt = mited_damage_dealt * random.uniform(0.95, 1.05)
            
            if enrage_timer.timed_out:
                text_to_log = log(red, f"Hit! {source.PlayerName} hits {target.PlayerName} for {mited_damage_dealt:.2f} damage! Enraged")
            else:
                text_to_log = log(red, f"Hit! {source.PlayerName} hits {target.PlayerName} for {mited_damage_dealt:.2f} damage!")

        if mited_damage_dealt > target.HP:
            mited_damage_dealt = target.HP + 1000

        target.HP -= int(max(mited_damage_dealt, 1))
    
        if enrage_buff > 10:
            target.Bleed += max(mited_damage_dealt / target.MHP, 0.01)