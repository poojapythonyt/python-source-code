import pygame
import random
import math

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hard Magnet Collector")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 34)
big_font = pygame.font.Font(None, 70)

# Colors
BLACK = (12, 12, 22)
WHITE = (255, 255, 255)
RED = (240, 60, 60)
YELLOW = (255, 220, 40)
GOLD = (255, 170, 20)
BLUE = (60, 150, 255)
PURPLE = (180, 80, 230)
GREEN = (60, 220, 100)
ORANGE = (255, 130, 40)

# Player
player = pygame.Rect(
    WIDTH // 2 - 25,
    HEIGHT // 2 - 25,
    50,
    50
)

BASE_SPEED = 6

coins = []
bombs = []
powerups = []

score = 0
lives = 3

game_over = False

spawn_timer = 0
power_timer = 0

speed_boost = 0


# ---------------- CREATE OBJECTS ----------------

def create_coin():

    while True:

        x = random.randint(30, WIDTH - 30)
        y = random.randint(90, HEIGHT - 30)

        if math.hypot(
            x - player.centerx,
            y - player.centery
        ) > 100:

            break

    coin = {
        "x": float(x),
        "y": float(y),
        "gold": random.random() < 0.10,
        "dx": random.choice([-1, 1]) * random.uniform(0.5, 1.2),
        "dy": random.choice([-1, 1]) * random.uniform(0.5, 1.2)
    }

    coins.append(coin)


def create_bomb():

    while True:

        x = random.randint(30, WIDTH - 30)
        y = random.randint(90, HEIGHT - 30)

        if math.hypot(
            x - player.centerx,
            y - player.centery
        ) > 150:

            break

    bomb = {
        "rect": pygame.Rect(x, y, 30, 30),
        "dx": random.choice([-1, 1]) * random.uniform(1.5, 3),
        "dy": random.choice([-1, 1]) * random.uniform(1.5, 3)
    }

    bombs.append(bomb)


def create_powerup():

    x = random.randint(40, WIDTH - 40)
    y = random.randint(100, HEIGHT - 40)

    powerups.append(
        pygame.Rect(x, y, 30, 30)
    )


# ---------------- RESET ----------------

def reset_game():

    global score
    global lives
    global game_over
    global spawn_timer
    global power_timer
    global speed_boost

    coins.clear()
    bombs.clear()
    powerups.clear()

    player.center = (
        WIDTH // 2,
        HEIGHT // 2
    )

    score = 0
    lives = 3

    spawn_timer = 0
    power_timer = 0
    speed_boost = 0

    game_over = False

    # Starting objects
    for _ in range(10):
        create_coin()

    for _ in range(3):
        create_bomb()


reset_game()


# ---------------- MAIN LOOP ----------------

running = True

