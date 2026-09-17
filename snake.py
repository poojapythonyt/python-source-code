import pygame
import random

pygame.init()

# Screen
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Power-Up Snake")

clock = pygame.time.Clock()

# Colors
BLACK = (20, 20, 25)
WHITE = (255, 255, 255)
GREEN = (60, 220, 90)
RED = (240, 70, 70)
GOLD = (255, 210, 40)
BLUE = (70, 150, 255)
PURPLE = (180, 80, 220)
GRAY = (100, 100, 110)

font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 70)

CELL = 25

# Snake
snake = []
direction = (1, 0)
next_direction = (1, 0)

# Food
food = None
golden_food = None

# Power-ups
speed_power = None
magnet_power = None
shield_power = None

# Obstacles
obstacles = []

score = 0
lives = 3
high_score = 0

speed_boost = 0
magnet_active = 0
shield_active = False

game_over = False


def random_position():
    x = random.randrange(1, (WIDTH // CELL) - 1) * CELL
    y = random.randrange(2, (HEIGHT // CELL) - 1) * CELL
    return (x, y)


def create_food():
    global food

    while True:
        position = random_position()

        if position not in snake and position not in obstacles:
            food = position
            break


def create_obstacles():
    global obstacles

    obstacles = []

    for _ in range(8):

        position = random_position()

        if position not in snake:
            obstacles.append(position)


def create_power_up():

    global golden_food
    global speed_power
    global magnet_power
    global shield_power

    golden_food = None
    speed_power = None
    magnet_power = None
    shield_power = None

    power_type = random.choice(
        ["gold", "speed", "magnet", "shield"]
    )

    while True:

        position = random_position()

        if position not in snake and position not in obstacles and position != food:

            if power_type == "gold":
                golden_food = position

            elif power_type == "speed":
                speed_power = position

            elif power_type == "magnet":
                magnet_power = position

            elif power_type == "shield":
                shield_power = position

            break


def reset_game():

    global snake
    global direction
    global next_direction
    global score
    global lives
    global speed_boost
    global magnet_active
    global shield_active
    global game_over

    snake = [
        (400, 300),
        (375, 300),
        (350, 300)
    ]

    direction = (1, 0)
    next_direction = (1, 0)

    score = 0
    lives = 3

    speed_boost = 0
    magnet_active = 0
    shield_active = False

    game_over = False

    create_obstacles()
    create_food()
    create_power_up()


reset_game()

move_timer = 0


running = True

while running:

    clock.tick(60)

    # ---------------- EVENTS ----------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP and direction != (0, 1):
                next_direction = (0, -1)

            if event.key == pygame.K_DOWN and direction != (0, -1):
                next_direction = (0, 1)

            if event.key == pygame.K_LEFT and direction != (1, 0):
                next_direction = (-1, 0)

            if event.key == pygame.K_RIGHT and direction != (-1, 0):
                next_direction = (1, 0)

            if event.key == pygame.K_r and game_over:
                reset_game()

    # ---------------- GAME ----------------

    if not game_over:

        direction = next_direction

        move_delay = 110

        if speed_boost > 0:
            move_delay = 65
            speed_boost -= 1

        if magnet_active > 0:
            magnet_active -= 1

            # REAL MAGNET EFFECT:
            # Move the normal food one CELL closer to the snake head.
            if food is not None:
                head_x, head_y = snake[0]
                food_x, food_y = food

                dx = head_x - food_x
                dy = head_y - food_y

                # Move only if food is not already at the head.
                if dx != 0 or dy != 0:
                    if abs(dx) >= abs(dy):
                        food_x += CELL if dx > 0 else -CELL
                    else:
                        food_y += CELL if dy > 0 else -CELL

                    new_food = (food_x, food_y)

                    # Do not let magnet food move into the snake or an obstacle.
                    if new_food not in snake and new_food not in obstacles:
                        food = new_food

        move_timer += clock.get_time()

        if move_timer >= move_delay:

            move_timer = 0

            head_x, head_y = snake[0]

            new_head = (
                head_x + direction[0] * CELL,
                head_y + direction[1] * CELL
            )

            # Wall collision
            if (
                new_head[0] < 0
                or new_head[0] >= WIDTH
                or new_head[1] < 0
                or new_head[1] >= HEIGHT
            ):

                if shield_active:

                    shield_active = False

                else:

                    lives -= 1

                    if lives <= 0:
                        game_over = True

                    else:
                        snake = [
                            (400, 300),
                            (375, 300),
                            (350, 300)
                        ]

                    continue

            # Body collision
            if new_head in snake:

                if shield_active:

                    shield_active = False

                else:

                    lives -= 1

                    if lives <= 0:
                        game_over = True

                    else:
                        snake = [
                            (400, 300),
                            (375, 300),
                            (350, 300)
                        ]

                    continue

            # Obstacle collision
            if new_head in obstacles:

                if shield_active:

                    shield_active = False

                else:

                    lives -= 1

                    if lives <= 0:
                        game_over = True

                    else:
                        snake = [
                            (400, 300),
                            (375, 300),
                            (350, 300)
                        ]

                    continue

            snake.insert(0, new_head)

            ate_food = False

            # Normal food
            if new_head == food:

                score += 10
                ate_food = True

                create_food()

                if random.random() < 0.35:
                    create_power_up()

            # Golden food
            if golden_food is not None:

                if new_head == golden_food:

                    score += 50
                    ate_food = True

                    create_power_up()

            # Speed power
            if speed_power is not None:

                if new_head == speed_power:

                    speed_boost = 120
                    ate_food = True

                    create_power_up()

            # Magnet power
            if magnet_power is not None:

                if new_head == magnet_power:

                    magnet_active = 180
                    ate_food = True

                    create_power_up()

            # Shield power
            if shield_power is not None:

                if new_head == shield_power:

                    shield_active = True
                    ate_food = True

                    create_power_up()

            if not ate_food:

                snake.pop()

    # ---------------- DRAW ----------------

    screen.fill(BLACK)

    # Obstacles
    for block in obstacles:

        pygame.draw.rect(
            screen,
            GRAY,
            (
                block[0],
                block[1],
                CELL,
                CELL
            ),
            border_radius=5
        )

    # Normal food
    if food is not None:

        pygame.draw.circle(
            screen,
            RED,
            (
                food[0] + CELL // 2,
                food[1] + CELL // 2
            ),
            9
        )

    # Golden food
    if golden_food is not None:

        pygame.draw.circle(
            screen,
            GOLD,
            (
                golden_food[0] + CELL // 2,
                golden_food[1] + CELL // 2
            ),
            11
        )

    # Speed power
    if speed_power is not None:

        pygame.draw.circle(
            screen,
            BLUE,
            (
                speed_power[0] + CELL // 2,
                speed_power[1] + CELL // 2
            ),
            10
        )

    # Magnet power
    if magnet_power is not None:

        pygame.draw.circle(
            screen,
            PURPLE,
            (
                magnet_power[0] + CELL // 2,
                magnet_power[1] + CELL // 2
            ),
            10
        )

    # Shield power
    if shield_power is not None:

        pygame.draw.circle(
            screen,
            WHITE,
            (
                shield_power[0] + CELL // 2,
                shield_power[1] + CELL // 2
            ),
            10
        )

    # Snake
    for i, part in enumerate(snake):

        color = GREEN

        if i == 0:
            color = WHITE if shield_active else GREEN

        pygame.draw.rect(
            screen,
            color,
            (
                part[0],
                part[1],
                CELL - 2,
                CELL - 2
            ),
            border_radius=6
        )

    # Score
    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (20, 15)
    )

    # Lives
    lives_text = font.render(
        f"Lives: {lives}",
        True,
        RED
    )

    screen.blit(
        lives_text,
        (150, 15)
    )

    # Power status
    if speed_boost > 0:

        text = font.render(
            "SPEED BOOST!",
            True,
            BLUE
        )

        screen.blit(
            text,
            (300, 15)
        )

    if magnet_active > 0:

        text = font.render(
            "MAGNET!",
            True,
            PURPLE
        )

        screen.blit(
            text,
            (300, 45)
        )

    if shield_active:

        text = font.render(
            "SHIELD ACTIVE!",
            True,
            WHITE
        )

        screen.blit(
            text,
            (500, 15)
        )

    # Game Over
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

        if score > high_score:
            high_score = score

        game_text = big_font.render(
            "GAME OVER",
            True,
            RED
        )

        screen.blit(
            game_text,
            (
                WIDTH // 2 - game_text.get_width() // 2,
                HEIGHT // 2 - 80
            )
        )

        score_text = font.render(
            f"Final Score: {score}",
            True,
            WHITE
        )

        screen.blit(
            score_text,
            (
                WIDTH // 2 - score_text.get_width() // 2,
                HEIGHT // 2
            )
        )

        restart_text = font.render(
            "Press R to Restart",
            True,
            WHITE
        )

        screen.blit(
            restart_text,
            (
                WIDTH // 2 - restart_text.get_width() // 2,
                HEIGHT // 2 + 50
            )
        )

    pygame.display.update()


pygame.quit()