import sys
import pygame
import random

from weapons import get_weapon
from weapons import get_random_weapon

from timerhelper import timmer

from damagestate import take_damage

from themedstuff import themed_ajt
from themedstuff import themed_names

from typing import Tuple

from screendata import Screen

from colorama import Fore, Style

red = Fore.RED
green = Fore.GREEN
blue = Fore.BLUE
white = Fore.WHITE

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

enrage_timer = timmer()
temp_screen = Screen(SCREEN_WIDTH, SCREEN_HEIGHT)

def display_stats_menu(hp_up, def_up, atk_up, regain_up, critrate_up, critdamage_up, dodgeodds_up):
    #pygame.init()
    #screen = pygame.display.set_mode((1600, 900))
    screen = temp_screen.screen
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 25)

    # Create the menu items
    menu_items = [
        ('HP', hp_up),
        ('Def', def_up),
        ('Atk', atk_up),
        ('Unused', 0),
        ('Regain', regain_up),
        ('CritRate', critrate_up),
        ('CritDamageMod', critdamage_up),
        ('DodgeOdds', dodgeodds_up)
    ]

    # Button dimensions and spacing
    button_width = 600
    button_height = 40
    button_margin = 10

    # Create button rectangles
    buttons = []
    for i, (text, value) in enumerate(menu_items):
        button_x = 100
        button_y = 20 + (i * (button_height + button_margin))
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        buttons.append((button_rect, i + 1))  # Store button rect and corresponding value

    # Add Autopick button
    autopick_button_rect = pygame.Rect(button_x, 20 + len(menu_items) * (button_height + button_margin),
                                       button_width, button_height)

    # Handle user input
    while True:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse click
                    for button_rect, value in buttons:
                        if button_rect.collidepoint(event.pos):
                            return value
                    if autopick_button_rect.collidepoint(event.pos):
                        with open("auto.pick", 'w') as file:
                            file.write("hi")
                        return 9

        # Draw menu items and buttons
        screen.fill((0, 0, 0))  # Clear the screen

        for i, ((text, value), (button_rect, _)) in enumerate(zip(menu_items, buttons)):
            # Draw button background
            pygame.draw.rect(screen, (100, 100, 100), button_rect)

            # Draw button text
            text_surface = font.render(f'{i+1}. {text} (+{value})', True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)

        # Draw Autopick button
        pygame.draw.rect(screen, (100, 100, 100), autopick_button_rect)
        autopick_text = "Autopick"
        text_surface = font.render(autopick_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=autopick_button_rect.center)
        screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(10)

# Helper function to move an item towards a target, considering velocity
def move_towards_with_arc(current_pos, target_pos, velocity, arc_offset):
    cx, cy = current_pos
    tx, ty = target_pos
    dx, dy = tx - cx, ty - cy

    # Calculate the distance to the target
    dist = (dx**2 + dy**2) ** 0.5

    # If the item is already at the target, return the target position
    if dist == 0:
        return tx, ty

    # Calculate the step size in the x and y directions
    step_x = velocity * dx / dist
    step_y = velocity * (dy + arc_offset) / dist

    # If the item is close enough to the target, move it directly to the target
    if dist < 15:
        return tx, ty

    # Otherwise, move the item towards the target with the calculated step size
    return cx + step_x, cy + step_y


def log(color, text):
    print(color + text + Style.RESET_ALL)

