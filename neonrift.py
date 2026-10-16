import math
import random
import sys
import pygame

pygame.init()

# ---------------- CONFIGURATION ----------------
WIDTH, HEIGHT = 1000, 650
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON RIFT | Cyber Escape")
clock = pygame.time.Clock()

BG = (5, 8, 24)
CYAN = (0, 245, 255)
PINK = (255, 40, 180)
RED = (255, 65, 85)
PURPLE = (140, 70, 255)
WHITE = (240, 250, 255)
GOLD = (255, 210, 60)

font = pygame.font.SysFont("consolas", 22, bold=True)
big_font = pygame.font.SysFont("consolas", 54, bold=True)
small_font = pygame.font.SysFont("consolas", 16)

# ---------------- GLOW EFFECTS ----------------
def glow_circle(surface, color, pos, radius):
    x, y = int(pos[0]), int(pos[1])
    for extra, alpha in [(18, 15), (12, 25), (6, 45)]:
        layer = pygame.Surface(
            (radius * 2 + extra * 2, radius * 2 + extra * 2),
            pygame.SRCALPHA
        )
        pygame.draw.circle(
            layer, (*color, alpha),
            (radius + extra, radius + extra), radius + extra
        )
        surface.blit(layer, (x - radius - extra, y - radius - extra))

    pygame.draw.circle(surface, color, (x, y), radius)


def neon_line(surface, color, start, end, width=2):
    pygame.draw.line(surface, color, start, end, width)


def draw_text(text, x, y, color=WHITE, font_obj=font):
    image = font_obj.render(text, True, color)
    screen.blit(image, (x, y))


# ---------------- BACKGROUND ----------------
stars = [
    [random.randrange(WIDTH), random.randrange(HEIGHT),
     random.choice([1, 1, 2, 3]), random.uniform(20, 100)]
    for _ in range(110)
]

particles = []
bullets = []
enemies = []
orbs = []

player_pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
player_vel = pygame.Vector2()
player_radius = 15

score = 0
health = 100
shield_energy = 100
game_over = False
paused = False
started = False
elapsed = 0
enemy_timer = 0
orb_timer = 0
shoot_timer = 0
shield_on = False


def reset_game():
    global player_pos, player_vel, particles, bullets, enemies, orbs
    global score, health, shield_energy, game_over, paused
    global elapsed, enemy_timer, orb_timer, shoot_timer, started

    player_pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
    player_vel = pygame.Vector2()
    particles = []
    bullets = []
    enemies = []
    orbs = []

    score = 0
    health = 100
    shield_energy = 100
    game_over = False
    paused = False
    elapsed = 0
    enemy_timer = 0
    orb_timer = 0
    shoot_timer = 0
    started = True


def burst(pos, color, count=12):
    for _ in range(count):
        angle = random.random() * math.tau
        speed = random.uniform(50, 240)
        particles.append({
            "pos": pygame.Vector2(pos),
            "vel": pygame.Vector2(math.cos(angle), math.sin(angle)) * speed,
            "life": random.uniform(0.2, 0.65),
            "maxlife": 0.65,
            "color": color,
            "size": random.randint(2, 5)
        })


def spawn_enemy():
    side = random.randrange(4)

    if side == 0:
        pos = pygame.Vector2(random.randrange(WIDTH), -25)
    elif side == 1:
        pos = pygame.Vector2(WIDTH + 25, random.randrange(HEIGHT))
    elif side == 2:
        pos = pygame.Vector2(random.randrange(WIDTH), HEIGHT + 25)
    else:
        pos = pygame.Vector2(-25, random.randrange(HEIGHT))

    kind = random.choices(["normal", "fast", "tank"], [65, 25, 10])[0]

    if kind == "fast":
        radius, hp, speed, color = 11, 1, 145, PINK
    elif kind == "tank":
        radius, hp, speed, color = 23, 4, 45, PURPLE
    else:
        radius, hp, speed, color = 16, 2, 75, RED

    enemies.append({
        "pos": pos,
        "radius": radius,
        "hp": hp,
        "speed": speed,
        "color": color
    })


def spawn_orb():
    orbs.append({
        "pos": pygame.Vector2(
            random.randint(35, WIDTH - 35),
            random.randint(70, HEIGHT - 35)
        ),
        "phase": random.random() * math.tau
    })


def draw_ship(pos, angle):
    # Triangle ship pointing toward the mouse
    forward = pygame.Vector2(math.cos(angle), math.sin(angle))
    side = pygame.Vector2(-forward.y, forward.x)

    tip = pos + forward * 23
    back_left = pos - forward * 15 + side * 12
    back_right = pos - forward * 15 - side * 12

    # Engine glow
    glow_circle(screen, CYAN, pos - forward * 17, 5)

    pygame.draw.polygon(
        screen, CYAN,
        [tip, back_left, back_right], 2
    )
    pygame.draw.polygon(
        screen, (10, 35, 60),
        [tip, back_left, back_right]
    )
    pygame.draw.polygon(
        screen, CYAN,
        [tip, back_left, back_right], 2
    )

    pygame.draw.circle(
        screen, WHITE,
        (int(pos.x), int(pos.y)), 4
    )


