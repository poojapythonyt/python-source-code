import pygame
import random
import math
import os

pygame.init()

# -----------------------------
# WINDOW
# -----------------------------
WIDTH = 900
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON SURVIVOR")

clock = pygame.time.Clock()
FPS = 60

# -----------------------------
# COLORS
# -----------------------------
BLACK = (8, 10, 20)
WHITE = (245, 245, 255)
BLUE = (50, 180, 255)
CYAN = (40, 240, 255)
RED = (255, 70, 90)
YELLOW = (255, 220, 70)
GREEN = (70, 255, 150)
PURPLE = (180, 80, 255)
GRAY = (100, 110, 130)

# -----------------------------
# FONTS
# -----------------------------
font_big = pygame.font.Font(None, 64)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 26)

# -----------------------------
# HIGH SCORE
# -----------------------------
HIGH_SCORE_FILE = "neon_highscore.txt"


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            return int(file.read())
    except:
        return 0


def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(score))
    except:
        pass


high_score = load_high_score()


# -----------------------------
# PARTICLES
# -----------------------------
particles = []


def create_particles(x, y, color, amount=12):
    for _ in range(amount):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 5)

        particles.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(20, 45),
            "color": color,
            "size": random.randint(2, 5)
        })


def update_particles():
    for particle in particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["life"] -= 1

        particle["vx"] *= 0.97
        particle["vy"] *= 0.97

        if particle["life"] <= 0:
            particles.remove(particle)


def draw_particles():
    for particle in particles:
        pygame.draw.circle(
            screen,
            particle["color"],
            (int(particle["x"]), int(particle["y"])),
            particle["size"]
        )


# -----------------------------
# PLAYER
# -----------------------------
class Player:

    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 90

        self.width = 34
        self.height = 42

        self.speed = 6

        self.lives = 3

        self.shield = False
        self.shield_timer = 0

        self.invincible = 0

    def update(self, keys):

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed

        self.x = max(25, min(WIDTH - 25, self.x))
        self.y = max(25, min(HEIGHT - 25, self.y))

        if self.shield:
            self.shield_timer -= 1

            if self.shield_timer <= 0:
                self.shield = False

        if self.invincible > 0:
            self.invincible -= 1

    def draw(self):

        # Flicker when invincible
        if self.invincible > 0 and self.invincible % 8 < 4:
            return

        # Glow
        pygame.draw.circle(
            screen,
            (20, 80, 120),
            (self.x, self.y),
            30
        )

        # Ship
        points = [
            (self.x, self.y - 23),
            (self.x - 18, self.y + 20),
            (self.x, self.y + 12),
            (self.x + 18, self.y + 20)
        ]

        pygame.draw.polygon(screen, CYAN, points)
        pygame.draw.polygon(screen, WHITE, points, 2)

        # Engine
        pygame.draw.polygon(
            screen,
            YELLOW,
            [
                (self.x - 7, self.y + 15),
                (self.x + 7, self.y + 15),
                (self.x, self.y + 30)
            ]
        )

        # Shield
        if self.shield:
            pygame.draw.circle(
                screen,
                BLUE,
                (self.x, self.y),
                34,
                3
            )

    def rect(self):
        return pygame.Rect(
            self.x - 15,
            self.y - 18,
            30,
            36
        )


# -----------------------------
# ENEMY
# -----------------------------
class Enemy:

    def __init__(self, difficulty):

        self.x = random.randint(30, WIDTH - 30)
        self.y = random.randint(-200, -40)

        self.size = random.randint(15, 28)

        self.speed = random.uniform(
            2.5 + difficulty * 0.15,
            4.0 + difficulty * 0.25
        )

        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-3, 3)

        self.color = random.choice([
            RED,
            PURPLE,
            (255, 100, 40)
        ])

    def update(self):

        self.y += self.speed
        self.rotation += self.rotation_speed

    def draw(self):

        # Glow
        pygame.draw.circle(
            screen,
            (70, 20, 50),
            (int(self.x), int(self.y)),
            self.size + 8
        )

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            self.size
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (int(self.x - self.size * 0.3),
             int(self.y - self.size * 0.3)),
            3
        )

    def rect(self):

        return pygame.Rect(
            self.x - self.size,
            self.y - self.size,
            self.size * 2,
            self.size * 2
        )


