
import pygame
import random
import math
import sys

pygame.init()

# ---------- SETTINGS ----------
W, H = 1000, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("SHADOW NINJA")
clock = pygame.time.Clock()

WHITE = (245, 245, 255)
CYAN = (40, 240, 255)
PURPLE = (150, 70, 255)
PINK = (255, 50, 170)
GOLD = (255, 215, 60)
DARK = (10, 10, 27)

font = pygame.font.SysFont("consolas", 24, bold=True)
big_font = pygame.font.SysFont("consolas", 48, bold=True)

GRAVITY = 1700
WORLD_WIDTH = 4000
JUMP_SPEED = 700
JUMP_BUFFER_TIME = 0.15
COYOTE_TIME = 0.10

# ---------- WORLD ----------
platforms = [
    pygame.Rect(0, 550, 600, 50),
    pygame.Rect(700, 480, 250, 30),
    pygame.Rect(1050, 410, 250, 30),
    pygame.Rect(1400, 500, 350, 30),
    pygame.Rect(1850, 430, 260, 30),
    pygame.Rect(2200, 350, 260, 30),
    pygame.Rect(2550, 470, 300, 30),
    pygame.Rect(2950, 400, 300, 30),
    pygame.Rect(3350, 500, 650, 100),
]

# ---------- GAME OBJECTS ----------
player = pygame.Rect(100, 450, 34, 48)
player_vel_y = 0
on_ground = False
coyote_timer = 0
jump_buffer_timer = 0
facing = 1

health = 100
score = 0
coins_collected = 0
attack_timer = 0
invincible_timer = 0
camera_x = 0

enemies = [
    {"rect": pygame.Rect(400, 500, 32, 40),
     "left": 320, "right": 550, "speed": 110, "hp": 2},
    {"rect": pygame.Rect(800, 430, 32, 40),
     "left": 720, "right": 900, "speed": 130, "hp": 2},
    {"rect": pygame.Rect(1150, 360, 32, 40),
     "left": 1070, "right": 1250, "speed": 150, "hp": 3},
    {"rect": pygame.Rect(1500, 450, 32, 40),
     "left": 1430, "right": 1650, "speed": 160, "hp": 3},
    {"rect": pygame.Rect(1950, 390, 32, 40),
     "left": 1870, "right": 2050, "speed": 175, "hp": 3},
    {"rect": pygame.Rect(2650, 420, 32, 40),
     "left": 2580, "right": 2800, "speed": 190, "hp": 4},
    {"rect": pygame.Rect(3450, 450, 40, 50),
     "left": 3400, "right": 3750, "speed": 200, "hp": 8},
]

coins = []
for x, y in [
    (220, 500), (480, 500), (780, 430),
    (1130, 360), (1230, 360), (1510, 450),
    (1940, 380), (2300, 300), (2660, 420),
    (3040, 350), (3500, 450), (3650, 450)
]:
    coins.append(pygame.Rect(x, y, 20, 20))

particles = []
game_over = False
victory = False
started = False
attack_flash = 0


def burst(x, y, color, count=12):
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(60, 260)
        particles.append([
            float(x), float(y),
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            random.uniform(0.25, 0.65),
            color
        ])


def draw_glow(surface, x, y, radius, color):
    for r, alpha in [(radius + 12, 25), (radius + 6, 45)]:
        glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow, (*color, alpha), (r, r), r
        )
        surface.blit(glow, (int(x - r), int(y - r)))

    pygame.draw.circle(
        surface, color, (int(x), int(y)), radius
    )