# ---------------- MAIN LOOP ----------------
reset_game()
started = False

while True:
    dt = min(clock.tick(FPS) / 1000, 0.033)
    elapsed += dt

    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_RETURN and not started:
                reset_game()

            elif event.key == pygame.K_r and game_over:
                reset_game()

            elif event.key == pygame.K_p and started and not game_over:
                paused = not paused

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not started:
                reset_game()

    # ---------------- UPDATE GAME ----------------
    if started and not game_over and not paused:
        keys = pygame.key.get_pressed()

        move = pygame.Vector2(
            int(keys[pygame.K_d] or keys[pygame.K_RIGHT])
            - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            int(keys[pygame.K_s] or keys[pygame.K_DOWN])
            - int(keys[pygame.K_w] or keys[pygame.K_UP])
        )

        if move.length_squared() > 0:
            move = move.normalize()

        player_vel = move * 270
        player_pos += player_vel * dt

        player_pos.x = max(22, min(WIDTH - 22, player_pos.x))
        player_pos.y = max(55, min(HEIGHT - 22, player_pos.y))

        # Shield drains while held; recharges when released
        shield_on = keys[pygame.K_SPACE] and shield_energy > 0

        if shield_on:
            shield_energy = max(0, shield_energy - 38 * dt)
        else:
            shield_energy = min(100, shield_energy + 18 * dt)

        # Shoot toward mouse
        shoot_timer -= dt

        if pygame.mouse.get_pressed()[0] and shoot_timer <= 0:
            direction = mouse_pos - player_pos

            if direction.length_squared() > 0:
                direction = direction.normalize()
                bullets.append({
                    "pos": player_pos + direction * 20,
                    "vel": direction * 560,
                    "life": 1.3
                })
                burst(player_pos + direction * 19, CYAN, 3)
                shoot_timer = 0.15

        # Increasing enemy waves
        enemy_timer -= dt

        if enemy_timer <= 0:
            spawn_enemy()
            enemy_timer = max(0.24, 0.95 - score * 0.002)

        # Collectible energy orbs
        orb_timer -= dt

        if orb_timer <= 0:
            spawn_orb()
            orb_timer = random.uniform(4, 7)

        # Update bullets
        for bullet in bullets[:]:
            bullet["pos"] += bullet["vel"] * dt
            bullet["life"] -= dt

            if (
                bullet["life"] <= 0
                or not screen.get_rect().inflate(80, 80).collidepoint(
                    bullet["pos"].x, bullet["pos"].y
                )
            ):
                bullets.remove(bullet)

        # Update enemies
        for enemy in enemies[:]:
            direction = player_pos - enemy["pos"]

            if direction.length_squared() > 0:
                direction = direction.normalize()

            enemy["pos"] += direction * (
                enemy["speed"] + min(score * 0.1, 45)
            ) * dt

            # Enemy collides with player
            distance = enemy["pos"].distance_to(player_pos)

            if distance < enemy["radius"] + player_radius:
                if shield_on:
                    burst(enemy["pos"], CYAN, 15)
                    enemies.remove(enemy)
                    score += 2
                    continue
                else:
                    health -= 25 * dt

            # Bullets damage enemies
            for bullet in bullets[:]:
                if enemy["pos"].distance_to(bullet["pos"]) < enemy["radius"] + 5:
                    enemy["hp"] -= 1

                    if bullet in bullets:
                        bullets.remove(bullet)

                    burst(bullet["pos"], enemy["color"], 4)

                    if enemy["hp"] <= 0:
                        burst(enemy["pos"], enemy["color"], 18)
                        enemies.remove(enemy)
                        score += 10
                    break

        # Collect energy orbs
        for orb in orbs[:]:
            orb["phase"] += dt * 3

            if orb["pos"].distance_to(player_pos) < 25:
                health = min(100, health + 18)
                shield_energy = min(100, shield_energy + 25)
                score += 5
                burst(orb["pos"], GOLD, 16)
                orbs.remove(orb)

        # Update particles
        for p in particles[:]:
            p["pos"] += p["vel"] * dt
            p["vel"] *= 0.96
            p["life"] -= dt

            if p["life"] <= 0:
                particles.remove(p)

        if health <= 0:
            health = 0
            game_over = True
            burst(player_pos, PINK, 45)

    else:
        # Continue particles fading on game over
        for p in particles[:]:
            p["pos"] += p["vel"] * dt
            p["vel"] *= 0.96
            p["life"] -= dt

            if p["life"] <= 0:
                particles.remove(p)

    # ---------------- DRAW BACKGROUND ----------------
    screen.fill(BG)

    # Perspective-style neon grid
    grid_offset = int((elapsed * 30) % 40)

    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (12, 29, 53), (x, 0), (x, HEIGHT))

    for y in range(-40, HEIGHT + 40, 40):
        yy = y + grid_offset
        pygame.draw.line(screen, (12, 29, 53), (0, yy), (WIDTH, yy))

    # Moving stars
    for star in stars:
        star[1] += star[3] * dt

        if star[1] > HEIGHT:
            star[0] = random.randrange(WIDTH)
            star[1] = 0

        pygame.draw.circle(
            screen, (65, 105, 145),
            (int(star[0]), int(star[1])), star[2]
        )

    # Energy orbs
    for orb in orbs:
        pos = orb["pos"]
        pulse = 8 + int(2 * math.sin(orb["phase"]))
        glow_circle(screen, GOLD, pos, pulse)

    # Enemies
    for enemy in enemies:
        pos = enemy["pos"]
        radius = enemy["radius"]
        color = enemy["color"]

        glow_circle(screen, color, pos, radius)

        pygame.draw.circle(
            screen, color,
            (int(pos.x), int(pos.y)), radius, 2
        )
        pygame.draw.circle(
            screen, WHITE,
            (int(pos.x), int(pos.y)), 4
        )

        # HP indicator for tougher enemies
        if enemy["hp"] > 1:
            pygame.draw.rect(
                screen, (70, 20, 40),
                (pos.x - radius, pos.y - radius - 8, radius * 2, 4)
            )
            pygame.draw.rect(
                screen, color,
                (pos.x - radius, pos.y - radius - 8,
                 radius * 2 * enemy["hp"] / 4, 4)
            )

    # Laser bullets
    for bullet in bullets:
        pos = bullet["pos"]
        glow_circle(screen, CYAN, pos, 4)

    # Player and shield
    if started and not game_over:
        aim = mouse_pos - player_pos
        angle = math.atan2(aim.y, aim.x)

        draw_ship(player_pos, angle)

        if shield_on:
            glow_circle(screen, CYAN, player_pos, 28)
            pygame.draw.circle(
                screen, CYAN,
                (int(player_pos.x), int(player_pos.y)), 29, 2
            )

    # Particles
    for p in particles:
        alpha = max(0, min(255, int(255 * p["life"] / p["maxlife"])))
        size = max(1, int(p["size"] * p["life"] / p["maxlife"]))

        layer = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(
            layer, (*p["color"], alpha),
            (size + 1, size + 1), size
        )
        screen.blit(layer, (int(p["pos"].x - size), int(p["pos"].y - size)))

    # ---------------- HUD ----------------
    pygame.draw.rect(screen, (12, 20, 42), (0, 0, WIDTH, 48))
    pygame.draw.line(screen, CYAN, (0, 48), (WIDTH, 48), 1)

    draw_text("NEON RIFT", 18, 12, CYAN)
    draw_text(f"SCORE {score}", 230, 12, WHITE)
    draw_text(f"TIME {int(elapsed)}s", 410, 12, WHITE)

    # Health bar
    draw_text("HP", 615, 13, RED, small_font)
    pygame.draw.rect(screen, (45, 20, 38), (650, 17, 130, 13))
    pygame.draw.rect(
        screen, RED,
        (650, 17, int(130 * health / 100), 13)
    )

    # Shield bar
    draw_text("SHIELD", 800, 13, CYAN, small_font)
    pygame.draw.rect(screen, (20, 35, 50), (870, 17, 105, 13))
    pygame.draw.rect(
        screen, CYAN,
        (870, 17, int(105 * shield_energy / 100), 13)
    )

    draw_text(
        "WASD/ARROWS: MOVE   MOUSE: AIM + SHOOT   SPACE: SHIELD   P: PAUSE",
        15, HEIGHT - 26, (130, 170, 205), small_font
    )

    if not started:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((2, 4, 18, 205))
        screen.blit(overlay, (0, 0))

        draw_text("NEON RIFT", 315, 205, CYAN, big_font)
        draw_text("CYBER ESCAPE", 365, 270, PINK)
        draw_text("SURVIVE THE DIGITAL VOID", 337, 320, WHITE, small_font)
        draw_text("PRESS ENTER OR CLICK TO START", 300, 385, GOLD, font)

    if paused and not game_over:
        draw_text("PAUSED", 420, 285, GOLD, big_font)
        draw_text("PRESS P TO RESUME", 390, 350, WHITE, small_font)

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 0, 20, 210))
        screen.blit(overlay, (0, 0))

        draw_text("SYSTEM FAILURE", 270, 220, PINK, big_font)
        draw_text(f"FINAL SCORE: {score}", 385, 300, WHITE)
        draw_text("PRESS R TO RETRY", 390, 360, CYAN)

    pygame.display.flip()