def main(level):
    from player import Player
    # Initialize the game engine
    pygame.init()

    # Create the screen
    screen = temp_screen.screen

    # Create a clock
    clock = pygame.time.Clock()

    # Create a font object
    font = pygame.font.SysFont('Arial', 44)

    # Set the running flag to True
    running = True

    # Create the player and foe objects
    player = Player("Player")

    player.load()

    if player.level < 5:
        player.load_past_lives()

    while True:

        player.Bleed = 0

        if level < player.level:
            level = player.level + 1
        
        foe_pre_name = f"{random.choice(themed_ajt).capitalize()} {random.choice(themed_names).capitalize()}"

        foe = Player(f"{foe_pre_name} ({level})")
        foe.set_level(level)

        # Initialize item positions and velocity for tossing
        for item in player.Inv:
            item.position = (SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2)
            item.velocity = 0
            item.arc_offset = 0

        foe.update_inv(get_weapon(get_random_weapon()), True)

        for item in foe.Inv:
            item.position = (SCREEN_WIDTH * 5 // 6, SCREEN_HEIGHT // 2)
            item.velocity = 0
            item.arc_offset = 0

        # Index to track the current item being tossed
        player_item_index = 0
        foe_item_index = 0

        # Initialize timers for both players before the main loop
        player_toss_timer = 0
        foe_toss_timer = 0

        # heal the player
        player.HP = player.MHP

        enrage_timer.reset()
        enrage_timer.start()

        # Main game loop
        while running:
            enrage_timer.check_timeout()
            
            fps = clock.get_fps()

            enrage_mod = enrage_timer.get_timeout_duration()
            bleed_mod = (0.001 * ((enrage_mod * level) * (enrage_mod * 0.05))) + 1

            fps_cap = 5 * max(4, min(bleed_mod, 8))
            clock.tick(fps_cap)

            # Define movement speed for items (adjust this for faster/slower movement)
            toss_velocity = max(95, 5 * min(bleed_mod, 25))

            player.HP = player.HP + int((player.Regain * 100) - ((player.Bleed * bleed_mod) / player.Def))
            foe.HP = foe.HP + int(foe.Regain * 1) - int((foe.Bleed * bleed_mod) / foe.Def)

            if player.HP < 1:
                log(red, "you lose... restart game to load a new buffed save file")
                player.save_past_life()
                exit()
            elif player.HP > player.MHP:
                player.HP = player.MHP

            if foe.HP < 1:
                log(white, "saving players data")
                level = level + 1
                log(white, "The foe has leveled up")
                player.level_up(mod=bleed_mod)
                player.save()
                break
            elif foe.HP > foe.MHP:
                foe.HP = foe.MHP

            # Update toss timers
            player_toss_timer = 1
            foe_toss_timer = 1

            # Toss one item from the player to the foe every 1 second
            if player_toss_timer >= 1:
                if player_item_index >= len(player.Inv):
                    player_item_index = 0  # Loop over items

                current_item = player.Inv[player_item_index]
                if current_item.velocity == 0:
                    # Set initial velocity and a random arc offset
                    current_item.velocity = toss_velocity
                    current_item.arc_offset = random.randint(-15, 15)  # Random arc up or down

                end_pos = (SCREEN_WIDTH * 5 // 6, SCREEN_HEIGHT // 2)
                current_item.position = move_towards_with_arc(current_item.position, end_pos, current_item.velocity, current_item.arc_offset)

                # Check if the item has reached the foe's text
                foe_rect = font.render(foe.PlayerName, True, (255, 255, 255)).get_rect(center=(SCREEN_WIDTH * 5 // 6, SCREEN_HEIGHT // 2))
                if foe_rect.collidepoint(current_item.position):
                    take_damage(player, foe, [bleed_mod, enrage_timer, current_item])

                    current_item.velocity = 0  # Reset velocity after hit
                    current_item.position = (SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2)
                    player_item_index += 1  # Move to the next itemc

                # Reset the toss timer after an item is tossed
                del current_item
                player_toss_timer = 0


            # Toss one item from the foe to the player every 1 second
            if foe_toss_timer >= 1:
                if foe_item_index >= len(foe.Inv):
                    foe_item_index = 0  # Loop over items

                current_item = foe.Inv[foe_item_index]
                if current_item.velocity == 0:
                    # Set initial velocity and a random arc offset
                    current_item.velocity = toss_velocity
                    current_item.arc_offset = random.randint(-15, 15)  # Random arc up or down

                end_pos = (SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2)
                current_item.position = move_towards_with_arc(current_item.position, end_pos, current_item.velocity, current_item.arc_offset)

                # Check if the item has reached the player's text
                player_rect = font.render(player.PlayerName, True, (255, 255, 255)).get_rect(center=(SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2))
                if player_rect.collidepoint(current_item.position):
                    take_damage(foe, player, [bleed_mod, enrage_timer, current_item])

                    current_item.velocity = 0  # Reset velocity after hit
                    current_item.position = (SCREEN_WIDTH * 5 // 6, SCREEN_HEIGHT // 2)
                    foe_item_index += 1  # Move to the next item

                # Reset the toss timer after an item is tossed
                del current_item
                foe_toss_timer = 0


            # Render the screen            
            screen.fill((0, 0, 0))

            # Draw the player's name
            player_offset = 80
            player_hp_bar_offset = player_offset - 50
            player_text = font.render(player.PlayerName, True, (255, 255, 255))
            player_rect = player_text.get_rect(center=((SCREEN_WIDTH // 6) - player_offset, SCREEN_HEIGHT // 2))
            screen.blit(player_text, player_rect)

            # Draw the player's HP bar
            player_hp_percent = player.HP / player.MHP * 100
            player_hp_bar = pygame.Rect(player_rect.x - player_hp_bar_offset, player_rect.y + 60, player_hp_percent * 4, 5)
            player_hp_bar_full = pygame.Rect(player_rect.x - player_hp_bar_offset, player_rect.y + 60, 100 * 4, 5)
            player_hp_percent_text = font.render(f"{player_hp_percent:.2f}%", True, (255, 255, 255))
            player_hp_percent_rect = player_hp_percent_text.get_rect(center=((SCREEN_WIDTH // 6) - player_offset, (SCREEN_HEIGHT // 2) + 60))
            pygame.draw.rect(screen, (0, 255, 0), player_hp_bar)
            pygame.draw.rect(screen, (255, 0, 0), player_hp_bar_full)
            screen.blit(player_hp_percent_text, player_hp_percent_rect)

            hp_stat = font.render(f"Max HP: {player.MHP}", True, (255, 255, 255))
            def_stat = font.render(f"Def: {player.Def}", True, (255, 255, 255))
            atk_stat = font.render(f"Atk: {player.Atk}", True, (255, 255, 255))
            regain_stat = font.render(f"HP Regain: {(player.Regain * 100):.2f}", True, (255, 255, 255))
            critrate_stat = font.render(f"Crit Rate: {(player.CritRate * 100):.2f}%", True, (255, 255, 255))
            critdamage_stat = font.render(f"Crit Damage Mod: {(player.CritDamageMod * 100):.2f}%", True, (255, 255, 255))
            dodge_stat = font.render(f"Dodge Odds: {(player.DodgeOdds * 100):.2f}%", True, (255, 255, 255))

            hp_rect = hp_stat.get_rect(center=((SCREEN_WIDTH // 6), (SCREEN_HEIGHT // 2) - 400))
            def_rect = def_stat.get_rect(center=((SCREEN_WIDTH // 6), (SCREEN_HEIGHT // 2) - 350))
            atk_rect = atk_stat.get_rect(center=((SCREEN_WIDTH // 6), (SCREEN_HEIGHT // 2) - 300))
            critrate_rect = critrate_stat.get_rect(center=((SCREEN_WIDTH // 6), (SCREEN_HEIGHT // 2) - 250))
            critdamage_rect = critdamage_stat.get_rect(center=((SCREEN_WIDTH // 6) + 600, (SCREEN_HEIGHT // 2) - 400))
            regain_rect = regain_stat.get_rect(center=((SCREEN_WIDTH // 6) + 600, (SCREEN_HEIGHT // 2) - 350))
            dodge_rect = dodge_stat.get_rect(center=((SCREEN_WIDTH // 6) + 600, (SCREEN_HEIGHT // 2) - 300))

            if enrage_timer.timed_out:
                enrage_stat = font.render(f"Enrage Buff: {(bleed_mod):.2f}x", True, (255, 255, 255))
                enrage_rect = enrage_stat.get_rect(center=((SCREEN_WIDTH // 6) + 600, (SCREEN_HEIGHT // 2) - 250))
                screen.blit(enrage_stat, enrage_rect)
                
            fps_stat = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
            fps_rect = fps_stat.get_rect(center=((SCREEN_WIDTH // 6) + 1200, (SCREEN_HEIGHT // 2) - 400))
            screen.blit(fps_stat, fps_rect)

            screen.blit(hp_stat, hp_rect)
            screen.blit(def_stat, def_rect)
            screen.blit(atk_stat, atk_rect)
            screen.blit(regain_stat, regain_rect)
            screen.blit(critrate_stat, critrate_rect)
            screen.blit(critdamage_stat, critdamage_rect)
            screen.blit(dodge_stat, dodge_rect)

            # Draw the foe's name
            foe_text = font.render(foe.PlayerName, True, (255, 255, 255))
            foe_rect = foe_text.get_rect(center=(SCREEN_WIDTH * 5 // 6, SCREEN_HEIGHT // 2))
            screen.blit(foe_text, foe_rect)

            # Draw the foe's HP bar
            foe_hp_percent = foe.HP / foe.MHP * 100
            foe_hp_bar = pygame.Rect(foe_rect.x, foe_rect.y + 60, foe_hp_percent * 2, 5)
            foe_hp_text = font.render(f"{int(foe.HP)}/{int(foe.MHP)}", True, (255, 255, 255))
            foe_hp_rect = foe_hp_text.get_rect(center=(SCREEN_WIDTH * 5 // 6, (SCREEN_HEIGHT // 2) + 60))
            pygame.draw.rect(screen, (255, 0, 0), foe_hp_bar)
            screen.blit(foe_hp_text, foe_hp_rect)

            # Draw the current tossed items
            if player_item_index < len(player.Inv):
                current_item = player.Inv[player_item_index]
                item_text = font.render(current_item.game_obj, True, (255, 255, 255))
                item_rect = item_text.get_rect(center=current_item.position)
                screen.blit(item_text, item_rect)

            if foe_item_index < len(foe.Inv):
                current_item = foe.Inv[foe_item_index]
                item_text = font.render(current_item.game_obj, True, (255, 255, 255))
                item_rect = item_text.get_rect(center=current_item.position)
                screen.blit(item_text, item_rect)

            # Flip the display
            pygame.display.flip()