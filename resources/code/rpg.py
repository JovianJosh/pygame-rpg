import pygame
import random
import pickle
import button
import os
import sys

pygame.init()

clock = pygame.time.Clock()
fps = 60

# Game window
bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Battle')

# Define game variables
action_cooldown = 0
action_wait_time = 90
attack = False
clicked = False
game_over = 0
stage = 0
wins = 0


# Define fonts
font = pygame.font.SysFont('Times New Roman', 26)
font_2 = pygame.font.SysFont('Times New Roman', 20)

# Define colours
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
white = (255, 255, 255)
yellow = (255, 205, 0)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Load images
background_img = pygame.image.load(resource_path('img/Background/background.png')).convert_alpha()
panel_img = pygame.image.load(resource_path('img/Icons/panel.png')).convert_alpha()
potion_img = pygame.image.load(resource_path('img/Icons/potion.png')).convert_alpha()
restart_img = pygame.image.load(resource_path('img/Icons/restart.png')).convert_alpha()
victory_img = pygame.image.load(resource_path('img/Icons/victory.png')).convert_alpha()
defeat_img = pygame.image.load(resource_path('img/Icons/defeat.png')).convert_alpha()
sword_img = pygame.image.load(resource_path('img/Icons/sword.png')).convert_alpha()

# Function for drawing text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function for drawing background
def draw_bg():
    screen.blit(background_img, (0, 0))

# Function for drawing panel
def draw_panel():
    screen.blit(panel_img, (0, screen_height - bottom_panel))
    draw_text(f'{hero.name} HP: {hero.hp}', font, red, 100, screen_height - bottom_panel + 10)
    draw_text(f'Level: {hero.level}', font_2, blue, 100, screen_height - bottom_panel + 60)
    draw_text(f'XP: {hero.xp}/{hero.xp_to_next_level}', font_2, green, 100, screen_height - bottom_panel + 90)
    draw_text(f'Gold: {hero.gold}', font_2, yellow, 100, screen_height - bottom_panel + 120)
    draw_text(f'Str: {hero.strength}', font_2, red, 270, screen_height - bottom_panel + 10)
    draw_text(f'Max HP: {hero.max_hp}', font_2, green, 270, screen_height - bottom_panel +40)
    draw_text(f'Agi: {hero.attack_speed}ms', font_2, blue, 270, screen_height - bottom_panel +70)
    draw_text(f'Crit: {hero.cr}', font_2, yellow, 270, screen_height - bottom_panel +100)
    draw_text(f'Stage: {stage}', font, yellow, 20, screen_height - bottom_panel + 10)
    
    for count, bandit in enumerate(bandit_list):
        draw_text(f'{bandit.name} HP: {bandit.hp}', font, red, 550, (screen_height - bottom_panel + 10) + count * 60)

# Function for showing allocate stats window
def show_allocate_stats_window():
    window_width = 300
    window_height = 200
    window_x = (screen_width - window_width) // 2
    window_y = (screen_height - window_height) // 2
    pygame.draw.rect(screen, black, (window_x, window_y, window_width, window_height))
    pygame.draw.rect(screen, white, (window_x + 5, window_y + 5, window_width - 10, window_height - 10))
    draw_text('Allocate Stats Points', font, black, window_x + 50, window_y + 10)
    draw_text('Press 1: Strength + 5', font_2, red, window_x + 20, window_y + 50)
    draw_text('Press 2: Max HP + 20', font_2, green, window_x + 20, window_y + 80)
    draw_text('Press 3: Attack Speed + 80', font_2, blue, window_x + 20, window_y + 110)
    draw_text('Press 4: Crit Rate + 5', font_2, yellow, window_x + 20, window_y + 140)
    draw_text(f'Stats Points: {hero.stats_points}', font_2, black, window_x + 20, window_y + 170)

def save_game():
    data = {
        'hero': {
            'hp': hero.hp,
            'max_hp': hero.max_hp,
            'strength': hero.strength,
            'level': hero.level,
            'xp': hero.xp,
            'xp_to_next_level': hero.xp_to_next_level,
            'gold': hero.gold,
            'skill_points': hero.skill_points,
            'stats_points': hero.stats_points,
        },
        'bandits': [
            {'hp': bandit.hp, 'alive': bandit.alive} for bandit in bandit_list
        ],
        'skills': [
            {'name': skill.name, 'level': skill.level, 'cost_per_level': skill.cost_per_level}
            for skill in owned_skills
        ],
        'equipped_skills': [
            skill.name if skill else None for skill in equipped_skills
        ],
        'stage': stage  # Save the current stage count
    }
    with open('savegame.pkl', 'wb') as f:
        pickle.dump(data, f)

