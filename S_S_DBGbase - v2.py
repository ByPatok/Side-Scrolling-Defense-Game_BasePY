import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 400
BACKGROUND_COLOR = (135, 206, 235)
FPS = 60

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Side-Scrolling Defense Game")

# Game clock
clock = pygame.time.Clock()

# Create the castle and mine locations
castle_x, castle_y = 100, HEIGHT // 2
mine_x, mine_y = WIDTH - 100, HEIGHT // 2

# Create a font for displaying information
font = pygame.font.Font(None, 36)

# Health, damage, and cooldown for guards and enemies
guard_health = 50
guard_damage = 50
guard_cooldown = 1.5

enemy_health = 50
enemy_damage = 10
enemy_cooldown = 1.5

mine_health = 200

# Gold and gold generation rate
gold = 0
gold_generation_rate = 1  # Gold generated per second

# Castle and mine health
castle_health = 200

# Health bar colors
HEALTH_BAR_COLOR = (0, 255, 0)
DAMAGE_COLOR = (255, 0, 0)

# Spawn timers for guards and enemies
guard_spawn_timer = 0
enemy_spawn_timer = 0

# Enemy spawn interval (every 10 seconds)
enemy_spawn_interval = FPS * 10

# Load and resize images (e.g., castle, mine, guard, enemy)
castle_img = pygame.transform.scale(pygame.image.load("castle.png"), (50, 50))
mine_img = pygame.transform.scale(pygame.image.load("mine.png"), (50, 50))
guard_img = pygame.transform.scale(pygame.image.load("guard.png"), (50, 50))
enemy_img = pygame.transform.scale(pygame.image.load("zombie.png"), (50, 50))

guards = []
enemies = []

# Player level and experience
level = 1
player_xp = 0
xp_needed_for_level_up = 100

def draw_health_bar(x, y, health, max_health, width, height):
    pygame.draw.rect(screen, DAMAGE_COLOR, (x, y, width, height))
    health_width = (health / max_health) * width
    pygame.draw.rect(screen, HEALTH_BAR_COLOR, (x, y, health_width, height))

# Function to check for collision and handle combat
def check_combat(guard, enemy, player_xp):
    if guard[2] > 0 and enemy[2] > 0:  # Check if both have health
        if abs(guard[0] - enemy[0]) < 25:  # Check for collision
            guard[2] -= enemy_damage
            enemy[2] -= guard_damage
            if enemy[2] <= 0:  # Enemy defeated
                player_xp += 20  # Award XP for defeating an enemy
                enemies.remove(enemy)
    return player_xp  # Return the updated player's XP

# Main Game Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle user input (e.g., spawning guards)
            if event.button == 1:  # Left mouse button
                if guard_spawn_timer <= 0 and gold >= 10:  # Check if there's enough gold to recruit a guard
                    guards.append([castle_x, castle_y, guard_health, guard_damage, guard_cooldown])  # Initialize guard
                    guard_spawn_timer = guard_cooldown
                    gold -= 10  # Deduct gold for recruiting a guard

    # Generate gold
    gold += gold_generation_rate / FPS

    # Check for level up
    if player_xp >= xp_needed_for_level_up:
        level += 1
        player_xp -= xp_needed_for_level_up
        xp_needed_for_level_up = level * 100
        gold_generation_rate += 1  # Increase gold generation rate when leveling up

    # - Spawn guards from the castle
    if guard_spawn_timer > 0:
        guard_spawn_timer -= 1 / FPS

    # - Update positions and check for combat
    for guard in guards:
        guard[0] += 5  # Move guards to the left
        if abs(guard[0] - mine_x) < 25:  # Check for collision with the mine
            mine_health -= guard_damage  # Damage the mine
            if mine_health <= 0:
                mine_health = 0

        for enemy in enemies:
            player_xp = check_combat(guard, enemy, player_xp)  # Check for combat between guard and enemy

    for enemy in enemies:
        enemy[0] -= 5  # Move enemies to the right
        if abs(enemy[0] - castle_x) < 25:  # Check for collision with the castle
            castle_health -= enemy_damage  # Damage the castle
            if castle_health <= 0:
                castle_health = 0

    # Remove guards and enemies with zero health
    guards = [guard for guard in guards if guard[2] > 0]
    enemies = [enemy for enemy in enemies if enemy[2] > 0]

    # Draw everything
    screen.fill(BACKGROUND_COLOR)

    # Draw images for castle, mine, guards, and enemies
    screen.blit(castle_img, (castle_x - castle_img.get_width() // 2, castle_y - castle_img.get_height() // 2))
    screen.blit(mine_img, (mine_x - mine_img.get_width() // 2, mine_y - mine_img.get_height() // 2))

    for guard in guards:
        x, y, health, _, _ = guard
        screen.blit(guard_img, (x - guard_img.get_width() // 2, y - guard_img.get_height() // 2))
        draw_health_bar(x - guard_img.get_width() // 2, y - guard_img.get_height() // 2 - 10, health, guard_health, guard_img.get_width(), 5)

    for enemy in enemies:
        x, y, health, _, _ = enemy
        screen.blit(enemy_img, (x - enemy_img.get_width() // 2, y - enemy_img.get_height() // 2))
        draw_health_bar(x - enemy_img.get_width() // 2, y - enemy_img.get_height() // 2 - 10, health, enemy_health, enemy_img.get_width(), 5)

    # Draw health bars for the castle and mine
    draw_health_bar(castle_x - castle_img.get_width() // 2, castle_y - castle_img.get_height() // 2 - 10, castle_health, 200, castle_img.get_width(), 5)
    draw_health_bar(mine_x - mine_img.get_width() // 2, mine_y - mine_img.get_height() // 2 - 10, mine_health, 100, mine_img.get_width(), 5)

    # Display game information in a bottom box
    bottom_box = pygame.Surface((WIDTH, HEIGHT // 6))
    bottom_box.fill((0, 0, 0))
    screen.blit(bottom_box, (0, HEIGHT - HEIGHT // 6))

    # Display important information in the bottom box
    text = font.render("Guards: " + str(len(guards)), True, (255, 255, 255))
    screen.blit(text, (20, HEIGHT - HEIGHT // 6 + 10))
    text = font.render("Enemies: " + str(len(enemies)), True, (255, 255, 255))
    screen.blit(text, (160, HEIGHT - HEIGHT // 6 + 10))
    text = font.render("Level: " + str(level), True, (255, 255, 255))
    screen.blit(text, (320, HEIGHT - HEIGHT // 6 + 10))
    text = font.render("XP: " + str(int(player_xp)) + "/" + str(xp_needed_for_level_up), True, (255, 255, 255))
    screen.blit(text, (470, HEIGHT - HEIGHT // 6 + 10))
    text = font.render("Gold: " + str(int(gold)), True, (255, 255, 255))
    screen.blit(text, (320, HEIGHT - HEIGHT // 6 + 40))

    # Draw a button to recruit guards
    pygame.draw.rect(screen, (0, 0, 255), (WIDTH - 160, HEIGHT - HEIGHT // 6 + 10, 140, 40))
    text = font.render("Recruit Guard", True, (255, 255, 255))
    screen.blit(text, (WIDTH - 150, HEIGHT - HEIGHT // 6 + 20))

    # Spawn new enemies every 10 seconds
    enemy_spawn_timer -= 1
    if enemy_spawn_timer <= 0:
        enemies.append([mine_x, mine_y, enemy_health, enemy_damage, enemy_cooldown])
        enemy_spawn_timer = enemy_spawn_interval

    pygame.display.update()
    clock.tick(FPS)
