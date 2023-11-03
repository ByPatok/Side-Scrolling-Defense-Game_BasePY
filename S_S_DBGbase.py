import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1024, 768
BACKGROUND_COLOR = (135, 206, 235)
FPS = 60

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Side-Scrolling Defense Game")

# Game clock
clock = pygame.time.Clock()

# Game states
START = 0
PLAYING = 1
GAME_OVER = 2
current_state = START  # Start the game at the start screen

# Create the castle and mine locations
castle_x, castle_y = 100, HEIGHT // 2
mine_x, mine_y = WIDTH - 100, HEIGHT // 2

# Health, damage, and cooldown for guards and enemies
guard_health = 50
guard_damage = 10  # Modified to make guards and enemies do the same damage
guard_cooldown = 1.5

enemy_health = 50
enemy_damage = 10  # Modified to make guards and enemies do the same damage
enemy_cooldown = 1.5

mine_health = 500  # Increased mine health
castle_health = 500  # Increased castle health

# Health bar colors
HEALTH_BAR_COLOR = (0, 255, 0)
DAMAGE_COLOR = (255, 0, 0)

# Width of the health bars for mine and castle
mine_health_bar_width = 100
castle_health_bar_width = 100

# Spawn timers for guards and enemies
guard_spawn_timer = 0
enemy_spawn_timer = 0

# Enemy spawn interval (every 10 seconds)
spawn_interval = FPS * 10

# Load and resize images (e.g., castle, mine, guard, enemy)
castle_img = pygame.transform.scale(pygame.image.load("castle.png"), (50, 50))
mine_img = pygame.transform.scale(pygame.image.load("mine.png"), (50, 50))
guard_img = pygame.transform.scale(pygame.image.load("guard.png"), (50, 50))
enemy_img = pygame.transform.scale(pygame.image.load("zombie.png"), (50, 50))

# Lists to store guards and enemies
guards = []
enemies = []

# Player level and experience
level = 1
player_xp = 0
xp_needed_for_level_up = 100
gold_generation_rate = 1

def draw_health_bar(x, y, health, max_health, width, height):
    pygame.draw.rect(screen, DAMAGE_COLOR, (x, y, width, height))
    health_width = (health / max_health) * width
    pygame.draw.rect(screen, HEALTH_BAR_COLOR, (x, y, health_width, height))

def check_combat(guard, enemy):
    if guard[2] > 0 and enemy[2] > 0:  # Check if both have health
        if abs(guard[0] - enemy[0]) < 25:  # Check for collision
            guard[2] -= enemy_damage
            enemy[2] -= guard_damage

def remove_dead_enemies():
    global player_xp
    updated_enemies = []
    for enemy in enemies:
        if enemy[2] > 0:
            updated_enemies.append(enemy)
        else:
            player_xp += 10  # Gain XP when an enemy is killed
    return updated_enemies

def reset_game():
    global current_state, gold, level, player_xp, xp_needed_for_level_up, castle_health, mine_health, guard_spawn_timer, enemy_spawn_timer
    current_state = START
    gold = 0
    level = 1
    player_xp = 0
    xp_needed_for_level_up = 100
    guards.clear()
    enemies.clear()
    castle_health = 500  # Reset castle health
    mine_health = 500  # Reset mine health
    guard_spawn_timer = 0
    enemy_spawn_timer = 0

# Buttons
class FancyButton:
    def __init__(self, text, x, y, width, height, base_color, hover_color, click_color, font_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color
        self.click_color = click_color
        self.font_color = font_color
        self.current_color = self.base_color
        self.clicked = False
        self.font = pygame.font.Font(None, 36)  # Default font

    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)  # Add a black border

        text_surface = self.font.render(self.text, True, self.font_color)
        text_rect = text_surface.get_rect()
        text_rect.center = self.rect.center
        screen.blit(text_surface, text_rect)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        is_clicked = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            if is_clicked:
                self.current_color = self.click_color
                self.clicked = True
            else:
                self.clicked = False
        else:
            self.current_color = self.base_color
            self.clicked = False

