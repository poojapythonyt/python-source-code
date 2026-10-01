import pygame
import random
import math

pygame.init()

# =========================================================
# SCREEN
# =========================================================

WIDTH = 1000
HEIGHT = 650

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Castle Defense")

clock = pygame.time.Clock()

# =========================================================
# COLORS
# =========================================================

SKY = (135, 206, 235)
GRASS = (80, 170, 80)
ROAD = (190, 165, 115)

WHITE = (255, 255, 255)
BLACK = (25, 25, 25)

RED = (220, 50, 50)
DARK_RED = (150, 30, 30)

GREEN = (50, 200, 80)
DARK_GREEN = (30, 130, 50)

BLUE = (60, 120, 230)
DARK_BLUE = (35, 70, 160)

YELLOW = (255, 220, 40)
GOLD = (255, 175, 20)

BROWN = (120, 70, 35)
DARK_BROWN = (70, 40, 20)

STONE = (155, 155, 155)
DARK_STONE = (90, 90, 90)

PURPLE = (160, 70, 220)
ORANGE = (255, 140, 30)

# =========================================================
# FONTS
# =========================================================

font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 17)
big_font = pygame.font.SysFont("Arial", 52, bold=True)

# =========================================================
# CASTLE
# =========================================================

castle_rect = pygame.Rect(40, 300, 180, 250)

# Cannon starting point
CANNON_X = 220
CANNON_Y = 350

# =========================================================
# GAME VARIABLES
# =========================================================

castle_hp = 100
max_castle_hp = 100

coins = 0

wave = 1

damage = 25
bullet_speed = 12

damage_upgrade_cost = 50
speed_upgrade_cost = 50
repair_cost = 30

enemies = []
bullets = []
particles = []

spawn_timer = 0
wave_delay = 0

enemies_spawned = 0
enemies_to_spawn = 5

game_over = False
game_won = False

# Current cannon direction
cannon_angle = 0


# =========================================================
# RESET
# =========================================================

def reset_game():

    global castle_hp
    global coins
    global wave
    global damage
    global bullet_speed
    global damage_upgrade_cost
    global speed_upgrade_cost
    global repair_cost
    global enemies_spawned
    global enemies_to_spawn
    global spawn_timer
    global wave_delay
    global game_over
    global game_won
    global cannon_angle

    castle_hp = 100
    coins = 0

    wave = 1

    damage = 25
    bullet_speed = 12

    damage_upgrade_cost = 50
    speed_upgrade_cost = 50
    repair_cost = 30

    enemies_spawned = 0
    enemies_to_spawn = 5

    spawn_timer = 0
    wave_delay = 0

    game_over = False
    game_won = False

    cannon_angle = 0

    enemies.clear()
    bullets.clear()
    particles.clear()


# =========================================================
# CREATE ENEMY
# =========================================================

def create_enemy():

    enemy_type = random.choice(
        ["normal", "normal", "fast", "tank"]
    )

    if enemy_type == "normal":

        size = 36
        hp = 50 + wave * 10
        speed = 1.2 + wave * 0.12
        reward = 10

    elif enemy_type == "fast":

        size = 28
        hp = 35 + wave * 7
        speed = 2.4 + wave * 0.15
        reward = 15

    else:

        size = 50
        hp = 120 + wave * 20
        speed = 0.7 + wave * 0.08
        reward = 25

    enemy = {
        "x": WIDTH + 50,
        "y": random.randint(380, 510),
        "size": size,
        "hp": hp,
        "max_hp": hp,
        "speed": speed,
        "reward": reward,
        "type": enemy_type
    }

    enemies.append(enemy)


# =========================================================
# PARTICLES
# =========================================================

def create_particles(x, y):

    for _ in range(8):

        particles.append({
            "x": x,
            "y": y,
            "dx": random.uniform(-3, 3),
            "dy": random.uniform(-3, 3),
            "life": 25
        })


# =========================================================
# SHOOT BULLET
# =========================================================

def shoot_bullet(target_x, target_y):

    global cannon_angle

    dx = target_x - CANNON_X
    dy = target_y - CANNON_Y

    distance = math.sqrt(
        dx * dx + dy * dy
    )

    if distance == 0:
        return

    # Normalize direction
    dx /= distance
    dy /= distance

    # Store cannon direction
    cannon_angle = math.atan2(dy, dx)

    # Bullet starts slightly outside cannon
    start_x = CANNON_X + dx * 25
    start_y = CANNON_Y + dy * 25

    bullets.append({
        "x": start_x,
        "y": start_y,
        "dx": dx,
        "dy": dy
    })


