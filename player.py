import os
import sys
import math
import uuid
import random

import pickle

from halo import Halo

from items import ItemType

from weapons import WeaponType
from weapons import get_weapon

from damage_over_time import dot as damageovertimetype
from healing_over_time import hot as healingovertimetype

from load_photos import resource_path

from themedstuff import themed_ajt
from themedstuff import themed_names

spinner = Halo(text='Loading', spinner='dots', color='green')

starting_max_blessing = 5

class Player:
    def __init__(self, name):
        """
        Initializes a new player character.
        """
        self.PlayerName: str = name
        self.level: int = 1
        self.EXP: int = 0
        self.MHP: int = 1000 * self.level
        self.HP: int = self.MHP
        self.Def: int = 25
        self.Atk: int = 250
        self.Mitigation: float = 2
        self.Regain: float = 0.02
        self.Vitality: float = 1
        self.CritRate: float = 0.03
        self.CritDamageMod: float = 2
        self.DodgeOdds: float = 0.03
        self.DamageTaken: int = 0
        self.DamageDealt: int = 0
        self.Kills: int = 0
        self.RushStat: int = 3
        self.Logs: list = []
        self.Inv: list[WeaponType] = [get_weapon('game_bit')]
        self.Items: list[ItemType] = []
        self.DOTS: list[damageovertimetype] = []
        self.HOTS: list[healingovertimetype] = []
        self.photo: str = "player.png"
        self.photodata = ""
        

    def save(self):
        temp_data = self.photodata
        self.photodata = "No Photo Data"

        lives_folder = "lives"

        if not os.path.exists(lives_folder):
            os.makedirs(lives_folder)

        with open(os.path.join(lives_folder, f'{self.PlayerName}.dat'), 'wb') as f:
            pickle.dump(self.__dict__, f)
        self.photodata = temp_data

    def load(self):
        try:

            lives_folder = "lives"

            if not os.path.exists(lives_folder):
                os.makedirs(lives_folder)

            with open(os.path.join(lives_folder, f'{self.PlayerName}.dat'), 'rb') as f:
                self.__dict__ = pickle.load(f)
        except FileNotFoundError:
            print(f"Save file for {self.PlayerName} not found. Starting new game.")
        except Exception as e:
            print(f"Error loading save file: {e}")

        self.check_stats()

    def set_photo(self, photo):
        if os.path.exists(resource_path(os.path.join("photos", f"{photo}.png"))):
            self.photo: str = resource_path(os.path.join("photos", f"{photo}.png"))
        else:
            photos = os.listdir(resource_path(os.path.join("photos", "fallbacks")))
            self.photo: str = resource_path(os.path.join(os.path.join("photos", "fallbacks"), f"{random.choice(photos)}"))

    def load_mimic(self):
        for filename in os.listdir("."):
            if ".dat" in filename.lower():
                try:
                    with open(f'{filename}', 'rb') as f:
                        self.__dict__ = pickle.load(f)
                except FileNotFoundError:
                    print(f"Save file for {filename} not found. Error...")
                except Exception as e:
                    print(f"Error loading save file: {e}")

    def load_past_lives(self):
        past_lives_folder = "past_lives"
        if not os.path.exists(past_lives_folder):
            os.makedirs(past_lives_folder)
            print("No past lives found.")
            return
        
        spinner.start(text="Past Lifes: Starting")

        past_lives_folder_list = os.listdir(past_lives_folder)
        total_items = len(past_lives_folder_list)
        random.shuffle(past_lives_folder_list)
        starting_items = 0
        for filename in past_lives_folder_list:
            if filename.endswith(".pastlife"):
                filepath = os.path.join(past_lives_folder, filename)

                starting_items += 1
        
                spinner.start(text=f"({starting_items}/{total_items}) Past Lifes ({self.PlayerName}): {filepath}")

                try:
                    with open(filepath, 'rb') as f:
                        past_life_data = pickle.load(f)

                    can_load = False

                    if self.PlayerName == past_life_data['PlayerName']:
                        can_load = True
                    elif self.PlayerName.lower() == "player":
                        can_load = True
                    
                    if can_load:
                        self.level_up()
                        self.MHP: int = self.MHP + self.check_base_stats(self.MHP, int(past_life_data['MHP'] * total_items) + 1000)
                        self.HP: int = self.MHP
                        self.Def: int = self.Def + self.check_base_stats(self.Def, int(past_life_data['Def']) + 2)
                        self.Atk: int = self.Atk + self.check_base_stats(self.Atk, int(past_life_data['Atk']) + 2)
                        self.Regain: float = self.Regain + float(past_life_data['Regain'] * 0.001) + 0.01
                        self.gain_crit_rate(float(past_life_data['CritRate'] * 0.001) + 0.01)
                        self.gain_crit_damage(float(past_life_data['CritDamageMod'] * 0.0003) + 0.001)
                        self.gain_dodgeodds_rate(float(past_life_data['DodgeOdds'] * 0.01) + 0.001)

                        for item in past_life_data['Items']:
                            self.MHP: int = self.MHP + self.check_base_stats(self.MHP, 1000)
                            self.HP: int = self.MHP
                            self.Def: int = self.Def + self.check_base_stats(self.Def, 50)
                            self.Atk: int = self.Atk + self.check_base_stats(self.Atk, 50)
                            self.Regain: float = self.Regain + (0.001)
                            self.Mitigation: float = self.Mitigation + (0.0001)
                            self.gain_crit_rate(0.01)
                            self.gain_crit_damage(0.01)
                            self.gain_dodgeodds_rate(0.001)

                        if past_life_data['Vitality'] < 0:
                            spinner.fail(text=f"Past Lifes: {filepath} failed to load (Vitality is negative. Deleting past life file.)")
                            os.remove(filepath)
                            continue

                        elif past_life_data['Vitality'] > 1.0000001:
                            temp_past_life_vitality = past_life_data['Vitality'] - 1
                            while temp_past_life_vitality > 0:
                                spinner.start(text=f"({starting_items}/{total_items}) Past Lifes ({self.PlayerName}): Granting Vitality ({temp_past_life_vitality} > {self.Vitality})")
                                
                                bonus = max(0.001, self.Vitality - 1)
                                
                                scaling_factor = 0.95
                                
                                vit_gain = (bonus * scaling_factor)
                                
                                self.gain_vit(vit_gain)

                                temp_past_life_vitality -= vit_gain
                        
                        self.check_stats()

                        if len(str(past_life_data['Logs'])) > 1:
                            past_life_data['Logs'] = ""

                            with open(filepath, 'wb') as f:
                                pickle.dump(past_life_data, f)
                    else:
                        self.MHP: int = self.MHP + self.check_base_stats(self.MHP, int(past_life_data['MHP'] * total_items) + 50)
                        self.HP: int = self.MHP
                        self.Def: int = self.Def + self.check_base_stats(self.Def, int(past_life_data['Def']) + 50)
                        self.Atk: int = self.Atk + self.check_base_stats(self.Atk, int(past_life_data['Atk']) + 100)

                except Exception as e:
                    spinner.fail(text=f"Past Lifes: {filepath} failed to load ({str(e)}. Deleting past life file.)")
                    os.remove(filepath)
                    continue
        
        spinner.succeed(text=f"Past Lifes: Fully Loaded")
                
        self.level = 1

    def save_past_life(self):
        lives_folder = "lives"
        past_lives_folder = "past_lives"
        self.photodata = "No Photo Data"

        if not os.path.exists(past_lives_folder):
            os.makedirs(past_lives_folder)

        past_life_id = str(uuid.uuid4())
        past_life_filename = os.path.join(past_lives_folder, f"{past_life_id}.pastlife")

        self.Logs = []

        try:
            with open(past_life_filename, 'wb') as f:
                pickle.dump(self.__dict__, f)
            print(f"Saved past life to {past_life_filename}")
        except Exception as e:
            print(f"Error saving past life: {e}")

        try:
            os.remove(os.path.join(lives_folder, f'{self.PlayerName}.dat'))
        except FileNotFoundError:
            pass

    def update_inv(self, item: WeaponType, add: bool):
        if add:
            self.Inv.append(item)
        else:
            self.Inv.remove(item)

    def gain_dodgeodds_rate(self, points):
        """Increases dodge odds based on points, with increasing cost.

        Every 0.5 dodge odds increase costs 5000x more points.
        """
        to_be_lowered_by = 5000
        current_rate = self.DodgeOdds

        if current_rate > 0.5:
            desired_increase = points / ((to_be_lowered_by * (current_rate // 2)) + 1)
        else:
            desired_increase = points

        self.DodgeOdds = current_rate + desired_increase

    def gain_crit_rate(self, points):
        """Increases crit rate based on points, with increasing cost.

        Every 0.05 crit rate increase costs 2500x more points.
        """
        to_be_lowered_by = 2500
        desired_increase = 0
        max_point_gain = 0.01
        temp_points = points

        while temp_points > max_point_gain:
            if self.CritRate > 1:
                desired_increase = max_point_gain / ((to_be_lowered_by * (self.CritRate // 2)) + 1)
            else:
                desired_increase = max_point_gain

            self.CritRate = self.CritRate + desired_increase

            temp_points -= max_point_gain

    def gain_crit_damage(self, points):
        """Increases crit damage based on points, with increasing cost.

        Every 10 crit damage increase costs 100x more points.
        """
        current_damage = self.CritDamageMod
        to_be_lowered_by = 100

        if current_damage > 10:
            desired_increase = points / ((to_be_lowered_by * (current_damage // 10)) + 1)
        else:
            desired_increase = points

        self.CritDamageMod += desired_increase 
    
    def check_base_stats(self, stat_total: int, stat_gain: int):
        stats_to_start_lower = 50
        to_be_lowered_by = 10 + (stat_total // 1000)

        stat_modifiers = {}

        for i in range(45):
            new_key = (i * 100)
            new_value = to_be_lowered_by ** max(0.7 * (i + 1), 1.0)
            stat_modifiers[new_key] = new_value

        stat_modifiers[stats_to_start_lower] = to_be_lowered_by

        desired_increase = stat_gain

        for item in self.Items:
            desired_increase = item.stat_gain(desired_increase)

        for threshold, modifier in stat_modifiers.items():
            if stat_total > threshold:
                desired_increase = desired_increase / max((modifier * (stat_total // stats_to_start_lower)), 1)
                break

        return max(min(int(desired_increase), 1000000), 1)
    
    def gain_vit(self, points):
        """
        Increases the player's Vitality stat based on the input points, applying diminishing returns
        and item bonuses.

        The amount of Vitality gained decreases as the player's Vitality increases,
        simulating diminishing returns.  This diminishing return is controlled by a series
        of stat modifiers that apply based on thresholds of existing Vitality. Items the player
        possesses can also affect the amount of vitality gained.

        Args:
            points (float): The base number of Vitality points to be added.  This value is modified
                           by item effects and diminishing returns.
        """
        stats_to_start_lower = 1.2
        to_be_lowered_by = (self.Vitality ** 1.5)

        stat_modifiers = {}

        for i in range(65):
            new_key = (i * 0.25)
            new_value = to_be_lowered_by ** max(0.3 * (i + 1), 1.0)
            stat_modifiers[new_key] = new_value

        stat_modifiers[stats_to_start_lower] = to_be_lowered_by

        desired_increase = points

        for item in self.Items:
            desired_increase = item.stat_gain(desired_increase)

        for threshold, modifier in stat_modifiers.items():
            if self.Vitality > threshold:
                desired_increase = max(((points) / (self.Vitality ** modifier)), 0.0000000001)
                self.Vitality += desired_increase
                break

#themed_ajt = ["atrocious", "baneful", "barbaric", "beastly", "belligerent", "bloodthirsty", "brutal", "callous", "cannibalistic", "cowardly", "cruel", "cunning", "dangerous", "demonic", "depraved", "destructive", "diabolical", "disgusting", "dishonorable", "dreadful", "eerie", "evil", "execrable", "fiendish", "filthy", "foul", "frightening", "ghastly", "ghoulish", "gruesome", "heinous", "hideous", "homicidal", "horrible", "hostile", "inhumane", "insidious", "intimidating", "malevolent", "malicious", "monstrous", "murderous", "nasty", "nefarious", "noxious", "obscene", "odious", "ominous", "pernicious", "perverted", "poisonous", "predatory", "premeditated", "primal", "primitive", "profane", "psychopathic", "rabid", "relentless", "repulsive", "ruthless", "sadistic", "savage", "scary", "sinister", "sociopathic", "spiteful", "squalid", "terrifying", "threatening", "treacherous", "ugly", "unholy", "venomous", "vicious", "villainous", "violent", "wicked", "wrongful", "xenophobic"]
#themed_names = ["luna", "carly", "becca", "ally", "hilander", "chibi", "mimic", "mezzy", "graygray", "bubbles"]

    def check_name_stats_mod(self):
        if themed_names[0] in self.PlayerName.lower():
            return random.choice([5, 6, 7, 9])

        if themed_names[1] in self.PlayerName.lower():
            return random.choice([2, 2, 2, 2, 2, 2, 2, 2, 9])
            
        if themed_names[2] in self.PlayerName.lower():
            return random.choice([1, 3, 5, 6, 9])

        if themed_names[3] in self.PlayerName.lower():
            return random.choice([1, 2, 3, 9])

        if themed_names[4] in self.PlayerName.lower():
            return random.choice([6, 6, 6, 6, 6, 6, 9])

        if themed_names[5] in self.PlayerName.lower():
            return 9

        if themed_names[6] in self.PlayerName.lower():
            return 9

        if themed_names[7] in self.PlayerName.lower():
            return random.choice([1, 9])

        if themed_names[8] in self.PlayerName.lower():
            return random.choice([4, 9])

        if themed_names[9] in self.PlayerName.lower():
            return random.choice([8, 9])
        
        return 9

    def check_name_mod(self):
        if "lady" in self.PlayerName.lower():

            if "light" in self.PlayerName.lower():
                self.Regain *= 2
                self.Mitigation += 4
                self.Vitality *= 1.5

            if "dark" in self.PlayerName.lower():
                self.Regain /= 2
                self.Mitigation /= 5
                self.Vitality *= 2.5

            self.MHP *= 10
            self.Atk *= 2
            self.Def *= 2
            self.Vitality *= 1.5

        if themed_names[0] in self.PlayerName.lower():
            dodge_buff = 0.15
            max_hp_debuff = self.MHP / 4

            while self.MHP > max_hp_debuff:
                dodge_buff = dodge_buff + (0.0000007 * self.Vitality)
                self.MHP = self.MHP - 1

            self.Atk = int(self.Atk * 1)
            self.Def = int(self.Def * 2)
            self.gain_crit_rate(0.00001 * self.level)
            self.DodgeOdds = (self.DodgeOdds + dodge_buff) * self.Vitality

        if themed_names[1] in self.PlayerName.lower():
            def_to_add = 10000

            self.MHP *= 10
            self.Mitigation *= 10

            max_hp_debuff = max(self.MHP - random.randint(5 * self.level, 15 * self.level), 10)
            max_crit_rate = self.CritRate / 100
            max_atk_stat = round(self.Atk * 0.95)
            item_buff = random.uniform(0.4, 0.9)

            while self.Vitality > max(0.2, self.Vitality / self.level):
                item_buff += random.uniform(0.01, 0.3)
                self.Vitality = self.Vitality - 0.001

            while self.MHP > max_hp_debuff:
                self.Def += self.check_base_stats(self.Def, def_to_add)
                self.MHP = self.MHP - 1

            while self.CritRate > max_crit_rate:
                self.Def += self.check_base_stats(self.Def, def_to_add)
                self.CritRate -= self.CritRate / 15

            while self.Atk > max_atk_stat:
                self.Def += self.check_base_stats(self.Def, def_to_add)
                self.Atk = self.Atk - 1

            while self.Regain > 5:
                self.Def += self.check_base_stats(self.Def, def_to_add)
                self.Regain = self.Regain - 0.001

            self.Atk = int(self.Atk) + 1
            self.Def += self.check_base_stats(self.Def, int(self.Def * self.level) + 1)

            self.gain_crit_damage((0.0002 * self.level))

            while self.Def > 25000:
                item_buff += random.uniform(0.05, 0.25)
                self.Def = self.Def - 5
            
            for item in self.Items:
                item.name = "Carly\'s Blessing of Defense"
                item.power += self.level * item_buff
            
        if themed_names[2] in self.PlayerName.lower():
            self.MHP = int(self.MHP * 15)
            self.Atk = int(self.Atk * 8)
            self.CritRate = self.CritRate / 1000

        if themed_names[3] in self.PlayerName.lower():
            self.Atk = int(self.Atk * 1.5)
            self.Def = int(self.Def * 1.5)
            self.CritDamageMod = self.CritDamageMod * ((0.005 * self.level) + 1)
            self.DodgeOdds = self.DodgeOdds / 1000

        if themed_names[4] in self.PlayerName.lower():
            self.Atk = int(self.Atk * 1.5)
            self.Def = int(self.Def * 0.5) + 1
            self.gain_crit_rate(1)
            self.CritDamageMod = self.CritDamageMod * ((0.035 * self.level) + 1)

        if themed_names[5] in self.PlayerName.lower():
            self.Vitality = self.Vitality + (0.0001 * self.level)

        if themed_names[6] in self.PlayerName.lower():
            tempname = self.PlayerName
            self.load_mimic()
            self.MHP = int(self.MHP / ((10000 / self.level) + 1))
            self.Atk = int(self.Atk / 5)
            self.Def = int(self.Def / 4)
            self.Regain = self.Regain / 5
            self.DodgeOdds = self.DodgeOdds / 4
            self.Vitality -= self.Vitality / 4

            if self.Vitality > 1:
                self.Vitality = 1

            self.PlayerName = tempname
            self.set_photo("Player".lower())

        if themed_names[7] in self.PlayerName.lower():
            self.MHP = int(self.MHP * 150)

        if themed_names[8] in self.PlayerName.lower():
            self.Regain = self.Regain * (0.05 * self.level)

        if themed_names[9] in self.PlayerName.lower():
            for item in self.Items:
                item.name = "Bubbles\'s Blessing of Damage, Defense, and Utility"
                item.power += (self.level * 0.0003)


        if themed_ajt[0] in self.PlayerName.lower(): # atrocious
            self.MHP = int(self.MHP * 1.9)
            self.Atk = int(self.Atk * 1.1)

        if themed_ajt[1] in self.PlayerName.lower(): # baneful
            self.Atk = int(self.Atk * 1.95)
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[2] in self.PlayerName.lower(): # barbaric
            self.MHP = int(self.MHP * 1.1)
            self.Def = int(self.Def * 1.9)

        if themed_ajt[3] in self.PlayerName.lower(): # beastly
            self.MHP = int(self.MHP * 1.05)
            self.Atk = int(self.Atk * 1.05)

        if themed_ajt[4] in self.PlayerName.lower(): # belligerent
            self.DodgeOdds = self.DodgeOdds * 1.9
            self.Atk = int(self.Atk * 1.1)

        if themed_ajt[5] in self.PlayerName.lower(): # bloodthirsty
            self.MHP = int(self.MHP - (self.MHP * 0.1))
            self.Atk = int(self.Atk + (self.Atk * 0.2))

        if themed_ajt[6] in self.PlayerName.lower(): # brutal
            self.CritRate = self.CritRate + 0.1
            self.DodgeOdds = self.DodgeOdds * 1.9

        if themed_ajt[7] in self.PlayerName.lower(): # callous
            self.Def = int(self.Def * 1.1)
            self.DodgeOdds = self.DodgeOdds * 1.9

        if themed_ajt[8] in self.PlayerName.lower(): # cannibalistic
            self.MHP = int(self.MHP + (self.MHP * 0.05))

        if themed_ajt[9] in self.PlayerName.lower(): # cowardly
            self.MHP = int(self.MHP * 1.2)
            self.Atk = int(self.Atk * 0.8)

        if themed_ajt[10] in self.PlayerName.lower(): # cruel
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[11] in self.PlayerName.lower(): # cunning
            self.DodgeOdds = self.DodgeOdds * 1.1

        if themed_ajt[12] in self.PlayerName.lower(): # dangerous
            self.Atk = int(self.Atk * 1.05)
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[13] in self.PlayerName.lower(): # demonic
            self.MHP = int(self.MHP * 1.9)
            self.Atk = int(self.Atk * 1.15)

        if themed_ajt[14] in self.PlayerName.lower(): # depraved
            self.Def = int(self.Def - (self.Def * 0.1))
            self.Atk = int(self.Atk + (self.Atk * 0.1))

        if themed_ajt[15] in self.PlayerName.lower(): # destructive
            self.Atk = int(self.Atk * 1.1)
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[16] in self.PlayerName.lower(): # diabolical
            self.Atk = int(self.Atk * 1.1)
            self.DodgeOdds = self.DodgeOdds * 1.9

        if themed_ajt[17] in self.PlayerName.lower(): # disgusting
            self.Def = int(self.Def * 1.9)

        if themed_ajt[18] in self.PlayerName.lower(): # dishonorable
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)

        if themed_ajt[19] in self.PlayerName.lower(): # dreadful
            self.Atk = int(self.Atk * 1.05)

        if themed_ajt[20] in self.PlayerName.lower(): # eerie
            self.DodgeOdds = self.DodgeOdds * 1.05

        if themed_ajt[21] in self.PlayerName.lower(): # evil
            self.MHP = int(self.MHP * 1.95)
            self.Atk = int(self.Atk * 1.05)

        if themed_ajt[22] in self.PlayerName.lower(): # execrable
            self.MHP = int(self.MHP * 1.9)

        if themed_ajt[23] in self.PlayerName.lower(): # fiendish
            self.DodgeOdds = self.DodgeOdds * 1.9
            self.CritRate = self.CritRate + 0.1

        if themed_ajt[24] in self.PlayerName.lower(): # filthy
            self.Def = int(self.Def * 1.95)

        if themed_ajt[25] in self.PlayerName.lower(): # foul
            self.Def = int(self.Def * 1.95)
            self.DodgeOdds = self.DodgeOdds * 1.95

        if themed_ajt[26] in self.PlayerName.lower(): # frightening
            self.Atk = int(self.Atk * 1.05)
            self.DodgeOdds = self.DodgeOdds * 1.95

        if themed_ajt[27] in self.PlayerName.lower(): # ghastly
            self.MHP = int(self.MHP * 1.95)
            self.DodgeOdds = self.DodgeOdds * 1.05

        if themed_ajt[28] in self.PlayerName.lower(): # ghoulish
            self.MHP = int(self.MHP * 1.95)
            self.Atk = int(self.Atk * 1.05)

        if themed_ajt[29] in self.PlayerName.lower(): # gruesome
            self.Atk = int(self.Atk * 1.05)
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[30] in self.PlayerName.lower(): # heinous
            self.Atk = int(self.Atk * 1.1)
            self.CritDamageMod = self.CritDamageMod * 1.1

        if themed_ajt[31] in self.PlayerName.lower(): # hideous
            self.Def = int(self.Def * 1.9)
            self.MHP = int(self.MHP * 1.1)

        if themed_ajt[32] in self.PlayerName.lower(): # homicidal
            self.Atk = int(self.Atk * 1.15)

        if themed_ajt[33] in self.PlayerName.lower(): # horrible
            self.Atk = int(self.Atk * 1.02)
            self.CritRate = self.CritRate + 0.02

        if themed_ajt[34] in self.PlayerName.lower(): # hostile
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)

        if themed_ajt[35] in self.PlayerName.lower(): # inhumane
            self.CritDamageMod = self.CritDamageMod * 1.1

        if themed_ajt[36] in self.PlayerName.lower(): # insidious
            self.Atk = int(self.Atk * 1.05)
            self.DodgeOdds = self.DodgeOdds * 1.05

        if themed_ajt[37] in self.PlayerName.lower(): # intimidating
            self.Atk = int(self.Atk * 1.95)
            self.Def = int(self.Def * 1.05)

        if themed_ajt[38] in self.PlayerName.lower(): # malevolent
            self.CritDamageMod = self.CritDamageMod * 1.05
            self.DodgeOdds = self.DodgeOdds * 1.95

        if themed_ajt[39] in self.PlayerName.lower(): # malicious
            self.Atk = int(self.Atk * 1.07)

        if themed_ajt[40] in self.PlayerName.lower(): # monstrous
            self.MHP = int(self.MHP * 1.1)
            self.Atk = int(self.Atk * 1.1)

        if themed_ajt[41] in self.PlayerName.lower(): # murderous
            self.CritRate = self.CritRate + 0.15

        if themed_ajt[42] in self.PlayerName.lower(): # nasty
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)
            self.DodgeOdds = self.DodgeOdds * 1.95

        if themed_ajt[43] in self.PlayerName.lower(): # nefarious
            self.CritRate = self.CritRate + 0.05
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[44] in self.PlayerName.lower(): # noxious
            self.Atk = int(self.Atk * 1.05)
            self.MHP = int(self.MHP * 1.95)

        if themed_ajt[45] in self.PlayerName.lower(): # obscene
            self.Def = int(self.Def * 1.9)
            self.DodgeOdds = self.DodgeOdds * 1.9

        if themed_ajt[46] in self.PlayerName.lower(): # odious
            self.Def = int(self.Def * 1.95)

        if themed_ajt[47] in self.PlayerName.lower(): # ominous
            self.CritRate = self.CritRate + 0.02
            self.CritDamageMod = self.CritDamageMod * 1.03

        if themed_ajt[48] in self.PlayerName.lower(): # pernicious
            self.MHP = int(self.MHP * 1.95)
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[49] in self.PlayerName.lower(): # perverted
            self.Def = int(self.Def * 1.9)
            self.DodgeOdds = self.DodgeOdds * 1.1

        if themed_ajt[50] in self.PlayerName.lower(): # poisonous
            self.Atk = int(self.Atk * 1.07)
            self.MHP = int(self.MHP * 1.93)

        if themed_ajt[51] in self.PlayerName.lower(): # predatory
            self.DodgeOdds = self.DodgeOdds * 1.1
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[52] in self.PlayerName.lower(): # premeditated
            self.CritRate = self.CritRate + 0.1

        if themed_ajt[53] in self.PlayerName.lower(): # primal
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)
            self.MHP = int(self.MHP * 1.05)

        if themed_ajt[54] in self.PlayerName.lower(): # primitive
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)

        if themed_ajt[55] in self.PlayerName.lower(): # profane
            self.MHP = int(self.MHP * 1.9)
            self.CritDamageMod = self.CritDamageMod * 1.1

        if themed_ajt[56] in self.PlayerName.lower(): # psychopathic
            self.DodgeOdds = self.DodgeOdds * 1.9
            self.Atk = int(self.Atk * 1.1)
            self.CritDamageMod = self.CritDamageMod * 1.1

        if themed_ajt[57] in self.PlayerName.lower(): # rabid
            self.Atk = int(self.Atk * 1.1)
            self.Def = int(self.Def * 1.9)

        if themed_ajt[58] in self.PlayerName.lower(): # relentless
            self.DodgeOdds = self.DodgeOdds * 1.9
            self.Atk = int(self.Atk * 1.05)
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[59] in self.PlayerName.lower(): # repulsive
            self.Def = int(self.Def * 1.9)
            self.DodgeOdds = self.DodgeOdds * 1.1

        if themed_ajt[60] in self.PlayerName.lower(): # ruthless
            self.CritDamageMod = self.CritDamageMod * 1.15

        if themed_ajt[61] in self.PlayerName.lower(): # sadistic
            self.Atk = int(self.Atk * 1.02)
            self.CritDamageMod = self.CritDamageMod * 1.08

        if themed_ajt[62] in self.PlayerName.lower(): # savage
            self.Atk = int(self.Atk * 1.1)
            self.Def = int(self.Def * 1.9)
            self.MHP = int(self.MHP * 1.1)

        if themed_ajt[63] in self.PlayerName.lower(): # scary
            self.Atk = int(self.Atk * 1.95)
            self.DodgeOdds = self.DodgeOdds * 1.05
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[64] in self.PlayerName.lower(): # sinister
            self.DodgeOdds = self.DodgeOdds * 1.05
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[65] in self.PlayerName.lower(): # sociopathic
            self.DodgeOdds = self.DodgeOdds * 1.9
            self.Atk = int(self.Atk * 1.15)

        if themed_ajt[66] in self.PlayerName.lower(): # spiteful
            self.Atk = int(self.Atk * 1.07)
            self.MHP = int(self.MHP * 1.93)

        if themed_ajt[67] in self.PlayerName.lower(): # squalid
            self.Def = int(self.Def * 1.95)
            self.MHP = int(self.MHP * 1.05)

        if themed_ajt[68] in self.PlayerName.lower(): # terrifying
            self.Atk = int(self.Atk * 1.9)
            self.Def = int(self.Def * 1.1)

        if themed_ajt[69] in self.PlayerName.lower(): # threatening
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)
            self.DodgeOdds = self.DodgeOdds * 1.95

        if themed_ajt[70] in self.PlayerName.lower(): # treacherous
            self.Atk = int(self.Atk * 1.05)
            self.DodgeOdds = self.DodgeOdds * 1.05
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[71] in self.PlayerName.lower(): # ugly
            self.Def = int(self.Def * 1.1)
            self.MHP = int(self.MHP * 1.9)

        if themed_ajt[72] in self.PlayerName.lower(): # unholy
            self.MHP = int(self.MHP * 5)
            self.Atk = int(self.Atk * 2)
            self.CritDamageMod = self.CritDamageMod * 0.8

        if themed_ajt[73] in self.PlayerName.lower(): # venomous
            self.Atk = int(self.Atk * 1.1)
            self.MHP = int(self.MHP * 1.9)

        if themed_ajt[74] in self.PlayerName.lower(): # vicious
            self.Atk = int(self.Atk * 1.1)
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[75] in self.PlayerName.lower(): # villainous
            self.Atk = int(self.Atk * 1.05)
            self.DodgeOdds = self.DodgeOdds * 1.95
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[76] in self.PlayerName.lower(): # violent
            self.Atk = int(self.Atk * 1.15)
            self.Def = int(self.Def * 0.85)

        if themed_ajt[77] in self.PlayerName.lower(): # wicked
            self.Atk = int(self.Atk * 1.08)
            self.CritDamageMod = self.CritDamageMod * 1.02

        if themed_ajt[78] in self.PlayerName.lower(): # wrongful
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[79] in self.PlayerName.lower(): # xenophobic
            self.Def = int(self.Def * 1.1)

    def check_stats(self):
        max_dodgeodds = 5000
        max_crit_rate = 15
        def_up = 0

        if self.DodgeOdds > (max_dodgeodds + 0.01):
            mod_number_dodge = (self.DodgeOdds - (max_dodgeodds - 0.01))
            def_up = def_up + int(mod_number_dodge)
            self.gain_crit_rate(0.0001 * mod_number_dodge)
            self.DodgeOdds = max_dodgeodds

        if self.DodgeOdds > max_dodgeodds:
            self.DodgeOdds = max_dodgeodds

        if self.CritRate > (max_crit_rate + 0.01):
            mod_number_crit = (self.CritRate - (max_crit_rate - 0.01))
            def_up = def_up + int(mod_number_crit)
            self.gain_crit_damage(0.001 * mod_number_crit)
            self.CritRate = max_crit_rate

        if self.CritRate > max_crit_rate:
            self.CritRate = max_crit_rate
        
        if def_up > 1:
            def_up = self.check_base_stats(self.Def, def_up)
            self.Def = self.Def + def_up
        
        if self.Def < 5:
            self.Def = 5

        if self.Vitality < 0.001:
            print("Warning Vitality is way too low... fixing...")
            self.Vitality = 1
        
        ### Checking for hackers
        if self.level > 50000:
            if self.Vitality == 1:
                print("Hacking games is wrong, and you should not do that ;)")
                os.remove(f'{self.PlayerName}.dat')
                exit(404)
        
        if self.MHP > 20000000000:
            self.MHP = 1
    
    def heal_damage(self, input_healing: float):
        self.HP += round(input_healing)
        if self.HP > self.MHP: self.HP = self.MHP

    def take_damage(self, input_damage: float):
        total_damage = self.damage_mitigation(input_damage)
        self.HP -= round(total_damage)
    
    def do_pre_turn(self):
        self.regain_hp()
        self.take_dot()
        self.take_hot()

    def damage_mitigation(self, damage_pre: float):
        return (damage_pre / (self.Mitigation * self.Vitality))
    
    def regain_hp(self):
        self.heal_damage(min(self.MHP, (self.Regain * self.Vitality) ** 0.90))

    def take_dot(self):
        for dot in self.DOTS:
            if dot.is_active():
                dot_damage = dot.tick()

                if dot_damage > self.MHP * 0.001 * self.Mitigation:
                    dot_damage = self.MHP * 0.001 * self.Mitigation

                for i in range(dot.tick_interval):
                    self.take_damage(dot_damage)
            else:
                self.DOTS.remove(dot)

    def take_hot(self):
        for hot in self.HOTS:
            if hot.is_active():
                hot_healing = hot.tick()
                for i in range(hot.tick_interval):
                    self.heal_damage(hot_healing)
            else:
                self.HOTS.remove(hot)
    
    def exp_to_levelup(self):
        return self.level ** 1.15

    def level_up(self, mod=float(1), foe_level=int(1)):
        """
        Levels up the player by 1 and allows the user to choose which stat to increase.
        """
        level_ups = 0
        max_level_ups = 5

        mod_fixed = ((mod * 0.35) + 1) * self.Vitality * (self.level / 1000)
        int_mod_novit = max(round(((mod * 0.85) + 1) * (self.level / 1000) * (self.level / 100)), 1)
        int_mod = max(round(mod_fixed * (self.level / 100)), 1)

        EXP_to_levelup = self.exp_to_levelup()

        if self.EXP >= EXP_to_levelup * 100:
            self.EXP += max(round(((foe_level * 2) ** 0.00025) * int_mod_novit), round((foe_level * 2) ** 0.00045)) + 1
        else:
            self.EXP += max(round(((foe_level * 4) ** 0.15) * int_mod_novit), round((foe_level * 4) ** 0.35)) + 1

        while self.EXP >= EXP_to_levelup:
            if level_ups > max_level_ups:
                break
            else:
                level_ups += 1

            self.level += 1

            self.EXP = max(self.EXP - (EXP_to_levelup), 0)
            
            hp_up: int = random.randint(5, 10 * int_mod)
            def_up: int = random.randint(2, 5 * int_mod)
            atk_up: int = random.randint(2, 5 * int_mod)
            regain_up: float = random.uniform(0.00001, 0.00002 * self.level * self.Vitality)
            critrate_up: float = random.uniform(0.001 * self.level, 0.0025 * self.level) * max((mod_fixed / 10000), 1)
            critdamage_up: float = random.uniform(0.004 * self.level, 0.008 * self.level) * max((mod_fixed / 10000), 1)
            dodgeodds_up: float = random.uniform(0.000002 * self.level, 0.00004 * self.level) * max((mod_fixed / 10000), 1)
            mitigation_up: float = (random.uniform(0.0000000001, 0.0000000002) / self.Mitigation) * max((mod_fixed / 1000000), 1)
            vitality_up: float = (random.uniform(0.00000016 * (self.level - 300), 0.00000032 * (self.level - 300)) / self.Vitality) * max((mod_fixed / 1000000), 1)

            hp_up = self.check_base_stats(self.MHP, hp_up)
            def_up = self.check_base_stats(self.Def, def_up)
            atk_up = self.check_base_stats(self.Atk, atk_up)

            if "player" in self.PlayerName.lower():
                choice = 9
            else:
                choice = self.check_name_stats_mod()

            if choice == 1:
                self.MHP += int(hp_up)
                self.HP += int(hp_up)
            elif choice == 2:
                self.Def += int(def_up)
            elif choice == 3:
                self.Atk += int(atk_up)
            elif choice == 4:
                self.Regain += regain_up
            elif choice == 5:
                self.gain_crit_rate(critrate_up)
            elif choice == 6:
                self.gain_crit_damage(critdamage_up)
            elif choice == 7:
                self.gain_dodgeodds_rate(dodgeodds_up)
            elif choice == 8:
                if len(self.Items) < starting_max_blessing:
                    self.Items.append(ItemType())
                else:
                    random.choice(self.Items).upgrade(mod_fixed * 25)
            elif choice == 9:
                if self.level > 500:
                    self.MHP += int(hp_up)
                    self.HP += int(hp_up)
                    self.Def += int(def_up)
                    self.Atk += int(atk_up)
                    self.Regain += regain_up
                    self.gain_crit_rate(critrate_up)
                    self.gain_crit_damage(critdamage_up)
                    self.gain_dodgeodds_rate(dodgeodds_up)

                    if len(self.Items) < starting_max_blessing:
                        self.Items.append(ItemType())
                    else:
                        for item in self.Items:
                            item.upgrade(mod_fixed)

                else:
                    self.MHP += int(hp_up / 2)
                    self.HP += int(hp_up / 2)
                    self.Def += int(def_up / 2)
                    self.Atk += int(atk_up / 2)
                    self.Regain += regain_up
                    self.gain_crit_rate(critrate_up)
                    self.gain_crit_damage(critdamage_up)
                    self.gain_dodgeodds_rate(dodgeodds_up)
                    
                    if len(self.Items) < starting_max_blessing:
                        self.Items.append(ItemType())
                    else:
                        for item in self.Items:
                            item.upgrade(mod_fixed)

            if self.level > 300:
                self.Mitigation += mitigation_up
                self.Vitality += vitality_up

        self.check_stats()
    
    def set_level(self, level):
        top_level = 1000
        top_level_full = top_level * 2

        self.level = level
        self.MHP: int = random.randint(2 * self.level, 5 * self.level) + 1000
        self.HP: int = self.MHP
        self.Def: int = self.Def + random.randint(int(self.MHP * (0.000000015 * self.level)), int(self.MHP * (0.000000055 * self.level))) + 500
        self.Atk: int = random.randint(2 * self.level, 3 * self.level)
        self.Regain: float = random.uniform(0.0001 * self.level, (self.level * 0.002)) + (self.level * 0.004)
        self.CritRate: float = random.uniform(0.000001 * self.level, (self.level * 0.000002)) + (self.level * 0.000001)
        self.CritDamageMod: float = 2 + (self.level * 0.00025)
        self.DodgeOdds: float = 0.03 + (self.level * 0.0001)
        self.Vitality: float = 1 + (self.level * 0.00002)
        self.Mitigation: float = 1

        if level > top_level:
            self.MHP = self.MHP + (2 * level)
            self.Atk = self.Atk + (4 * level)
            
            # Apply bonus every xyz levels past top_level
            xyz = 5
            bonus_levels = (level - top_level) // xyz
            self.MHP = self.MHP + (6 * bonus_levels)
            self.Atk = self.Atk + (2 * bonus_levels)
            self.Def = self.Def + (bonus_levels)
            self.CritRate = self.CritRate + (0.00001 * (bonus_levels * level))

            for i in range(int((level - 50) // 50) + 1):
                if len(self.Items) > starting_max_blessing:
                    random.choice(self.Items).upgrade((bonus_levels * 200) / level)
                else:
                    self.Items.append(ItemType())

        self.check_stats()
        self.check_name_mod()

        pre_temp_vit = self.Vitality
        post_temp_vit = (self.Vitality * (level / (top_level_full)))
        self.Vitality = max(post_temp_vit, 0.75)

        self.MHP = int(self.MHP * min((level / top_level), (25)) * post_temp_vit) + 5
        self.Atk = int(self.Atk * min((level / top_level), (5)) * post_temp_vit) + 5
        self.Def = int(self.Def * min((level / top_level), (2)) * post_temp_vit) + 5
        self.gain_crit_rate(0.0002 * (level / top_level_full))
        self.DodgeOdds = self.DodgeOdds * (level / (top_level_full * 5))

        if self.DodgeOdds > 0.5:
            self.DodgeOdds = 0.5

        self.check_stats()

        self.HP = self.MHP

def render_player_obj(pygame, player: Player, player_profile_pic, screen, enrage_timer, def_mod, bleed_mod, position, size, show_stats_on_hover=True):
    x, y = position
    width, height = size

    font = pygame.font.SysFont('Arial', 25)

    # Player name
    player_text = font.render(player.PlayerName, True, (255, 255, 255), (0, 0, 0, 125))
    player_rect = player_text.get_rect(topleft=(x, y))

    player_profile_pic = pygame.transform.scale(player_profile_pic, size)

    screen.blit(player_profile_pic, (player_rect.x, player_rect.y))

    screen.blit(player_text, player_rect)

    # Draw player's HP bar
    player_hp_percent = player.HP / player.MHP * 100
    player_hp_bar_offset = 25
    player_hp_bar = pygame.Rect(player_rect.x, player_rect.y + player_hp_bar_offset, player_hp_percent * (width / 100), 5)
    player_hp_bar_full = pygame.Rect(player_rect.x, player_rect.y + player_hp_bar_offset, width, 5)
    pygame.draw.rect(screen, (255, 0, 0), player_hp_bar_full)
    pygame.draw.rect(screen, (0, 255, 0), player_hp_bar)

    # Draw HP percentage
    player_hp_percent_text = font.render(f"{player_hp_percent:.2f}%", True, (255, 255, 255), (0, 0, 0))
    player_hp_percent_rect = player_hp_percent_text.get_rect(topleft=(x, y + player_hp_bar_offset + 5))
    screen.blit(player_hp_percent_text, player_hp_percent_rect)

    if player_hp_percent < 75:
        player_profile_pic.set_alpha(int(255 * (player_hp_percent / 75)))
    else:
        player_profile_pic.set_alpha(255)
        
    icon_rect = pygame.Rect(player_rect.x, player_rect.y, width, height)

    # Show stats if hover is enabled and mouse is over the icon
    mouse_pos = pygame.mouse.get_pos()
    if icon_rect.collidepoint(mouse_pos):
        stat_data = [
            ("Stats of:", player.PlayerName),
            ("Level:", player.level),
            ("EXP:", f"{round(player.EXP)}/{round(player.exp_to_levelup())}"),
            ("Max HP:", player.MHP),
            ("Atk:", int(player.Atk)),
            ("Def:", int(player.Def / def_mod)),
            ("Crit Rate / Mod:", f"{(player.CritRate * 100):.1f}% / {(player.CritDamageMod):.2f}x"),
            ("HP Regain:", f"{(player.Regain * 100):.0f}"),
        ]

        if player.Vitality > 1.01:
            stat_data.append(("Live Vitality:", f"{(player.Vitality):.2f}x"))
        elif player.Vitality != 1:
            stat_data.append(("Live Vitality:", f"{(player.Vitality):.5f}x"))

        if player.Mitigation > 1.01:
            stat_data.append(("Mitigation:", f"{(player.Mitigation):.2f}x"))

        if (player.DodgeOdds * 100) / bleed_mod > 1:
            stat_data.append(("Dodge Odds:", f"{((player.DodgeOdds * 100) / bleed_mod):.2f}%"))

        if len(player.DOTS) > 0:
            stat_data.append(("Dots:", f"{len(player.DOTS)}"))

        if len(player.HOTS) > 0:
            stat_data.append(("Hots:", f"{len(player.HOTS)}"))

        if len(player.Items) > 0:
            stat_data.append(("Blessings:", f"{len(player.Items)}"))

        x_offset = x
        y_offset = y - 275
        spacing = 25

        for i, (stat_name, stat_value) in enumerate(stat_data):
            stat_text = font.render(f"{stat_name} {stat_value}", True, (255, 255, 255), (0, 0, 0))
            stat_rect = stat_text.get_rect(topleft=(x_offset, y_offset + i * spacing))
            screen.blit(stat_text, stat_rect)

                