# Define the buttons
start_button = FancyButton("Start Game", 320, 240, 160, 40, (65, 105, 225), (70, 130, 180), (30, 70, 100), (255, 255, 255))
quit_button = FancyButton("Quit", 320, 300, 160, 40, (220, 20, 60), (180, 30, 30), (100, 20, 20), (255, 255, 255))
recruit_guard_button = FancyButton("Recruit Guard", WIDTH - 200, HEIGHT - 60, 160, 40, (50, 205, 50), (34, 139, 34), (0, 128, 0), (255, 255, 255))
font = pygame.font.Font(None, 36)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if current_state == START:
        # Draw the start screen
        for button in (start_button, quit_button):
            button.update()
            button.draw(screen)

        if start_button.clicked:
            reset_game()
            current_state = PLAYING
        elif quit_button.clicked:
            pygame.quit()
            sys.exit()

    if current_state == PLAYING:
        recruit_guard_button.update()
        recruit_guard_button.draw(screen)

        if recruit_guard_button.clicked and guard_spawn_timer <= 0 and gold >= 10:
            guards.append([castle_x, castle_y, guard_health, guard_damage, guard_cooldown])
            guard_spawn_timer = guard_cooldown
            gold -= 10

    # Game logic based on the current state
    if current_state == PLAYING:
        # Generate gold
        gold += gold_generation_rate / FPS

        # Check for level up
        if player_xp >= xp_needed_for_level_up:
            level += 1
            player_xp -= xp_needed_for_level_up
            xp_needed_for_level_up = level * 50
            gold_generation_rate += 2  # Increase gold generation rate when leveling up

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
                check_combat(guard, enemy)  # Check for combat between guard and enemy

        enemies = remove_dead_enemies()  # Remove dead enemies and grant XP

        for enemy in enemies:
            enemy[0] -= 5  # Move enemies to the right
            if castle_health > 0:
                if abs(enemy[0] - castle_x) < 25:  # Check for collision with the castle
                    castle_health -= enemy_damage  # Damage the castle

        # Check if castle health is zero and change game state to GAME_OVER
        if castle_health <= 0:
            current_state = GAME_OVER

        # Spawn new enemies every 10 seconds
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= spawn_interval:
            enemies.append([mine_x, mine_y, enemy_health, enemy_damage, enemy_cooldown])
            enemy_spawn_timer = 0

    elif current_state == GAME_OVER:
        for button in (start_button, quit_button):
            button.update()
            button.draw(screen)

        if start_button.clicked:
            reset_game()
            current_state = PLAYING
        elif quit_button.clicked:
            pygame.quit()
            sys.exit()

    # Draw everything
    screen.fill(BACKGROUND_COLOR)

    if current_state == START:
        # Draw the start screen
        for button in (start_button, quit_button):
            button.update()
            button.draw(screen)

        if start_button.clicked:
            reset_game()
            current_state = PLAYING
        elif quit_button.clicked:
            pygame.quit()
            sys.exit()

    elif current_state == PLAYING:
        # Draw the game screen
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

        draw_health_bar(castle_x - castle_img.get_width() // 2, castle_y - castle_img.get_height() // 2 - 10, castle_health, 500, castle_health_bar_width, 5)
        draw_health_bar(mine_x - mine_img.get_width() // 2, mine_y - mine_img.get_height() // 2 - 10, mine_health, 500, mine_health_bar_width, 5)

        bottom_box = pygame.Surface((WIDTH, HEIGHT // 6))
        bottom_box.fill((0, 0, 0))
        screen.blit(bottom_box, (0, HEIGHT - HEIGHT // 6))

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

        recruit_guard_button.update()
        recruit_guard_button.draw(screen)

    elif current_state == GAME_OVER:
        # Draw the game-over screen
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
        text = font.render("Game Over", True, (255, 255, 255))
        screen.blit(text, (460, 200))
        pygame.draw.rect(screen, (0, 0, 255), (420, 240, 160, 40))
        text = font.render("Restart", True, (255, 255, 255))
        screen.blit(text, (460, 250))
        pygame.draw.rect(screen, (255, 0, 0), (420, 300, 160, 40))
        text = font.render("Quit", True, (255, 255, 255))
        screen.blit(text, (460, 310))

    pygame.display.update()
    clock.tick(FPS)