def load_game():
    global hero, bandit_list, owned_skills, equipped_skills, stage
    try:
        with open('savegame.pkl', 'rb') as f:
            data = pickle.load(f)
            hero.hp = data['hero'].get('hp', hero.hp)
            hero.max_hp = data['hero'].get('max_hp', hero.max_hp)
            hero.strength = data['hero'].get('strength', hero.strength)
            hero.level = data['hero'].get('level', hero.level)
            hero.xp = data['hero'].get('xp', hero.xp)
            hero.xp_to_next_level = data['hero'].get('xp_to_next_level', hero.xp_to_next_level)
            hero.gold = data['hero'].get('gold', hero.gold)
            hero.skill_points = data['hero'].get('skill_points', hero.skill_points)
            hero.stats_points = data['hero'].get('stats_points', hero.stats_points)

            # Restore bandits
            for bandit, saved_bandit in zip(bandit_list, data.get('bandits', [])):
                bandit.hp = saved_bandit.get('hp', bandit.hp)
                bandit.alive = saved_bandit.get('alive', bandit.alive)

            # Restore skills
            for skill, saved_skill in zip(owned_skills, data.get('skills', [])):
                skill.level = saved_skill.get('level', skill.level)
                skill.cost_per_level = saved_skill.get('cost_per_level', skill.cost_per_level)

            # Restore equipped skills
            equipped_skill_names = data.get('equipped_skills', [None, None])
            equipped_skills = [
                next((skill for skill in owned_skills if skill.name == skill_name), None)
                for skill_name in equipped_skill_names
            ]

            # Restore stage
            stage = data.get('stage', stage)
    except FileNotFoundError:
        print("No saved game found. Starting a new game.")



# Fighter class
class Fighter():
    def __init__(self, x, y, name, max_hp, strength, potions, attack_speed):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.cr = 25
        self.cd = 150
        self.attack_speed = attack_speed
        self.last_attack_time = pygame.time.get_ticks()
        self.gold = 0
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.skill_points = 0
        self.stats_points = 0
        self.update_time = pygame.time.get_ticks()
        temp_list = []
        for i in range(8):
            img = pygame.image.load(resource_path(f'img/{self.name}/Idle/{i}.png'))
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(8):
            img = pygame.image.load(resource_path(f'img/{self.name}/Attack/{i}.png'))
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(3):
            img = pygame.image.load(resource_path(f'img/{self.name}/Hurt/{i}.png'))
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(10):
            img = pygame.image.load(resource_path(f'img/{self.name}/Death/{i}.png'))
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.initial_max_hp = max_hp
        self.initial_strength = strength
        self.initial_attack_speed = attack_speed
        self.initial_cr = 25
        self.initial_cd = 150

    def reset(self, is_new_game=False):
        self.alive = True
        if is_new_game:
            self.frame_index = 0
            self.action = 0
            self.update_time = pygame.time.get_ticks()
            self.level = 1
            self.xp = 0
            self.xp_to_next_level = 100
            self.gold = 0  
            self.skill_points = 0
            self.stats_points = 0
            self.strength = self.initial_strength  
            self.max_hp = self.initial_max_hp  
            self.attack_speed = self.initial_attack_speed 
            self.cr = 25
            self.cd = 150
            self.hp = self.max_hp  
        else:
            self.hp = self.max_hp 

    def crit(self):
        rand = random.randint(0, 100)
        return self.cr >= rand

    def crit_damage(self, damage):
        if self.cr:
            return int(damage * 1.5)

    def can_attack(self):
        now = pygame.time.get_ticks()
        return now - self.last_attack_time >= self.attack_speed

    def attack(self, target):
        if not self.can_attack():
            return
        if self.crit():
            rand = random.randint(-5, 5)
            damage = self.strength + rand
            damage = self.crit_damage(damage)
            target.hp -= damage
            target.hurt()
            damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), yellow)
            damage_text_group.add(damage_text)

        else:
            rand = random.randint(-5, 5)
            damage = self.strength + rand
            target.hp -= damage
            target.hurt()
            damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
            damage_text_group.add(damage_text)

        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
            self.xp += 50
            self.gold += 50
            self.check_level_up()

        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.last_attack_time = pygame.time.get_ticks()

    def check_level_up(self):
        if self.xp >= self.xp_to_next_level:
            self.level += 1
            self.xp -= self.xp_to_next_level
            self.xp_to_next_level += 50
            self.stats_points += 1

    def allocate_stats(self, stat):
        if self.stats_points > 0:
            if stat == 'STR':
                self.strength += 5
            elif stat == 'VIT':
                self.max_hp += 20
                self.hp = self.max_hp  # Fully heal after increasing max HP
            elif stat == 'AGI':
                if self.attack_speed > 100:
                    self.attack_speed -= 80
            elif stat == 'CRT':
                if self.cr < 100:
                    self.cr += 5
            self.stats_points -= 1



    def hurt(self):
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def update(self):
        animation_cooldown = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)