# =========================================================
# DRAW CASTLE
# =========================================================

def draw_castle():

    # Main castle
    pygame.draw.rect(
        screen,
        STONE,
        castle_rect
    )

    # Left tower
    pygame.draw.rect(
        screen,
        DARK_STONE,
        (25, 250, 60, 300)
    )

    # Right tower
    pygame.draw.rect(
        screen,
        DARK_STONE,
        (175, 250, 60, 300)
    )

    # Tower tops
    pygame.draw.rect(
        screen,
        DARK_BROWN,
        (20, 235, 70, 35)
    )

    pygame.draw.rect(
        screen,
        DARK_BROWN,
        (170, 235, 70, 35)
    )

    # Roofs
    pygame.draw.polygon(
        screen,
        BROWN,
        [
            (20, 235),
            (55, 195),
            (90, 235)
        ]
    )

    pygame.draw.polygon(
        screen,
        BROWN,
        [
            (170, 235),
            (205, 195),
            (240, 235)
        ]
    )

    # Door
    pygame.draw.rect(
        screen,
        DARK_BROWN,
        (105, 440, 50, 110)
    )

    # Windows
    pygame.draw.rect(
        screen,
        BLUE,
        (50, 320, 25, 40)
    )

    pygame.draw.rect(
        screen,
        BLUE,
        (190, 320, 25, 40)
    )

    # Flag pole
    pygame.draw.line(
        screen,
        BLACK,
        (130, 300),
        (130, 145),
        5
    )

    # Flag
    pygame.draw.polygon(
        screen,
        RED,
        [
            (130, 145),
            (190, 170),
            (130, 195)
        ]
    )


# =========================================================
# DRAW CANNON
# =========================================================

def draw_cannon():

    # Cannon base
    pygame.draw.circle(
        screen,
        DARK_BROWN,
        (CANNON_X, CANNON_Y),
        28
    )

    # Cannon barrel length
    barrel_length = 45

    end_x = CANNON_X + math.cos(cannon_angle) * barrel_length
    end_y = CANNON_Y + math.sin(cannon_angle) * barrel_length

    pygame.draw.line(
        screen,
        BLACK,
        (CANNON_X, CANNON_Y),
        (int(end_x), int(end_y)),
        18
    )

    # Barrel highlight
    pygame.draw.line(
        screen,
        DARK_STONE,
        (CANNON_X, CANNON_Y),
        (int(end_x), int(end_y)),
        12
    )

    # Cannon center
    pygame.draw.circle(
        screen,
        BLACK,
        (CANNON_X, CANNON_Y),
        12
    )


# =========================================================
# DRAW ENEMY
# =========================================================

def draw_enemy(enemy):

    x = int(enemy["x"])
    y = int(enemy["y"])
    size = enemy["size"]

    if enemy["type"] == "normal":

        color = RED

    elif enemy["type"] == "fast":

        color = PURPLE

    else:

        color = DARK_RED

    pygame.draw.circle(
        screen,
        color,
        (x, y),
        size // 2
    )

    # Eyes
    pygame.draw.circle(
        screen,
        WHITE,
        (x - 8, y - 5),
        6
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (x + 8, y - 5),
        6
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (x - 8, y - 5),
        3
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (x + 8, y - 5),
        3
    )

    # HP bar background
    pygame.draw.rect(
        screen,
        BLACK,
        (
            x - size // 2,
            y - size // 2 - 15,
            size,
            7
        )
    )

    hp_width = int(
        size * enemy["hp"] / enemy["max_hp"]
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (
            x - size // 2,
            y - size // 2 - 15,
            hp_width,
            7
        )
    )


# =========================================================
# DRAW BULLET
# =========================================================

def draw_bullet(bullet):

    x = int(bullet["x"])
    y = int(bullet["y"])

    # Bullet
    pygame.draw.circle(
        screen,
        YELLOW,
        (x, y),
        7
    )

    # Bullet glow
    pygame.draw.circle(
        screen,
        ORANGE,
        (x, y),
        3
    )


# =========================================================
# DRAW PARTICLES
# =========================================================

def draw_particles():

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


# =========================================================
# DRAW UI
# =========================================================

