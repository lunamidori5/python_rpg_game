import os
import sys
import pygame
import random
import threading

from screendata import Screen

from timerhelper import timmer

from damagestate import take_damage

from load_photos import set_bg_photo
from load_photos import set_bg_music
from load_photos import resource_path

from themedstuff import themed_ajt
from themedstuff import themed_names

from damagetypes import Generic

from typing import Tuple

from colorama import Fore, Style

from damage_over_time import dot as damageovertimetype
    
red = Fore.RED
green = Fore.GREEN
blue = Fore.BLUE
white = Fore.WHITE
yellow = Fore.YELLOW

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

photo_size = 128 * 3

enrage_timer = timmer()

def log(color, text):
    print(color + text + Style.RESET_ALL)
    return text

def debug_log(filename, text):
    with open(filename, "a") as f:
        f.write(f"\n{text}")
    
    return text

def kill_person(dead, killer):
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"{killer.PlayerName} killed {dead.PlayerName}, Below are stats for both...")

    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Dead Person")

    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Name: {dead.PlayerName}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Level: {dead.level}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"MHP: {dead.MHP}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"HP: {dead.HP}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Defense: {dead.Def}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Attack: {dead.Atk}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Regain: {dead.Regain}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"True Vitality: {dead.Vitality}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Crit Rate: {dead.CritRate}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Crit Damage Modifier: {dead.CritDamageMod}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Dodge Odds: {dead.DodgeOdds}")
    
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Killer")

    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Name: {killer.PlayerName}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Level: {killer.level}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"MHP: {killer.MHP}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"HP: {killer.HP}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Defense: {killer.Def}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Attack: {killer.Atk}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Regain: {killer.Regain}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"True Vitality: {killer.Vitality}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Crit Rate: {killer.CritRate}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Crit Damage Modifier: {killer.CritDamageMod}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Dodge Odds: {killer.DodgeOdds}")