def draw_ninja(x, y, direction):
    # Shadow
    pygame.draw.ellipse(
        screen, (25, 15, 45),
        (x - 8, y + 43, 50, 10)
    )

    # Legs
    pygame.draw.line(
        screen, (35, 30, 65),
        (x + 14, y + 34), (x + 7, y + 46), 7
    )
    pygame.draw.line(
        screen, (35, 30, 65),
        (x + 24, y + 34), (x + 30, y + 46), 7
    )

    # Body
    pygame.draw.rect(
        screen, (30, 25, 58),
        (x + 7, y + 16, 24, 23),
        border_radius=6
    )
    pygame.draw.rect(
        screen, PURPLE,
        (x + 7, y + 16, 24, 23), 2,
        border_radius=6
    )

    # Head and mask
    pygame.draw.circle(
        screen, (22, 20, 42), (x + 19, y + 12), 15
    )
    pygame.draw.arc(
        screen, PINK,
        (x + 4, y - 3, 30, 30), math.pi, math.tau, 3
    )

    # Glowing eyes
    eye_x = x + (24 if direction == 1 else 13)
    draw_glow(screen, eye_x, y + 10, 3, CYAN)

    # Scarf
    scarf_end = x - 16 if direction == 1 else x + 45
    pygame.draw.line(
        screen, PINK,
        (x + 12, y + 19), (scarf_end, y + 26), 5
    )

    # Sword
    sword_start = (x + 28, y + 22)
    sword_end = (x + 43 * direction, y + 8)

    pygame.draw.line(
        screen, CYAN, sword_start, sword_end, 3
    )


def reset():
    global player, player_vel_y, on_ground, facing
    global coyote_timer, jump_buffer_timer
    global health, score, coins_collected, attack_timer
    global invincible_timer, camera_x, enemies, coins
    global particles, game_over, victory, started, attack_flash

    player = pygame.Rect(100, 450, 34, 48)
    player_vel_y = 0
    on_ground = False
    coyote_timer = 0
    jump_buffer_timer = 0
    facing = 1

    health = 100
    score = 0
    coins_collected = 0
    attack_timer = 0
    invincible_timer = 0
    camera_x = 0
    attack_flash = 0

    enemies = [
        {"rect": pygame.Rect(400, 500, 32, 40),
         "left": 320, "right": 550, "speed": 110, "hp": 2},
        {"rect": pygame.Rect(800, 430, 32, 40),
         "left": 720, "right": 900, "speed": 130, "hp": 2},
        {"rect": pygame.Rect(1150, 360, 32, 40),
         "left": 1070, "right": 1250, "speed": 150, "hp": 3},
        {"rect": pygame.Rect(1500, 450, 32, 40),
         "left": 1430, "right": 1650, "speed": 160, "hp": 3},
        {"rect": pygame.Rect(1950, 390, 32, 40),
         "left": 1870, "right": 2050, "speed": 175, "hp": 3},
        {"rect": pygame.Rect(2650, 420, 32, 40),
         "left": 2580, "right": 2800, "speed": 190, "hp": 4},
        {"rect": pygame.Rect(3450, 450, 40, 50),
         "left": 3400, "right": 3750, "speed": 200, "hp": 8},
    ]

    coins = [
        pygame.Rect(x, y, 20, 20)
        for x, y in [
            (220, 500), (480, 500), (780, 430),
            (1130, 360), (1230, 360), (1510, 450),
            (1940, 380), (2300, 300), (2660, 420),
            (3040, 350), (3500, 450), (3650, 450)
        ]
    ]

    particles = []
    game_over = False
    victory = False
    started = True


