import pygame
import random
import math

pygame.init()

# =========================================================
# SETTINGS
# =========================================================

WIDTH = 800
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge Rush - HARD MODE")

clock = pygame.time.Clock()

# =========================================================
# COLORS
# =========================================================

BLACK = (15, 15, 20)
WHITE = (255, 255, 255)
RED = (230, 60, 60)
DARK_RED = (150, 30, 30)
BLUE = (60, 150, 255)
CYAN = (50, 220, 240)
YELLOW = (255, 210, 50)
PURPLE = (180, 70, 240)
GREEN = (70, 220, 120)
ORANGE = (255, 140, 40)
GRAY = (130, 130, 140)

# =========================================================
# FONTS
# =========================================================

font = pygame.font.Font(None, 34)
small_font = pygame.font.Font(None, 26)
big_font = pygame.font.Font(None, 80)

# =========================================================
# PLAYER
# =========================================================

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50

player = pygame.Rect(
    WIDTH // 2 - PLAYER_WIDTH // 2,
    HEIGHT - 90,
    PLAYER_WIDTH,
    PLAYER_HEIGHT
)

PLAYER_SPEED = 8

# =========================================================
# GAME VARIABLES
# =========================================================

blocks = []
coins = []
powerups = []
particles = []

score = 0
high_score = 0

lives = 3

shield = False
shield_timer = 0

game_over = False
paused = False

spawn_timer = 0
coin_timer = 0
powerup_timer = 0

difficulty_timer = 0

base_speed = 4
spawn_delay = 35

shake_timer = 0

# =========================================================
# CREATE BLOCK
# =========================================================

def create_block():

    block_type = random.choices(
        ["normal", "fast", "moving", "bomb"],
        weights=[50, 20, 20, 10]
    )[0]

    size = random.randint(30, 55)

    x = random.randint(0, WIDTH - size)

    if block_type == "normal":

        speed = base_speed

        color = RED

    elif block_type == "fast":

        speed = base_speed + random.uniform(3, 6)

        color = PURPLE

    elif block_type == "moving":

        speed = base_speed

        color = YELLOW

    else:

        speed = base_speed * 0.8

        color = ORANGE

    block = {
        "rect": pygame.Rect(x, -size, size, size),
        "type": block_type,
        "speed": speed,
        "color": color,
        "direction": random.choice([-1, 1]),
        "move_speed": random.uniform(2, 4)
    }

    blocks.append(block)


# =========================================================
# CREATE COIN
# =========================================================

def create_coin():

    x = random.randint(20, WIDTH - 20)
    y = -20

    coin = {
        "x": x,
        "y": y,
        "radius": 10,
        "speed": base_speed
    }

    coins.append(coin)


# =========================================================
# CREATE POWERUP
# =========================================================

def create_powerup():

    x = random.randint(20, WIDTH - 20)
    y = -30

    powerup = {
        "x": x,
        "y": y,
        "size": 28,
        "speed": 3
    }

    powerups.append(powerup)


# =========================================================
# CREATE PARTICLES
# =========================================================

def create_particles(x, y):

    for _ in range(15):

        particle = {
            "x": x,
            "y": y,
            "dx": random.uniform(-4, 4),
            "dy": random.uniform(-4, 4),
            "life": 30
        }

        particles.append(particle)


# =========================================================
# RESET GAME
# =========================================================

def reset_game():

    global blocks
    global coins
    global powerups
    global particles

    global score
    global lives

    global shield
    global shield_timer

    global game_over
    global paused

    global spawn_timer
    global coin_timer
    global powerup_timer

    global difficulty_timer

    global base_speed
    global spawn_delay

    global shake_timer

    player.x = WIDTH // 2 - PLAYER_WIDTH // 2
    player.y = HEIGHT - 90

    blocks = []
    coins = []
    powerups = []
    particles = []

    score = 0
    lives = 3

    shield = False
    shield_timer = 0

    game_over = False
    paused = False

    spawn_timer = 0
    coin_timer = 0
    powerup_timer = 0

    difficulty_timer = 0

    base_speed = 4
    spawn_delay = 35

    shake_timer = 0


# =========================================================
# DRAW TEXT
# =========================================================

def draw_text(text, font, color, x, y, center=False):

    surface = font.render(text, True, color)

    if center:

        rect = surface.get_rect(center=(x, y))

    else:

        rect = surface.get_rect(topleft=(x, y))

    screen.blit(surface, rect)


# =========================================================
# DRAW PLAYER
# =========================================================

def draw_player():

    pygame.draw.rect(
        screen,
        BLUE,
        player,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        CYAN,
        (
            player.x + 10,
            player.y + 8,
            12,
            12
        ),
        border_radius=4
    )

    # Shield
    if shield:

        pygame.draw.circle(
            screen,
            CYAN,
            player.center,
            38,
            3
        )


# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    clock.tick(FPS)

    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                running = False

            if event.key == pygame.K_p and not game_over:

                paused = not paused

            if event.key == pygame.K_r and game_over:

                reset_game()

    # =====================================================
    # GAME LOGIC
    # =====================================================

    if not game_over and not paused:

        # -------------------------------------------------
        # PLAYER MOVEMENT
        # -------------------------------------------------

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:

            player.x -= PLAYER_SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:

            player.x += PLAYER_SPEED

        if player.left < 0:

            player.left = 0

        if player.right > WIDTH:

            player.right = WIDTH

        # -------------------------------------------------
        # BLOCK SPAWNING
        # -------------------------------------------------

        spawn_timer += 1

        if spawn_timer >= spawn_delay:

            create_block()

            spawn_timer = 0

        # -------------------------------------------------
        # COIN SPAWNING
        # -------------------------------------------------

        coin_timer += 1

        if coin_timer >= 90:

            create_coin()

            coin_timer = 0

        # -------------------------------------------------
        # POWERUP SPAWNING
        # -------------------------------------------------

        powerup_timer += 1

        if powerup_timer >= 600:

            create_powerup()

            powerup_timer = 0

        # -------------------------------------------------
        # MOVE BLOCKS
        # -------------------------------------------------

        for block in blocks:

            rect = block["rect"]

            rect.y += block["speed"]

            # Moving block
            if block["type"] == "moving":

                rect.x += (
                    block["direction"]
                    * block["move_speed"]
                )

                if rect.left <= 0:

                    rect.left = 0
                    block["direction"] = 1

                if rect.right >= WIDTH:

                    rect.right = WIDTH
                    block["direction"] = -1

        # -------------------------------------------------
        # REMOVE BLOCKS
        # -------------------------------------------------

        blocks = [
            block
            for block in blocks
            if block["rect"].top < HEIGHT + 50
        ]

        # -------------------------------------------------
        # BLOCK COLLISION
        # -------------------------------------------------

        for block in blocks:

            rect = block["rect"]

            if player.colliderect(rect):

                if shield:

                    shield = False
                    shield_timer = 0

                    create_particles(
                        player.centerx,
                        player.centery
                    )

                    block["rect"].y = HEIGHT + 100

                else:

                    lives -= 1

                    shake_timer = 15

                    create_particles(
                        player.centerx,
                        player.centery
                    )

                    block["rect"].y = HEIGHT + 100

                    if lives <= 0:

                        game_over = True

                        if score > high_score:

                            high_score = score

        # -------------------------------------------------
        # BOMB EFFECT
        # -------------------------------------------------

        for block in blocks:

            if block["type"] == "bomb":

                explosion_radius = 50

                distance = math.sqrt(
                    (
                        player.centerx
                        - block["rect"].centerx
                    ) ** 2
                    +
                    (
                        player.centery
                        - block["rect"].centery
                    ) ** 2
                )

                if distance < explosion_radius:

                    if shield:

                        shield = False
                        block["rect"].y = HEIGHT + 100

                    else:

                        lives -= 1
                        shake_timer = 20

                        block["rect"].y = HEIGHT + 100

                        if lives <= 0:

                            game_over = True

        # -------------------------------------------------
        # COINS
        # -------------------------------------------------

        for coin in coins:

            coin["y"] += coin["speed"]

            distance = math.sqrt(
                (player.centerx - coin["x"]) ** 2
                +
                (player.centery - coin["y"]) ** 2
            )

            if distance < 35:

                score += 100

                coin["y"] = HEIGHT + 100

                create_particles(
                    coin["x"],
                    coin["y"]
                )

        coins = [
            coin
            for coin in coins
            if coin["y"] < HEIGHT + 50
        ]

        # -------------------------------------------------
        # POWERUPS
        # -------------------------------------------------

        for powerup in powerups:

            powerup["y"] += powerup["speed"]

            rect = pygame.Rect(
                powerup["x"] - 14,
                powerup["y"] - 14,
                28,
                28
            )

            if player.colliderect(rect):

                shield = True
                shield_timer = FPS * 8

                powerup["y"] = HEIGHT + 100

        powerups = [
            powerup
            for powerup in powerups
            if powerup["y"] < HEIGHT + 50
        ]

        # -------------------------------------------------
        # SHIELD TIMER
        # -------------------------------------------------

        if shield:

            shield_timer -= 1

            if shield_timer <= 0:

                shield = False

        # -------------------------------------------------
        # SCORE
        # -------------------------------------------------

        score += 1

        # -------------------------------------------------
        # DIFFICULTY
        # -------------------------------------------------

        difficulty_timer += 1

        if difficulty_timer >= FPS * 5:

            difficulty_timer = 0

            base_speed += 0.5

            if spawn_delay > 10:

                spawn_delay -= 2

        # -------------------------------------------------
        # PARTICLES
        # -------------------------------------------------

        for particle in particles:

            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]

            particle["life"] -= 1

        particles = [
            particle
            for particle in particles
            if particle["life"] > 0
        ]

    # =====================================================
    # DRAW
    # =====================================================

    screen.fill(BLACK)

    # Background grid
    for x in range(0, WIDTH, 50):

        pygame.draw.line(
            screen,
            (30, 30, 35),
            (x, 0),
            (x, HEIGHT)
        )

    for y in range(0, HEIGHT, 50):

        pygame.draw.line(
            screen,
            (30, 30, 35),
            (0, y),
            (WIDTH, y)
        )

    # -----------------------------------------------------
    # DRAW BLOCKS
    # -----------------------------------------------------

    for block in blocks:

        rect = block["rect"]

        pygame.draw.rect(
            screen,
            block["color"],
            rect,
            border_radius=8
        )

        if block["type"] == "bomb":

            pygame.draw.circle(
                screen,
                DARK_RED,
                rect.center,
                8
            )

            pygame.draw.line(
                screen,
                WHITE,
                rect.center,
                (
                    rect.centerx + 10,
                    rect.centery - 10
                ),
                2
            )

    # -----------------------------------------------------
    # DRAW COINS
    # -----------------------------------------------------

    for coin in coins:

        pygame.draw.circle(
            screen,
            YELLOW,
            (int(coin["x"]), int(coin["y"])),
            coin["radius"]
        )

        pygame.draw.circle(
            screen,
            ORANGE,
            (int(coin["x"]), int(coin["y"])),
            coin["radius"],
            3
        )

    # -----------------------------------------------------
    # DRAW POWERUPS
    # -----------------------------------------------------

    for powerup in powerups:

        x = int(powerup["x"])
        y = int(powerup["y"])

        pygame.draw.circle(
            screen,
            CYAN,
            (x, y),
            16
        )

        draw_text(
            "S",
            small_font,
            BLACK,
            x,
            y - 1,
            center=True
        )

    # -----------------------------------------------------
    # DRAW PARTICLES
    # -----------------------------------------------------

    for particle in particles:

        pygame.draw.circle(
            screen,
            ORANGE,
            (
                int(particle["x"]),
                int(particle["y"])
            ),
            3
        )

    # -----------------------------------------------------
    # DRAW PLAYER
    # -----------------------------------------------------

    draw_player()

    # -----------------------------------------------------
    # UI
    # -----------------------------------------------------

    draw_text(
        f"Score: {score // 10}",
        font,
        WHITE,
        20,
        15
    )

    draw_text(
        f"High: {high_score // 10}",
        font,
        YELLOW,
        20,
        50
    )

    draw_text(
        f"Lives: {'❤️' * lives}",
        font,
        WHITE,
        20,
        85
    )

    draw_text(
        f"Speed: {base_speed:.1f}",
        small_font,
        GRAY,
        WIDTH - 120,
        20
    )

    # -----------------------------------------------------
    # PAUSE
    # -----------------------------------------------------

    if paused:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT)
        )

        overlay.set_alpha(180)
        overlay.fill(BLACK)

        screen.blit(
            overlay,
            (0, 0)
        )

        draw_text(
            "PAUSED",
            big_font,
            YELLOW,
            WIDTH // 2,
            HEIGHT // 2 - 40,
            center=True
        )

        draw_text(
            "Press P to Resume",
            font,
            WHITE,
            WIDTH // 2,
            HEIGHT // 2 + 40,
            center=True
        )

    # -----------------------------------------------------
    # GAME OVER
    # -----------------------------------------------------

    if game_over:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT)
        )

        overlay.set_alpha(200)
        overlay.fill(BLACK)

        screen.blit(
            overlay,
            (0, 0)
        )

        draw_text(
            "GAME OVER",
            big_font,
            RED,
            WIDTH // 2,
            HEIGHT // 2 - 120,
            center=True
        )

        draw_text(
            f"Score: {score // 10}",
            font,
            WHITE,
            WIDTH // 2,
            HEIGHT // 2 - 30,
            center=True
        )

        draw_text(
            f"High Score: {high_score // 10}",
            font,
            YELLOW,
            WIDTH // 2,
            HEIGHT // 2 + 20,
            center=True
        )

        draw_text(
            "Press R to Restart",
            font,
            GREEN,
            WIDTH // 2,
            HEIGHT // 2 + 90,
            center=True
        )

    pygame.display.flip()

pygame.quit()