def reset_game(is_new_game=False):
    global hero, bandit_list, owned_skills, equipped_skills
    hero.reset(is_new_game=is_new_game)
    for bandit in bandit_list:
        bandit.reset(is_new_game=is_new_game)
    
    if is_new_game:
        # Reset skills
        for skill in owned_skills:
            skill.level = 0
            skill.cost_per_level = 100 if skill.name == "Fireball" else 120  # Reset cost to initial values
        equipped_skills = [None, None]  # Clear equipped skills


def show_start_screen():
    run_start = True
    while run_start:
        # Draw the background
        screen.fill(black)
        draw_bg()
        
        # Display the "New Game" and "Load Game" options
        draw_text('Battle RPG', font, yellow, screen_width // 2 - 100, screen_height // 2 - 150)
        draw_text('Press N to Start a New Game', font_2, white, screen_width // 2 - 150, screen_height // 2 - 50)
        draw_text('Press L to Load a Saved Game', font_2, white, screen_width // 2 - 150, screen_height // 2 + 20)

        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:  # New Game
                    reset_game(is_new_game=True)
                    run_start = False
                if event.key == pygame.K_l:  # Load Game
                    load_game()
                    run_start = False

        pygame.display.update()
        clock.tick(fps)

        
class Skill:
    def __init__(self, name, max_level, cost_per_level, skill_type, cooldown):
        self.name = name
        self.level = 0
        self.max_level = max_level
        self.cost_per_level = cost_per_level
        self.skill_type = skill_type  # AOE or Single-target
        self.cooldown = cooldown  # Cooldown in milliseconds
        self.last_used_time = 0  # Time when the skill was last used

    def buy_level(self, hero):
        if self.level < self.max_level and hero.gold >= self.cost_per_level:
            hero.gold -= self.cost_per_level
            self.level += 1
            self.cost_per_level *= 2
            return True
        return False

    def is_ready(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_used_time >= self.cooldown


def equip_skills_screen(owned_skills):
    run_equip = True
    selected_slot = None  # Track the currently selected slot (Q/E)
    message = ""  # Display success or error messages
    message_start_time = None  # Track when the message was set

    while run_equip:
        # Draw the background and the skill selection window
        draw_bg()
        window_x, window_y, window_width, window_height = 50, 50, screen_width - 100, screen_height - 100
        pygame.draw.rect(screen, black, (window_x, window_y, window_width, window_height))
        pygame.draw.rect(screen, white, (window_x + 5, window_y + 5, window_width - 10, window_height - 10))
        
        # Title for the equip skills screen
        draw_text("Equip and Upgrade Skills", font, black, window_x + 20, window_y + 10)

        # Display the hero's gold at the top
        draw_text(f"Gold: {hero.gold}", font, yellow, window_x + 20, window_y + 40)

        # Display the list of skills with notes
        for idx, skill in enumerate(owned_skills):
            draw_text(
                f"{idx + 1}. {skill.name} - Level {skill.level}/{skill.max_level} (Cost: {skill.cost_per_level} Gold)",
                font_2, yellow, window_x + 20, window_y + 80 + idx * 30
            )
            draw_text(
                f"Effect: {skill.skill_type} attack, Cooldown: {skill.cooldown // 1000}s", 
                font_2, white, window_x + 40, window_y + 100 + idx * 30
            )

        # Display equipped skills in slots
        draw_text(
            f"Slot Q: {equipped_skills[0].name if equipped_skills[0] else 'None'}",
            font_2, blue, window_x + 400, window_y + window_height - 130
        )
        draw_text(
            f"Slot E: {equipped_skills[1].name if equipped_skills[1] else 'None'}",
            font_2, blue, window_x + 400, window_y + window_height - 100
        )

        # Display messages (e.g., success or error) if within 2 seconds
        if message and message_start_time:
            if pygame.time.get_ticks() - message_start_time < 2000:
                draw_text(message, font_2, red, window_x + 20, window_y + window_height - 70)
            else:
                message = ""  # Clear the message after 2 seconds

        # Instructions
        draw_text("- Press Q/E + 1/2 to equip a skill.", font_2, black, window_x + 20, window_y + window_height - 160)
        draw_text("- Press P + 1/2 to buy or upgrade a skill.", font_2, black, window_x + 20, window_y + window_height - 140)
        draw_text("- Press ESC or B to exit this menu.", font_2, black, window_x + 20, window_y + window_height - 120)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                    run_equip = False
                elif event.key == pygame.K_p:
                    # Prompt user to select a skill to level up
                    sub_event = pygame.event.wait()
                    if sub_event.type == pygame.KEYDOWN:
                        skill_index = sub_event.key - pygame.K_1
                        if 0 <= skill_index < len(owned_skills):
                            if owned_skills[skill_index].buy_level(hero):
                                message = f"{owned_skills[skill_index].name} leveled up!"
                                message_start_time = pygame.time.get_ticks()
                            else:
                                message = "Not enough gold or max level reached."
                                message_start_time = pygame.time.get_ticks()
                elif event.key in [pygame.K_q, pygame.K_e]:
                    selected_slot = 0 if event.key == pygame.K_q else 1
                    message = f"Slot {['Q', 'E'][selected_slot]} selected. Choose a skill to equip."
                    message_start_time = pygame.time.get_ticks()
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    if selected_slot is not None:
                        skill_index = event.key - pygame.K_1
                        if 0 <= skill_index < len(owned_skills):
                            equipped_skills[selected_slot] = owned_skills[skill_index]
                            message = f"Equipped {owned_skills[skill_index].name} to {['Q', 'E'][selected_slot]}!"
                            message_start_time = pygame.time.get_ticks()
                        else:
                            message = "Invalid skill selection."
                            message_start_time = pygame.time.get_ticks()

        pygame.display.update()
        clock.tick(fps)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run_equip = False
                elif event.key == pygame.K_p:
                    # Prompt user to select a skill to level up
                    sub_event = pygame.event.wait()
                    if sub_event.type == pygame.KEYDOWN:
                        skill_index = sub_event.key - pygame.K_1
                        if 0 <= skill_index < len(owned_skills):
                            if owned_skills[skill_index].buy_level(hero):
                                message = f"{owned_skills[skill_index].name} leveled up!"
                                message_start_time = pygame.time.get_ticks()
                            else:
                                message = "Not enough gold or max level reached."
                                message_start_time = pygame.time.get_ticks()
                elif event.key in [pygame.K_q, pygame.K_e]:
                    selected_slot = 0 if event.key == pygame.K_q else 1
                    message = f"Slot {['Q', 'E'][selected_slot]} selected. Choose a skill to equip."
                    message_start_time = pygame.time.get_ticks()
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    if selected_slot is not None:
                        skill_index = event.key - pygame.K_1
                        if 0 <= skill_index < len(owned_skills):
                            equipped_skills[selected_slot] = owned_skills[skill_index]
                            message = f"Equipped {owned_skills[skill_index].name} to {['Q', 'E'][selected_slot]}!"
                            message_start_time = pygame.time.get_ticks()
                        else:
                            message = "Invalid skill selection."
                            message_start_time = pygame.time.get_ticks()

        pygame.display.update()
        clock.tick(fps)



def use_skill(skill, targets):
    if skill and skill.level > 0 and hero.alive:
        # Check if the skill is ready
        if not skill.is_ready():
            return False
        
        # Update the last_used_time for cooldown tracking
        skill.last_used_time = pygame.time.get_ticks()
        
        # Apply skill effects based on type
        if skill.skill_type == "AOE":
            for target in targets:
                if target.alive:
                    if hero.crit:
                        damage = skill.level * 10 + hero.strength
                        totaldmg = hero.crit_damage(damage)
                        color = yellow  # Critical hit
                    else:
                        totaldmg = skill.level * 10 + hero.strength
                        color = blue  # Normal hit
                    target.hp -= totaldmg
                    damage_text = DamageText(target.rect.centerx, target.rect.y - 20, f"{skill.name}: {totaldmg}", color)
                    damage_text_group.add(damage_text)
                    if target.hp < 1:
                        target.hp = 0
                        target.alive = False
                        target.death()
                        hero.xp += 50
                        hero.gold += 50
                        hero.check_level_up()
        
        elif skill.skill_type == "Single":
            # Target only the first alive target
            for target in targets:
                if target.alive:
                    if hero.crit:
                        damage = skill.level * 20 + hero.strength
                        totaldmg = hero.crit_damage(damage)
                        color = yellow  # Critical hit
                    else:
                        totaldmg = skill.level * 20 + hero.strength
                        color = blue  # Normal hit
                    target.hp -= totaldmg
                    damage_text = DamageText(target.rect.centerx, target.rect.y - 20, f"{skill.name}: {totaldmg}", color)
                    damage_text_group.add(damage_text)
                    if target.hp < 1:
                        target.hp = 0
                        target.alive = False
                        target.death()
                        hero.xp += 50
                        hero.gold += 50
                        hero.check_level_up()
                    break  # Stop after affecting the first alive target
        return True  # Skill successfully used
    return False  # Skill not used


def draw_cooldowns():
    if equipped_skills[0]:
        cooldown_q = max(0, equipped_skills[0].cooldown - (pygame.time.get_ticks() - equipped_skills[0].last_used_time))
        draw_text(f"Q: {equipped_skills[0].name} ({cooldown_q // 1000}s)", font_2, red, 20, screen_height - 80)
    if equipped_skills[1]:
        cooldown_e = max(0, equipped_skills[1].cooldown - (pygame.time.get_ticks() - equipped_skills[1].last_used_time))
        draw_text(f"E: {equipped_skills[1].name} ({cooldown_e // 1000}s)", font_2, blue, 20, screen_height - 50)

def scale_enemy_stats(stage):
    for bandit in bandit_list:
        bandit.max_hp = int(bandit.initial_max_hp * (1 + 0.2 * (stage - 1)))
        bandit.hp = bandit.max_hp
        bandit.strength = int(bandit.initial_strength * (1 + 0.1 * (stage - 1)))
        bandit.attack_speed = max(500, int(bandit.initial_attack_speed * (1 - 0.05 * (stage - 1))))

def next_stage():
    global stage, wins
    stage += 1
    wins = 0

    # Reset each bandit
    for bandit in bandit_list:
        bandit.reset(is_new_game=False)  # Reset stats and revive
        bandit.max_hp = int(bandit.initial_max_hp * (1 + 0.2 * (stage - 1)))  # Scale max HP
        bandit.hp = bandit.max_hp
        bandit.strength = int(bandit.initial_strength * (1 + 0.2 * (stage - 1)))  # Scale strength
        bandit.attack_speed = max(500, int(bandit.initial_attack_speed * (1 - 0.05 * (stage - 1))))  # Scale speed
    hero.hp = hero.max_hp



# Initialize skills
fireball = Skill("Fireball", max_level=5, cost_per_level=100, skill_type="AOE", cooldown=3000)  # 3-second cooldown
shield_bash = Skill("Shield Bash", max_level=5, cost_per_level=120, skill_type="Single", cooldown=2000)  # 2-second cooldown
owned_skills = [fireball, shield_bash]
equipped_skills = [None, None]  # Q and E slots

# HealthBar class
class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp, max_hp=None):
        self.hp = hp
        if max_hp:  # Update max_hp if provided
            self.max_hp = max_hp
        ratio = max(0, min(self.hp / self.max_hp, 1))  # Ensure ratio is between 0 and 1
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))  # Full health bar (red background)
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))  # Current health (green foreground)