def main(level):
    from player import Player
    from player import render_player_obj

    running = True
    past_level = 1
    foes_killed = 1

    starting_spawn_rate = 0.8

    last_known_player = ""
    last_known_foe = ""

    playerlist: list[Player] = []
    temp_themed_names: list[str] = []

    for item in themed_names:
        if "mimic".lower() in item.lower():
            continue
        else:
            temp_themed_names.append(item)

    player = Player("Player")

    player.load()
    player.set_photo("Player".lower())

    player.isplayer = True

    playerlist.append(player)
        
    for i in range(4):
        if random.random() < starting_spawn_rate:
            themed_name = temp_themed_names[0].capitalize()
            starting_spawn_rate /= 2
        else:
            themed_name = random.choice(temp_themed_names[1:]).capitalize()

        temp_themed_names.remove(themed_name.lower())

        player = Player(f"{themed_name.replace("_", " ")}")
        player.load()
        player.set_photo(themed_name.lower())

        player.isplayer = True

        playerlist.append(player)

    threads = []
    for player in playerlist:
        if player.level < 5:
            thread = threading.Thread(target=player.load_past_lives)
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    pygame.init()

    screen = Screen(SCREEN_WIDTH, SCREEN_HEIGHT).screen
    icon = pygame.image.load(resource_path(os.path.join("photos", f"midoriai-logo.png")))
    pygame.display.set_icon(icon)
    
    pygame.display.set_caption("Midori AI Auto Fighter", "Welcome to the fighting zone!")

    clock = pygame.time.Clock()

    font = pygame.font.SysFont('Arial', 44)

    background_file_name = set_bg_photo()
    background_image = pygame.image.load(background_file_name)
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    background_image.set_alpha(128)

    pygame.mixer.music.set_volume(0.05 / 2)
    music = pygame.mixer.music.load(set_bg_music())
    pygame.mixer.music.play(-1)  # -1 means loop the music indefinitely

    screen.fill((0, 0, 0))
    screen.blit(background_image, (0, 0))

    pygame.display.flip()

    for player in playerlist:
        player.photodata = pygame.image.load(os.path.join(player.photo))

    while True:

        level_sum = 0
        foelist: list[Player] = []

        for player in playerlist:
            player.DamageDealt = 0
            player.DamageTaken = 0

            level_sum += player.level

        level = round((level_sum + foes_killed) / (len(playerlist)))

        if level < max(round(past_level / 2) - 10, 1):
            level = random.randint(max(round(past_level / 2) - 10, 1), round(past_level / 2) + 10)
        else:
            past_level = level

        number_of_foes = 4
        foes_killed += number_of_foes

        temp_foe_themed_names: list[str] = []

        for item in themed_names:
            temp_foe_themed_names.append(item)

        if level < 2000:
            temp_foe_themed_names.remove("Luna".lower())
            temp_foe_themed_names.remove("Carly".lower())

        for i in range(number_of_foes):
            themed_name = random.choice(temp_foe_themed_names).capitalize()

            temp_foe_themed_names.remove(themed_name.lower())

            themed_title = random.choice(themed_ajt).capitalize()

            foe_pre_name = f"{themed_title} {themed_name.replace("_", " ")}"

            foe = Player(f"{foe_pre_name}")
            foe.set_photo(themed_name.lower())
            foe.set_level(random.randint(max(level - 10, 1), level + 10))

            foe.photodata = pygame.image.load(os.path.join(foe.photo))
            foe.photodata = pygame.transform.flip(foe.photodata, True, False)
            foe.photodata = pygame.transform.scale(foe.photodata, (photo_size, photo_size))

            #foe.update_inv(get_weapon(get_random_weapon()), True)

            foelist.append(foe)

        # heal the player
        player.HP = player.MHP

        enrage_timer.reset()
        enrage_timer.start()

        # Main game loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_d: 
                    for player in playerlist:
                        player.HP = -100000

            enrage_timer.check_timeout()
            
            fps = clock.get_fps()

            enrage_mod = enrage_timer.get_timeout_duration()
            level_base_enrage_mod = (level / max(level / 100, 15))
            player_base_enrage_mod = (enrage_mod * level_base_enrage_mod) / 4
            foe_base_enrage_mod = (enrage_mod * level_base_enrage_mod) / 4

            if enrage_mod > 10:
                buffed_starter = ((enrage_mod - 10) * 0.00000004) + ((enrage_mod - 5) * 0.00000002)
                bleed_mod = ((0.0000002 + buffed_starter) * (player_base_enrage_mod * foe_base_enrage_mod)) + 1
            elif enrage_mod > 5:
                buffed_starter = ((enrage_mod - 5) * 0.00000002)
                bleed_mod = ((0.0000002 + buffed_starter) * (player_base_enrage_mod * foe_base_enrage_mod)) + 1
            else:
                bleed_mod = (0.0000002 * (player_base_enrage_mod * foe_base_enrage_mod)) + 1

            def_mod = max(1, (bleed_mod * 0.0005))

            if bleed_mod > 1.2:
                def_mod = max(1, (bleed_mod * 0.002) + (bleed_mod * 0.002) + (bleed_mod * 0.001) + 1)
            
            if bleed_mod > 2:
                def_mod = max(1, (bleed_mod * 0.004) + (bleed_mod * 0.004) + (bleed_mod * 0.002) + 1)

            fps_cap = 65
            dt = clock.tick(fps_cap) / 1000
    
            # Render the screen
            screen.fill((0, 0, 0))
            screen.blit(background_image, (0, 0))

            foe_bottom = 250
            player_bottom = 625
            item_total_size = photo_size - (photo_size / 4)
            size = (item_total_size, item_total_size)

            if len(foelist) > 0:
                foe_stat_data = [
                    ("Stats of:", foelist[0].PlayerName),
                    ("Level:", foelist[0].level),
                    ("Max HP:", foelist[0].MHP),
                    ("Atk:", int(foelist[0].Atk)),
                    ("Def:", int(foelist[0].Def)),
                    ("Crit Rate:", f"{(foelist[0].CritRate * 100):.1f}%"),
                    ("Crit Damage Mod:", f"{(foelist[0].CritDamageMod):.2f}x"),
                    ("HP Regain:", f"{(foelist[0].Regain * 100):.0f}"),
                ]

                if len(foelist[0].Items) > 0:
                    foe_stat_data.append(("Blessings:", f"{len(foelist[0].Items)}"))

                if foelist[0].Vitality > 1.5:
                    foe_stat_data.append(("Vitality:", f"{(foelist[0].Vitality):.2f}x"))

                if (foelist[0].DodgeOdds * 100) / bleed_mod > 1:
                    foe_stat_data.append(("Dodge Odds:", f"{((foelist[0].DodgeOdds * 100) / bleed_mod):.2f}%"))

                # Foe stats drawing
                foe_x_offset = SCREEN_WIDTH - (SCREEN_WIDTH // 8) + 170
                foe_y_offset = (SCREEN_HEIGHT // 2) - 425 

                foe_num_stats = len(foe_stat_data)

                foe_spacing_moded = 55 - (foe_num_stats * 2)

                foe_font_size = max(16, 54 - 2 * foe_num_stats) 
                foe_stats_font = pygame.font.SysFont('Arial', foe_font_size)

                try:
                    for i, (stat_name, stat_value) in enumerate(foe_stat_data):
                        stat_text = foe_stats_font.render(f"{stat_name} {stat_value}", True, (255, 255, 255))
                        stat_rect = stat_text.get_rect(topright=(foe_x_offset, foe_y_offset + i * foe_spacing_moded))
                        screen.blit(stat_text, stat_rect)
                except Exception as error:
                    print(f"Could not render foe stats due to {str(error)}")

                for i, person in enumerate(foelist):
                    dt = clock.tick(fps_cap) / 1000
                    item_total_position = ((25 * i) + (50 + (item_total_size * i)), foe_bottom)
                    render_player_obj(pygame, person, person.photodata, screen, enrage_timer, def_mod, bleed_mod, item_total_position, size, True)

                    last_known_foe = person.PlayerName
                
                    if bleed_mod > 1.5:
                        person.RushStat = 0
                        person.take_damage(bleed_mod, person.level / 10)
                        person.gain_damage_over_time(damageovertimetype("Bleed", bleed_mod * person.level, max(10, round(1.5 ** bleed_mod)), Generic, person.PlayerName, round(1.2 * bleed_mod)), 0.2 * bleed_mod)

                    if person.HP > 1:
                        person.do_pre_turn()

                        if len(playerlist) > 0:
                            target_to_damage = random.choice(playerlist)
                            target_to_damage.take_damage(bleed_mod, take_damage(foelist, playerlist, target_to_damage, person, person.deal_damage(bleed_mod, target_to_damage.Type)))
                            
                            if target_to_damage.HP < 1:
                                target_to_damage.save_past_life()
                                kill_person(target_to_damage, person)
                                playerlist.remove(target_to_damage)
                    else:
                        foelist.remove(person)
            else:
                break

            if len(playerlist) > 0:
                for i, person in enumerate(playerlist):

                    dt = clock.tick(fps_cap) / 1000
                    item_total_position = ((25 * i) + (50 + (item_total_size * i)), player_bottom)
                    render_player_obj(pygame, person, person.photodata, screen, enrage_timer, def_mod, bleed_mod, item_total_position, size, True)

                    last_known_player = person.PlayerName
                
                    if bleed_mod > 1.5:
                        person.RushStat = 0
                        person.take_damage(bleed_mod, person.level / 10)
                        person.gain_damage_over_time(damageovertimetype("Bleed", bleed_mod * person.level, max(10, round(1.5 ** bleed_mod)), Generic, person.PlayerName, round(1.2 * bleed_mod)), 0.25 * bleed_mod)

                    if person.HP > 0:

                        person.do_pre_turn()

                        if len(foelist) > 0:
                            target_to_damage = random.choice(foelist)
                            target_to_damage.take_damage(bleed_mod, take_damage(foelist, playerlist, target_to_damage, person, person.deal_damage(bleed_mod, target_to_damage.Type)))

                            if target_to_damage.HP < 1:
                                foelist.remove(target_to_damage)
                                person.Kills += 1
                                total_rushmod = 0

                                if bleed_mod < 100:
                                    person.RushStat += 1

                                for player in playerlist:
                                    total_rushmod += max(1, player.RushStat)

                                for player in playerlist:
                                    if person.PlayerName == player.PlayerName:
                                        player.level_up(mod=bleed_mod * total_rushmod, foe_level=target_to_damage.level)
                                    else:
                                        player.level_up(mod=bleed_mod * total_rushmod, foe_level=max(5, round(target_to_damage.level*1.25)))
                                    
                                person.save()

                            elif target_to_damage.HP > target_to_damage.MHP:
                                target_to_damage.HP = target_to_damage.MHP
                    else:
                        person.save_past_life()
                        playerlist.remove(person)

                    if person.HP > person.MHP:
                        person.HP = person.MHP
            else:
                log(red, f"Your {last_known_player} at {level} kill by {last_known_foe}")
                log(red, "you lose... restart game to load a new buffed save file")
                pygame.quit()
                exit()
                
            if enrage_timer.timed_out:
                fps_stat = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
                fps_rect = fps_stat.get_rect(center=((SCREEN_WIDTH // 8) + 600, (SCREEN_HEIGHT // 2) - 400))
                screen.blit(fps_stat, fps_rect)

                enrage_timer_stat = font.render(f"Enrage: {(enrage_mod + enrage_timer.timeout_seconds):.1f} ({(bleed_mod):.2f}x)", True, (255, 255, 255))
                enrage_timer_rect = fps_stat.get_rect(center=((SCREEN_WIDTH // 8) + 600, (SCREEN_HEIGHT // 2) - 350))
                screen.blit(enrage_timer_stat, enrage_timer_rect)
            else:
                fps_stat = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
                fps_rect = fps_stat.get_rect(center=((SCREEN_WIDTH // 8) + 600, (SCREEN_HEIGHT // 2) - 400))
                screen.blit(fps_stat, fps_rect)

            pygame.display.flip()