# -----------------------------
# ENERGY ORB
# -----------------------------
class Energy:

    def __init__(self):

        self.x = random.randint(30, WIDTH - 30)
        self.y = random.randint(50, HEIGHT - 150)

        self.radius = 9

        self.angle = random.random() * math.pi * 2

    def update(self):

        self.angle += 0.08

    def draw(self):

        pulse = int(math.sin(self.angle) * 3)

        pygame.draw.circle(
            screen,
            (80, 120, 80),
            (self.x, self.y),
            self.radius + 8 + pulse
        )

        pygame.draw.circle(
            screen,
            YELLOW,
            (self.x, self.y),
            self.radius
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (self.x - 2, self.y - 2),
            3
        )

    def rect(self):

        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )


# -----------------------------
# SHIELD POWERUP
# -----------------------------
class ShieldPower:

    def __init__(self):

        self.x = random.randint(40, WIDTH - 40)
        self.y = random.randint(70, HEIGHT - 150)

        self.radius = 12

        self.angle = 0

    def update(self):

        self.angle += 0.08

    def draw(self):

        pygame.draw.circle(
            screen,
            (60, 80, 160),
            (self.x, self.y),
            22
        )

        pygame.draw.circle(
            screen,
            BLUE,
            (self.x, self.y),
            self.radius,
            3
        )

        pygame.draw.line(
            screen,
            CYAN,
            (self.x, self.y - 7),
            (self.x, self.y + 7),
            2
        )

        pygame.draw.line(
            screen,
            CYAN,
            (self.x - 7, self.y),
            (self.x + 7, self.y),
            2
        )

    def rect(self):

        return pygame.Rect(
            self.x - 14,
            self.y - 14,
            28,
            28
        )


# -----------------------------
# BACKGROUND STARS
# -----------------------------
stars = []

for _ in range(100):

    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3),
        random.uniform(0.5, 2)
    ])


def update_stars():

    for star in stars:

        star[1] += star[3]

        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0


def draw_stars():

    for x, y, size, speed in stars:

        pygame.draw.circle(
            screen,
            (100, 120, 150),
            (int(x), int(y)),
            size
        )


# -----------------------------
# GAME RESET
# -----------------------------
def reset_game():

    global player
    global enemies
    global energies
    global shield_power
    global score
    global game_time
    global spawn_timer
    global energy_timer
    global shield_timer
    global difficulty
    global particles

    player = Player()

    enemies = []
    energies = []
    shield_power = None

    score = 0
    game_time = 0

    spawn_timer = 0
    energy_timer = 0
    shield_timer = 0

    difficulty = 1

    particles = []


reset_game()

game_over = False


# -----------------------------
# MAIN GAME LOOP
# -----------------------------
running = True