# DamageText class
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.y -= 1
        self.counter += 1
        if self.counter > 30:
            self.kill()

damage_text_group = pygame.sprite.Group()

hero = Fighter(200, 260, 'Knight', 100, 10, 3, 1000)
bandit1 = Fighter(550, 270, 'Bandit', 40, 6, 1, 1000)
bandit2 = Fighter(700, 270, 'Bandit', 40, 6, 1, 900)

bandit_list = [bandit1, bandit2]
next_stage()

hero_health_bar = HealthBar(100, screen_height - bottom_panel + 40, hero.hp, hero.max_hp)
bandit1_health_bar = HealthBar(550, screen_height - bottom_panel + 40, bandit1.hp, bandit1.max_hp)
bandit2_health_bar = HealthBar(550, screen_height - bottom_panel + 100, bandit2.hp, bandit2.max_hp)

restart_button = button.Button(screen, 330, 120, restart_img, 120, 30)

# Load the saved game
load_game()

# Show the start screen
show_start_screen()

run = True
pause = False  # Pause flag
stats_allocation = False  # Stats allocation flag

# Main game loop
while run:
    clock.tick(fps)

    # Draw background and panel
    draw_bg()
    draw_panel()
    draw_cooldowns()

    # Draw health bars
    hero_health_bar.draw(hero.hp)
    for i, bandit in enumerate(bandit_list):
        HealthBar(550, screen_height - bottom_panel + 40 + (i * 60), bandit.hp, bandit.max_hp).draw(bandit.hp)

    # Update and draw the hero
    hero.update()
    hero.draw()

    # Update and draw the bandits
    for bandit in bandit_list:
        bandit.update()
        bandit.draw()

    # Update damage text
    damage_text_group.update()
    damage_text_group.draw(screen)

    # Handle stats allocation
    if stats_allocation:
        show_allocate_stats_window()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    hero.allocate_stats('STR')
                elif event.key == pygame.K_2:
                    hero.allocate_stats('VIT')
                elif event.key == pygame.K_3:
                    hero.allocate_stats('AGI')
                elif event.key == pygame.K_4:
                    hero.allocate_stats('CRT')

        # Check if stats allocation is complete
        if hero.stats_points <= 0:
            stats_allocation = False  # Exit stats allocation mode
            pause = True  # Trigger battle complete message
        continue  # Skip the rest of the loop until stats allocation is finished

    # Handle pause
    if pause:
        draw_text("Battle Complete!", font, yellow, screen_width // 2 - 100, screen_height // 2 - 100)
        draw_text("Press Enter or Space to continue to the next stage", font_2, white, screen_width // 2 - 150, screen_height // 2)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:  # Resume game
                    pause = False
                    next_stage()  # Proceed to the next stage
        continue  # Skip the rest of the loop until Enter is pressed

    # Handle mouse hover and clicks
    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()
    attack = False
    target = None

    for bandit in bandit_list:
        if bandit.rect.collidepoint(pos) and bandit.alive:
            pygame.mouse.set_visible(False)
            screen.blit(sword_img, pos)
            if clicked:
                attack = True
                target = bandit

    # Hero attack logic
    if attack and hero.alive and target and target.alive:
        hero.attack(target)

    # Bandit attack logic
    for bandit in bandit_list:
        if bandit.alive and hero.alive and bandit.can_attack():
            bandit.attack(hero)

    # Check for game over conditions
    if not hero.alive:
        game_over = -1
    elif all(not bandit.alive for bandit in bandit_list):
        game_over = 1
        pause = True  # Enter pause state to show "Battle Complete!"
        stats_allocation = hero.stats_points > 0  # Enter stats allocation mode if points are available

    # Handle pause
    if pause:
        draw_text("Battle Complete!", font, yellow, screen_width // 2 - 100, screen_height // 2 - 100)
        draw_text("Press Enter or Space to continue to the next stage", font_2, white, screen_width // 2 - 150, screen_height // 2)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:  # Resume game
                    hero.hp = hero.max_hp
                    pause = False
                    next_stage()  # Proceed to the next stage
        continue  # Skip the rest of the loop until Enter is pressed


    # Handle game over
    if game_over != 0:
        if game_over == 1:
            if hero.stats_points > 0:
                stats_allocation = True
        elif game_over == -1:
            screen.blit(defeat_img, (290, 50))  # Show defeat image
            # Only display the restart button when it's a defeat
            if restart_button.draw():
                reset_game(is_new_game=False)  # Restart without resetting progress
                game_over = 0  # Reset game over state


    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            clicked = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save_game()
            if event.key == pygame.K_l:
                load_game()
            # Equip skills screen
            if event.key == pygame.K_b:
                equip_skills_screen(owned_skills)
            # Use skills in slots
            if event.key == pygame.K_q and equipped_skills[0]:
                use_skill(equipped_skills[0], bandit_list)
            if event.key == pygame.K_e and equipped_skills[1]:
                use_skill(equipped_skills[1], bandit_list)

    # Update the display
    pygame.display.update()

pygame.quit()