# ---------- MAIN LOOP ----------
while True:
    dt = min(clock.tick(60) / 1000, 0.033)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if not started and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                reset()

            elif (game_over or victory) and event.key == pygame.K_r:
                reset()

            elif (
                started and not game_over and not victory
                and event.key in (pygame.K_SPACE, pygame.K_w,
                                  pygame.K_UP)
            ):
                jump_buffer_timer = JUMP_BUFFER_TIME

            elif (
                started and not game_over and not victory
                and event.key == pygame.K_j and attack_timer <= 0
            ):
                attack_timer = 0.30
                attack_flash = 0.18

    keys = pygame.key.get_pressed()

    if started and not game_over and not victory:
        if on_ground:
            coyote_timer = COYOTE_TIME
        else:
            coyote_timer = max(0, coyote_timer - dt)

        jump_buffer_timer = max(0, jump_buffer_timer - dt)
        if jump_buffer_timer > 0 and (on_ground or coyote_timer > 0):
            player_vel_y = -JUMP_SPEED
            on_ground = False
            coyote_timer = 0
            jump_buffer_timer = 0

        # Movement
        dx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 280 * dt
            facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 280 * dt
            facing = 1

        player.x += int(dx)
        player.x = max(0, min(WORLD_WIDTH - player.width, player.x))

        # Horizontal collisions
        for platform in platforms:
            if player.colliderect(platform):
                if dx > 0:
                    player.right = platform.left
                elif dx < 0:
                    player.left = platform.right

        # Gravity + reliable vertical collision detection.
        # Keep the previous bottom so fast falls cannot pass through platforms.
        previous_bottom = player.bottom
        player_vel_y += GRAVITY * dt
        vertical_step = int(player_vel_y * dt)
        if vertical_step == 0 and player_vel_y != 0:
            vertical_step = 1 if player_vel_y > 0 else -1
        player.y += vertical_step
        on_ground = False

        for platform in platforms:
            horizontally_overlapping = (
                player.right > platform.left and player.left < platform.right
            )

            # Landing while moving down: detect crossing the platform top.
            if (player_vel_y >= 0 and horizontally_overlapping
                    and previous_bottom <= platform.top
                    and player.bottom >= platform.top):
                player.bottom = platform.top
                player_vel_y = 0
                on_ground = True

            # Hitting the underside while moving up.
            elif (player_vel_y < 0 and horizontally_overlapping
                    and player.top < platform.bottom
                    and player.bottom > platform.bottom):
                player.top = platform.bottom
                player_vel_y = 0

        # Falling off the world
        if player.top > H + 100:
            health = 0
            game_over = True

        attack_timer = max(0, attack_timer - dt)
        attack_flash = max(0, attack_flash - dt)
        invincible_timer = max(0, invincible_timer - dt)

        # Sword attack: press J
        if attack_timer > 0:
            sword_box = pygame.Rect(
                player.centerx + (15 if facing == 1 else -75),
                player.y + 8, 60, 35
            )

            for enemy in enemies[:]:
                if sword_box.colliderect(enemy["rect"]):
                    enemy["hp"] -= 1
                    burst(
                        enemy["rect"].centerx,
                        enemy["rect"].centery, CYAN, 5
                    )

                    if enemy["hp"] <= 0:
                        burst(
                            enemy["rect"].centerx,
                            enemy["rect"].centery, PINK, 18
                        )
                        enemies.remove(enemy)
                        score += 100

        # Enemy movement and contact damage
        for enemy in enemies:
            rect = enemy["rect"]
            rect.x += int(enemy["speed"] * dt)

            if rect.right >= enemy["right"]:
                enemy["speed"] = -abs(enemy["speed"])
            elif rect.left <= enemy["left"]:
                enemy["speed"] = abs(enemy["speed"])

            if player.colliderect(rect) and invincible_timer <= 0:
                health -= 20
                invincible_timer = 0.8
                burst(player.centerx, player.centery, PINK, 12)

        # Coin collection
        for coin in coins[:]:
            if player.colliderect(coin):
                coins.remove(coin)
                coins_collected += 1
                score += 50
                burst(coin.centerx, coin.centery, GOLD, 12)

        # Update particles
        for p in particles[:]:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[4] -= dt

            if p[4] <= 0:
                particles.remove(p)

        # Camera follows player
        camera_x = max(
            0, min(WORLD_WIDTH - W, player.centerx - W // 2)
        )

        if health <= 0:
            health = 0
            game_over = True

        # Reach the final area to win
        if player.x >= 3900:
            victory = True

    # ---------- DRAW ----------
    screen.fill(DARK)

    # Moon
    draw_glow(screen, 820, 110, 30, PURPLE)
    pygame.draw.circle(screen, (215, 205, 255), (820, 110), 23)

    # Parallax city
    for i in range(18):
        bx = i * 100 - int(camera_x * 0.25) % 100
        bh = 100 + (i * 37 % 120)

        pygame.draw.rect(
            screen, (20, 18, 48),
            (bx, 500 - bh, 65, bh)
        )

        for wy in range(500 - bh + 12, 490, 22):
            for wx in range(bx + 10, bx + 55, 20):
                pygame.draw.rect(
                    screen, (70, 50, 110),
                    (wx, wy, 5, 8)
                )

    # Platforms
    for platform in platforms:
        rect = platform.move(-camera_x, 0)

        if rect.right < 0 or rect.left > W:
            continue

        pygame.draw.rect(screen, (25, 22, 55), rect)
        pygame.draw.line(
            screen, CYAN,
            (rect.left, rect.top),
            (rect.right, rect.top), 3
        )
        pygame.draw.line(
            screen, PURPLE,
            (rect.left, rect.bottom),
            (rect.right, rect.bottom), 2
        )

    # Coins
    for coin in coins:
        cx = coin.centerx - camera_x
        cy = coin.centery + math.sin(pygame.time.get_ticks() * 0.006 + coin.x) * 4

        if -30 < cx < W + 30:
            draw_glow(screen, cx, cy, 9, GOLD)
            pygame.draw.circle(
                screen, WHITE, (int(cx), int(cy)), 4
            )

    # Enemies
    for enemy in enemies:
        rect = enemy["rect"].move(-camera_x, 0)

        if -60 < rect.x < W + 60:
            draw_glow(
                screen, rect.centerx, rect.centery,
                13, PINK
            )
            pygame.draw.rect(
                screen, (45, 20, 55), rect,
                border_radius=6
            )
            pygame.draw.rect(
                screen, PINK, rect, 2,
                border_radius=6
            )
            pygame.draw.circle(
                screen, CYAN,
                (rect.centerx, rect.y + 12), 4
            )

    # Player flickers briefly after taking damage
    px = player.x - camera_x

    if invincible_timer <= 0 or int(invincible_timer * 12) % 2 == 0:
        draw_ninja(px, player.y, facing)

    # Sword slash
    if attack_flash > 0:
        start = (
            px + (28 if facing == 1 else 6),
            player.y + 24
        )
        end = (
            px + (75 if facing == 1 else -40),
            player.y + 5
        )

        pygame.draw.line(screen, WHITE, start, end, 5)
        pygame.draw.line(screen, CYAN, start, end, 2)

    # Particles
    for p in particles:
        sx = int(p[0] - camera_x)
        sy = int(p[1])

        if -10 < sx < W + 10:
            radius = max(1, int(4 * p[4] / 0.65))
            pygame.draw.circle(
                screen, p[5], (sx, sy), radius
            )

    # HUD
    pygame.draw.rect(screen, (12, 12, 35), (0, 0, W, 55))
    pygame.draw.line(screen, CYAN, (0, 55), (W, 55), 2)

    screen.blit(font.render("SHADOW NINJA", True, CYAN), (18, 14))
    screen.blit(font.render(f"SCORE: {score}", True, WHITE), (280, 14))
    screen.blit(font.render(f"COINS: {coins_collected}", True, GOLD), (490, 14))

    pygame.draw.rect(screen, (60, 20, 45), (760, 20, 160, 16))
    pygame.draw.rect(
        screen, PINK,
        (760, 20, int(160 * health / 100), 16)
    )
    screen.blit(small if False else font.render("HP", True, WHITE), (720, 14))

    screen.blit(
        pygame.font.SysFont("consolas", 15).render(
            "MOVE: A/D   JUMP: SPACE   ATTACK: J",
            True, WHITE
        ),
        (20, H - 28)
    )

    # Start screen
    if not started:
        pygame.draw.rect(screen, (8, 8, 25), (180, 160, 640, 270))
        screen.blit(big_font.render("SHADOW NINJA", True, CYAN), (240, 195))
        screen.blit(font.render("RUN • JUMP • FIGHT • COLLECT", True, PINK), (300, 270))
        screen.blit(font.render("PRESS ENTER OR SPACE TO START", True, GOLD), (270, 330))
        screen.blit(pygame.font.SysFont("consolas", 18).render("Move: A/D or arrows | Jump: SPACE/W/UP | Attack: J", True, WHITE), (245, 375))

    if game_over or victory:
        pygame.draw.rect(screen, (8, 8, 25), (240, 180, 520, 230))

        title = "MISSION COMPLETE!" if victory else "GAME OVER"
        color = GOLD if victory else PINK

        screen.blit(big_font.render(title, True, color), (275, 220))
        screen.blit(
            font.render(f"FINAL SCORE: {score}", True, WHITE),
            (385, 290)
        )
        screen.blit(
            font.render("PRESS R TO RESTART", True, CYAN),
            (345, 345)
        )

    pygame.display.flip()