while running:

    clock.tick(FPS)

    # -------------------------
    # EVENTS
    # -------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if game_over and event.key == pygame.K_r:
                reset_game()
                game_over = False

    keys = pygame.key.get_pressed()

    # -------------------------
    # GAME UPDATE
    # -------------------------
    if not game_over:

        player.update(keys)

        update_stars()
        update_particles()

        game_time += 1

        # Difficulty increases
        difficulty = 1 + game_time // (FPS * 10)

        # Score
        score += 1

        # ---------------------
        # ENEMY SPAWNING
        # ---------------------
        spawn_timer += 1

        spawn_delay = max(
            18,
            55 - difficulty * 3
        )

        if spawn_timer >= spawn_delay:

            enemies.append(
                Enemy(difficulty)
            )

            spawn_timer = 0

        # ---------------------
        # ENERGY SPAWN
        # ---------------------
        energy_timer += 1

        if energy_timer >= 180 and len(energies) < 2:

            energies.append(
                Energy()
            )

            energy_timer = 0

        # ---------------------
        # SHIELD SPAWN
        # ---------------------
        shield_timer += 1

        if shield_power is None and shield_timer >= 600:

            shield_power = ShieldPower()
            shield_timer = 0

        # ---------------------
        # UPDATE ENEMIES
        # ---------------------
        for enemy in enemies[:]:

            enemy.update()

            if enemy.y > HEIGHT + 50:

                enemies.remove(enemy)

            elif enemy.rect().colliderect(player.rect()):

                if player.shield:

                    create_particles(
                        enemy.x,
                        enemy.y,
                        BLUE,
                        20
                    )

                    enemies.remove(enemy)

                elif player.invincible <= 0:

                    player.lives -= 1
                    player.invincible = FPS * 2

                    create_particles(
                        player.x,
                        player.y,
                        RED,
                        25
                    )

                    enemies.remove(enemy)

                    if player.lives <= 0:

                        game_over = True

                        if score > high_score:
                            high_score = score
                            save_high_score(score)

        # ---------------------
        # ENERGY
        # ---------------------
        for energy in energies[:]:

            energy.update()

            if energy.rect().colliderect(player.rect()):

                score += 500

                create_particles(
                    energy.x,
                    energy.y,
                    YELLOW,
                    18
                )

                energies.remove(energy)

        # ---------------------
        # SHIELD
        # ---------------------
        if shield_power:

            shield_power.update()

            if shield_power.rect().colliderect(player.rect()):

                player.shield = True
                player.shield_timer = FPS * 5

                create_particles(
                    shield_power.x,
                    shield_power.y,
                    BLUE,
                    20
                )

                shield_power = None

    else:

        update_particles()

    # -------------------------
    # DRAW
    # -------------------------
    screen.fill(BLACK)

    draw_stars()

    # Draw energy
    for energy in energies:
        energy.draw()

    # Draw shield power
    if shield_power:
        shield_power.draw()

    # Draw enemies
    for enemy in enemies:
        enemy.draw()

    # Draw player
    player.draw()

    # Draw particles
    draw_particles()

    # -------------------------
    # HUD
    # -------------------------
    score_text = font_medium.render(
        f"SCORE: {score}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (20, 20)
    )

    high_text = font_small.render(
        f"BEST: {high_score}",
        True,
        GRAY
    )

    screen.blit(
        high_text,
        (20, 58)
    )

    # Lives
    lives_text = font_small.render(
        f"LIVES: {'♥ ' * player.lives}",
        True,
        RED
    )

    screen.blit(
        lives_text,
        (WIDTH - 150, 25)
    )

    # Shield status
    if player.shield:

        shield_text = font_small.render(
            "SHIELD ACTIVE",
            True,
            CYAN
        )

        screen.blit(
            shield_text,
            (WIDTH - 180, 55)
        )

    # Difficulty
    difficulty_text = font_small.render(
        f"LEVEL {difficulty}",
        True,
        PURPLE
    )

    screen.blit(
        difficulty_text,
        (WIDTH // 2 - 40, 20)
    )

    # -------------------------
    # GAME OVER
    # -------------------------
    if game_over:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 190)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        title = font_big.render(
            "GAME OVER",
            True,
            RED
        )

        screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                200
            )
        )

        final_score = font_medium.render(
            f"Score: {score}",
            True,
            WHITE
        )

        screen.blit(
            final_score,
            (
                WIDTH // 2 - final_score.get_width() // 2,
                275
            )
        )

        best = font_medium.render(
            f"Best: {high_score}",
            True,
            YELLOW
        )

        screen.blit(
            best,
            (
                WIDTH // 2 - best.get_width() // 2,
                320
            )
        )

        restart = font_small.render(
            "Press R to Restart",
            True,
            CYAN
        )

        screen.blit(
            restart,
            (
                WIDTH // 2 - restart.get_width() // 2,
                390
            )
        )

        quit_text = font_small.render(
            "ESC - Quit",
            True,
            GRAY
        )

        screen.blit(
            quit_text,
            (
                WIDTH // 2 - quit_text.get_width() // 2,
                430
            )
        )

    pygame.display.flip()


pygame.quit()