def draw_ui():

    # Top panel
    pygame.draw.rect(
        screen,
        WHITE,
        (0, 0, WIDTH, 90)
    )

    # HP
    hp_label = font.render(
        "CASTLE HP",
        True,
        BLACK
    )

    screen.blit(
        hp_label,
        (20, 10)
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (20, 43, 220, 27)
    )

    hp_width = int(
        220 * castle_hp / max_castle_hp
    )

    hp_color = (
        GREEN
        if castle_hp > 30
        else RED
    )

    pygame.draw.rect(
        screen,
        hp_color,
        (20, 43, hp_width, 27)
    )

    hp_text = small_font.render(
        f"{castle_hp} / {max_castle_hp}",
        True,
        WHITE
    )

    screen.blit(
        hp_text,
        (105, 48)
    )

    # Coins
    coin_text = font.render(
        f"Coins: {coins}",
        True,
        BLACK
    )

    screen.blit(
        coin_text,
        (285, 30)
    )

    # Wave
    wave_text = font.render(
        f"Wave: {wave}/10",
        True,
        BLACK
    )

    screen.blit(
        wave_text,
        (455, 30)
    )

    # Stats
    damage_text = small_font.render(
        f"Damage: {damage}",
        True,
        BLACK
    )

    screen.blit(
        damage_text,
        (610, 15)
    )

    speed_text = small_font.render(
        f"Bullet Speed: {bullet_speed}",
        True,
        BLACK
    )

    screen.blit(
        speed_text,
        (610, 45)
    )


# =========================================================
# BUTTON
# =========================================================

def draw_button(rect, text, color):

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        BLACK,
        rect,
        2,
        border_radius=8
    )

    text_surface = small_font.render(
        text,
        True,
        WHITE
    )

    screen.blit(
        text_surface,
        (
            rect.centerx
            - text_surface.get_width() // 2,
            rect.centery
            - text_surface.get_height() // 2
        )
    )


damage_button = pygame.Rect(
    480,
    555,
    155,
    45
)

speed_button = pygame.Rect(
    645,
    555,
    155,
    45
)

repair_button = pygame.Rect(
    810,
    555,
    155,
    45
)


# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    clock.tick(60)

    # =====================================================
    # BACKGROUND
    # =====================================================

    screen.fill(SKY)

    pygame.draw.rect(
        screen,
        GRASS,
        (0, 90, WIDTH, 560)
    )

    # Enemy road
    pygame.draw.rect(
        screen,
        ROAD,
        (220, 350, 780, 200)
    )

    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Shoot
                if (
                    not game_over
                    and not game_won
                    and mouse_y > 90
                    and mouse_y < 550
                ):

                    shoot_bullet(
                        mouse_x,
                        mouse_y
                    )

                # Damage upgrade
                if damage_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    if (
                        coins >= damage_upgrade_cost
                        and not game_over
                        and not game_won
                    ):

                        coins -= damage_upgrade_cost

                        damage += 10

                        damage_upgrade_cost += 25

                # Speed upgrade
                if speed_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    if (
                        coins >= speed_upgrade_cost
                        and not game_over
                        and not game_won
                    ):

                        coins -= speed_upgrade_cost

                        bullet_speed += 2

                        speed_upgrade_cost += 25

                # Repair
                if repair_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    if (
                        coins >= repair_cost
                        and not game_over
                        and not game_won
                    ):

                        if castle_hp < max_castle_hp:

                            coins -= repair_cost

                            castle_hp += 20

                            if castle_hp > max_castle_hp:

                                castle_hp = max_castle_hp

                            repair_cost += 10

        # Keyboard
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:

                if game_over or game_won:

                    reset_game()


    # =====================================================
    # GAME LOGIC
    # =====================================================

    if not game_over and not game_won:

        # -------------------------------------------------
        # SPAWN ENEMIES
        # -------------------------------------------------

        if enemies_spawned < enemies_to_spawn:

            spawn_timer += 1

            if spawn_timer >= 55:

                create_enemy()

                enemies_spawned += 1

                spawn_timer = 0

        # -------------------------------------------------
        # MOVE BULLETS
        # -------------------------------------------------

        for bullet in bullets[:]:

            bullet["x"] += (
                bullet["dx"]
                * bullet_speed
            )

            bullet["y"] += (
                bullet["dy"]
                * bullet_speed
            )

            # Remove outside screen
            if (
                bullet["x"] < 0
                or bullet["x"] > WIDTH
                or bullet["y"] < 90
                or bullet["y"] > HEIGHT
            ):

                bullets.remove(bullet)

        # -------------------------------------------------
        # MOVE ENEMIES
        # -------------------------------------------------

        for enemy in enemies[:]:

            enemy["x"] -= enemy["speed"]

            # Enemy reaches castle
            if enemy["x"] < 230:

                castle_hp -= 10

                create_particles(
                    enemy["x"],
                    enemy["y"]
                )

                enemies.remove(enemy)

                if castle_hp <= 0:

                    castle_hp = 0

                    game_over = True

        # -------------------------------------------------
        # BULLET COLLISION
        # -------------------------------------------------

        for bullet in bullets[:]:

            bullet_rect = pygame.Rect(
                int(bullet["x"]) - 6,
                int(bullet["y"]) - 6,
                12,
                12
            )

            for enemy in enemies[:]:

                enemy_rect = pygame.Rect(
                    int(enemy["x"])
                    - enemy["size"] // 2,

                    int(enemy["y"])
                    - enemy["size"] // 2,

                    enemy["size"],
                    enemy["size"]
                )

                if bullet_rect.colliderect(
                    enemy_rect
                ):

                    enemy["hp"] -= damage

                    if bullet in bullets:

                        bullets.remove(bullet)

                    create_particles(
                        enemy["x"],
                        enemy["y"]
                    )

                    # Enemy defeated
                    if enemy["hp"] <= 0:

                        coins += enemy["reward"]

                        create_particles(
                            enemy["x"],
                            enemy["y"]
                        )

                        enemies.remove(enemy)

                    break

        # -------------------------------------------------
        # PARTICLES
        # -------------------------------------------------

        for particle in particles[:]:

            particle["x"] += particle["dx"]

            particle["y"] += particle["dy"]

            particle["life"] -= 1

            if particle["life"] <= 0:

                particles.remove(particle)

        # -------------------------------------------------
        # NEXT WAVE
        # -------------------------------------------------

        if (
            enemies_spawned >= enemies_to_spawn
            and len(enemies) == 0
        ):

            wave_delay += 1

            if wave_delay >= 100:

                wave += 1

                wave_delay = 0

                enemies_spawned = 0

                enemies_to_spawn = 5 + wave * 2

                if wave > 10:

                    game_won = True

    # =====================================================
    # DRAW
    # =====================================================

    draw_castle()

    draw_cannon()

    for enemy in enemies:

        draw_enemy(enemy)

    for bullet in bullets:

        draw_bullet(bullet)

    draw_particles()

    draw_ui()

    # Bottom instructions
    instruction = small_font.render(
        "CLICK anywhere to aim and shoot",
        True,
        BLACK
    )

    screen.blit(
        instruction,
        (20, 565)
    )

    draw_button(
        damage_button,
        f"Damage +10 ({damage_upgrade_cost})",
        DARK_RED
    )

    draw_button(
        speed_button,
        f"Speed +2 ({speed_upgrade_cost})",
        DARK_BLUE
    )

    draw_button(
        repair_button,
        f"Repair +20 ({repair_cost})",
        DARK_GREEN
    )

    # =====================================================
    # GAME OVER
    # =====================================================

    if game_over:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT)
        )

        overlay.set_alpha(180)

        overlay.fill(BLACK)

        screen.blit(
            overlay,
            (0, 0)
        )

        text = big_font.render(
            "CASTLE DESTROYED!",
            True,
            RED
        )

        screen.blit(
            text,
            (
                WIDTH // 2
                - text.get_width() // 2,
                220
            )
        )

        wave_text = font.render(
            f"You reached Wave {wave}",
            True,
            WHITE
        )

        screen.blit(
            wave_text,
            (
                WIDTH // 2
                - wave_text.get_width() // 2,
                290
            )
        )

        restart = font.render(
            "Press R to Restart",
            True,
            YELLOW
        )

        screen.blit(
            restart,
            (
                WIDTH // 2
                - restart.get_width() // 2,
                340
            )
        )

    # =====================================================
    # WIN
    # =====================================================

    if game_won:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT)
        )

        overlay.set_alpha(180)

        overlay.fill(BLACK)

        screen.blit(
            overlay,
            (0, 0)
        )

        text = big_font.render(
            "CASTLE SAVED!",
            True,
            YELLOW
        )

        screen.blit(
            text,
            (
                WIDTH // 2
                - text.get_width() // 2,
                220
            )
        )

        victory = font.render(
            "You survived all 10 waves!",
            True,
            WHITE
        )

        screen.blit(
            victory,
            (
                WIDTH // 2
                - victory.get_width() // 2,
                290
            )
        )

        restart = font.render(
            "Press R to Play Again",
            True,
            GREEN
        )

        screen.blit(
            restart,
            (
                WIDTH // 2
                - restart.get_width() // 2,
                340
            )
        )

    pygame.display.update()


pygame.quit()