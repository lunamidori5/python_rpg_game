import math
import random

from player import Player

from damagetypes import Generic

from damage_over_time import dot as damageovertimetype
from healing_over_time import hot as healingovertimetype

from colorama import Fore, Style

from themedstuff import themed_names

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

def check_passive_mod(foelist: list[Player], playerlist: list[Player], source: Player, target: Player, mited_damage_dealt: float):
        
    alllist: list[Player] = []
    
    for player in foelist:
        alllist.append(player)
    
    for player in playerlist:
        alllist.append(player)

    if themed_names[0] in source.PlayerName.lower():
        if source.Regain > 10:
            source.Regain -= 0.01
            source.DodgeOdds += 0.001
            source.MHP += 500
            source.HP += 500
            source.Atk += 50
            source.Def += 1
        
        if source.Mitigation > 1:
            source.DodgeOdds += 0.001
            source.Mitigation -= 0.001
            source.EffectHitRate += 0.01

        if themed_names[0] in target.PlayerName.lower():
            if random.random() >= 0.98:
                log(random.choice([red, green, blue]), f"{source.PlayerName} tried to hit {target.PlayerName}! {random.choice([red, green, blue])}Why would I hit myself user... {random.choice([red, green, blue])}you think I am dumb?")
            
            mited_damage_dealt = mited_damage_dealt / 4
            
            target.DodgeOdds += 0.01
        else:
            if source.HP > source.MHP * 0.25:
                hp_diff = source.HP - source.MHP * 0.25
                reduction_factor = hp_diff / (source.MHP * 0.75)
                
                scaled_reduction = reduction_factor ** 0.95 * 0.05

                source.HP -= round(source.MHP * scaled_reduction)

                mited_damage_dealt = mited_damage_dealt * (((source.MHP - source.HP) + 1) * 4)
                target.gain_damage_over_time(damageovertimetype("Bleeding Light", mited_damage_dealt ** 0.75, 100, source.Type, source.PlayerName, 2), source.EffectHitRate)
            else:
                mited_damage_dealt = mited_damage_dealt * (((source.MHP - source.HP) + 1) * 2)
                target.gain_damage_over_time(damageovertimetype("Bleeding Light", mited_damage_dealt ** 0.55, 55, source.Type, source.PlayerName, 1), source.EffectHitRate)

    if themed_names[1] in source.PlayerName.lower():
        hp_percentage = source.HP / source.MHP

        if source.DodgeOdds > 0.5:
            source.Def += source.check_base_stats(source.Def, round(source.DodgeOdds ** 2)) + round(source.DodgeOdds)
            source.DodgeOdds = 0

        for player in alllist:
            if source.isplayer == player.isplayer:
                if player.PlayerName is not source.PlayerName:
                    if player.HP < player.MHP * 0.15:
                        source.take_damage(1, source.MHP * 0.05)
                        player.heal_damage(source.deal_damage(1, Generic) * 0.025)

                    if player.Def > source.Def:
                        player.Def -= 1
                        source.Def += source.check_base_stats(source.Def, player.level)


    elif themed_names[1] in target.PlayerName.lower():
        hp_percentage = source.HP / source.MHP

        if hp_percentage < 0.75:
            damage_reduction = (1 - hp_percentage) * 0.95
            mited_damage_dealt *= (1 - damage_reduction)

        if hp_percentage < 0.55:
                    
            if len(target.DOTS) > 5:
                target.DOTS.remove(random.choice(target.DOTS))
            else:
                for dot in target.DOTS:
                    dot.damage /= 2

            mited_damage_dealt = carly_mit_adder(target, mited_damage_dealt)

        if hp_percentage < 0.25:
            mited_damage_dealt = carly_mit_adder(target, mited_damage_dealt)
            
        
    if themed_names[2] in source.PlayerName.lower():
        for player in alllist:
            if source.isplayer == player.isplayer:
                if player.PlayerName is not source.PlayerName:
                    if player.HP < source.MHP * 0.15:
                        player.heal_damage(source.Atk * 0.005)
                        player.HOTS.append(healingovertimetype("Heal", round(player.HP * 0.001), 250, player.Type, source.PlayerName, 1))
                    
                    if len(player.DOTS) > 0:
                        to_be_moved = random.choice(player.DOTS)

                        player.DOTS.remove(to_be_moved)

                        random.choice(foelist).gain_damage_over_time(to_be_moved, source.EffectHitRate)

    if themed_names[3] in source.PlayerName.lower():
        if target.MHP > source.MHP:
            source.MHP += random.randint(5, 15)
            target.MHP -= 1

    if themed_names[4] in source.PlayerName.lower():
        pass

    if themed_names[5] in source.PlayerName.lower():
        pass

    if themed_names[6] in source.PlayerName.lower():
        pass

    if themed_names[7] in source.PlayerName.lower():
        if source.HP < source.MHP * 0.85:
            mited_damage_dealt = mited_damage_dealt + ((source.MHP / 4) / (target.Def * 2))

    if themed_names[8] in source.PlayerName.lower():
        if source.Atk > 1000:
            source.Regain += 0.05
            source.Atk -= 1
        if source.Def > 1000:
            source.Regain += 0.05
            source.Def -= 1

    if themed_names[9] in source.PlayerName.lower():
        pass
    
    return max(mited_damage_dealt, 1)

def carly_mit_adder(target: Player, mited_damage_dealt: float):
    for item in target.Items:
        if not item:
            continue
        try:
            mited_damage_dealt = item.on_damage_taken(mited_damage_dealt)
        except Exception as error:
            continue
    
    return mited_damage_dealt

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

def take_damage(foelist: list[Player], playerlist: list[Player], source: Player, target: Player, mited_damage_dealt: float):
    """
    Handles a player taking damage from another player.

    Args:
        foelist (list): A list of enemy Player objects.
        playerlist (list): A list of all Player objects.
        source (Player): The Player object inflicting the damage.
        target (Player): The Player object receiving the damage.
        fight_env_list (list): A list of unchangeable outside vars to impact damage.
    """
    
    return check_passive_mod(foelist, playerlist, source, target, mited_damage_dealt)