while running:

    dt = clock.tick(60)

    # ---------------- EVENTS ----------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r and game_over:
                reset_game()

    # ---------------- GAME ----------------

    if not game_over:

        # Difficulty
        difficulty = 1 + score // 100

        # Player speed
        player_speed = BASE_SPEED

        if speed_boost > 0:

            player_speed = 11
            speed_boost -= dt

        # Movement
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            player.x -= player_speed

        if keys[pygame.K_RIGHT]:
            player.x += player_speed

        if keys[pygame.K_UP]:
            player.y -= player_speed

        if keys[pygame.K_DOWN]:
            player.y += player_speed

        # Keep player inside screen
        player.left = max(player.left, 0)
        player.right = min(player.right, WIDTH)

        player.top = max(player.top, 70)
        player.bottom = min(player.bottom, HEIGHT)

        # ---------------- SPAWNING ----------------

        spawn_timer += dt

        spawn_delay = max(
            350,
            900 - difficulty * 50
        )

        if spawn_timer >= spawn_delay:

            create_coin()

            # More bombs at higher scores
            bomb_chance = min(
                0.8,
                0.25 + difficulty * 0.08
            )

            if random.random() < bomb_chance:
                create_bomb()

            spawn_timer = 0

        # Power-up spawn
        power_timer += dt

        if power_timer >= 7000:

            create_powerup()

            power_timer = 0

        # ---------------- COINS ----------------

        for coin in coins[:]:

            # Move coin
            coin["x"] += coin["dx"] * (
                1 + difficulty * 0.08
            )

            coin["y"] += coin["dy"] * (
                1 + difficulty * 0.08
            )

            # Bounce from walls
            if coin["x"] < 20 or coin["x"] > WIDTH - 20:
                coin["dx"] *= -1

            if coin["y"] < 80 or coin["y"] > HEIGHT - 20:
                coin["dy"] *= -1

            # Magnet effect
            distance = math.hypot(
                player.centerx - coin["x"],
                player.centery - coin["y"]
            )

            magnet_range = max(
                70,
                130 - difficulty * 5
            )

            if distance < magnet_range:

                if distance > 0:

                    pull = 2.5

                    coin["x"] += (
                        player.centerx - coin["x"]
                    ) / distance * pull

                    coin["y"] += (
                        player.centery - coin["y"]
                    ) / distance * pull

            coin_rect = pygame.Rect(
                int(coin["x"] - 10),
                int(coin["y"] - 10),
                20,
                20
            )

            # Collect
            if player.colliderect(coin_rect):

                if coin["gold"]:

                    score += 50

                else:

                    score += 10

                coins.remove(coin)

        # ---------------- BOMBS ----------------

        for bomb in bombs[:]:

            bomb["rect"].x += int(
                bomb["dx"] * (1 + difficulty * 0.12)
            )

            bomb["rect"].y += int(
                bomb["dy"] * (1 + difficulty * 0.12)
            )

            # Bounce
            if (
                bomb["rect"].left <= 0
                or bomb["rect"].right >= WIDTH
            ):
                bomb["dx"] *= -1

            if (
                bomb["rect"].top <= 70
                or bomb["rect"].bottom >= HEIGHT
            ):
                bomb["dy"] *= -1

            # Collision
            if player.colliderect(bomb["rect"]):

                lives -= 1

                bombs.remove(bomb)

                if lives <= 0:

                    game_over = True

        # ---------------- POWER-UP ----------------

        for power in powerups[:]:

            if player.colliderect(power):

                speed_boost = 5000

                powerups.remove(power)

    # ---------------- DRAW ----------------

    screen.fill(BLACK)

    # Background stars
    for i in range(55):

        x = (i * 83) % WIDTH
        y = (i * 47) % HEIGHT

        pygame.draw.circle(
            screen,
            WHITE,
            (x, y),
            1
        )

    # Coins
    for coin in coins:

        color = GOLD if coin["gold"] else YELLOW

        radius = 12 if coin["gold"] else 8

        pygame.draw.circle(
            screen,
            color,
            (
                int(coin["x"]),
                int(coin["y"])
            ),
            radius
        )

    # Bombs
    for bomb in bombs:

        pygame.draw.circle(
            screen,
            RED,
            bomb["rect"].center,
            15
        )

        pygame.draw.circle(
            screen,
            BLACK,
            bomb["rect"].center,
            5
        )

    # Power-ups
    for power in powerups:

        pygame.draw.circle(
            screen,
            PURPLE,
            power.center,
            15
        )

        pygame.draw.line(
            screen,
            WHITE,
            (
                power.centerx - 7,
                power.centery
            ),
            (
                power.centerx + 7,
                power.centery
            ),
            3
        )

    # Player
    pygame.draw.circle(
        screen,
        BLUE,
        player.center,
        25
    )

    # Magnet
    pygame.draw.arc(
        screen,
        RED,
        (
            player.x - 10,
            player.y - 5,
            50,
            50
        ),
        math.pi,
        math.pi * 2,
        6
    )

    # HUD
    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (20, 20)
    )

    lives_text = font.render(
        f"Lives: {lives}",
        True,
        RED
    )

    screen.blit(
        lives_text,
        (200, 20)
    )

    # Difficulty
    difficulty_text = font.render(
        f"Level: {1 + score // 100}",
        True,
        ORANGE
    )

    screen.blit(
        difficulty_text,
        (330, 20)
    )

    # Speed boost
    if speed_boost > 0:

        boost_text = font.render(
            "SPEED BOOST!",
            True,
            PURPLE
        )

        screen.blit(
            boost_text,
            (500, 20)
        )

    # Instructions
    instructions = font.render(
        "Arrow Keys = Move",
        True,
        WHITE
    )

    screen.blit(
        instructions,
        (300, HEIGHT - 35)
    )

    # ---------------- GAME OVER ----------------

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

        game_text = big_font.render(
            "GAME OVER",
            True,
            RED
        )

        screen.blit(
            game_text,
            (
                WIDTH // 2 -
                game_text.get_width() // 2,
                HEIGHT // 2 - 90
            )
        )

        final_text = font.render(
            f"Final Score: {score}",
            True,
            WHITE
        )

        screen.blit(
            final_text,
            (
                WIDTH // 2 -
                final_text.get_width() // 2,
                HEIGHT // 2
            )
        )

        restart_text = font.render(
            "Press R to Restart",
            True,
            YELLOW
        )

        screen.blit(
            restart_text,
            (
                WIDTH // 2 -
                restart_text.get_width() // 2,
                HEIGHT // 2 + 50
            )
        )

    pygame.display.update()


pygame.quit()