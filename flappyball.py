import pygame
import random

pygame.init()

# ---------------- SCREEN ----------------
WIDTH = 700
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Ball")

clock = pygame.time.Clock()

# ---------------- COLORS ----------------
SKY = (135, 206, 235)
WHITE = (255, 255, 255)
GREEN = (50, 180, 80)
DARK_GREEN = (30, 130, 55)
YELLOW = (255, 220, 50)
BLACK = (30, 30, 30)
RED = (230, 60, 60)

# ---------------- PLAYER ----------------
ball_x = 150
ball_y = 250

ball_radius = 18

velocity = 0
gravity = 0.45
jump = -8

# ---------------- PIPES ----------------
pipe_width = 70
pipe_gap = 150

pipe_x = WIDTH
pipe_speed = 4

gap_y = random.randint(120, 350)

# ---------------- GAME ----------------
score = 0
game_over = False

font = pygame.font.Font(None, 50)
big_font = pygame.font.Font(None, 75)

# ---------------- RESET ----------------
def reset_game():
    global ball_y
    global velocity
    global pipe_x
    global gap_y
    global pipe_speed
    global score
    global game_over

    ball_y = 250
    velocity = 0

    pipe_x = WIDTH
    gap_y = random.randint(120, 350)

    pipe_speed = 4
    score = 0

    game_over = False


# ---------------- MAIN LOOP ----------------
running = True

while running:

    clock.tick(60)

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Jump
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                if not game_over:
                    velocity = jump

                else:
                    reset_game()

        # Mouse jump
        if event.type == pygame.MOUSEBUTTONDOWN:

            if not game_over:
                velocity = jump

            else:
                reset_game()

    # ---------------- GAME UPDATE ----------------
    if not game_over:

        # Gravity
        velocity += gravity
        ball_y += velocity

        # Move pipe
        pipe_x -= pipe_speed

        # Pipe leaves screen
        if pipe_x + pipe_width < 0:

            pipe_x = WIDTH

            gap_y = random.randint(
                120,
                350
            )

            score += 1

            # Slowly increase speed
            pipe_speed += 0.2

        # ---------------- COLLISION ----------------

        ball_rect = pygame.Rect(
            ball_x - ball_radius,
            ball_y - ball_radius,
            ball_radius * 2,
            ball_radius * 2
        )

        top_pipe = pygame.Rect(
            pipe_x,
            0,
            pipe_width,
            gap_y - pipe_gap // 2
        )

        bottom_pipe = pygame.Rect(
            pipe_x,
            gap_y + pipe_gap // 2,
            pipe_width,
            HEIGHT
        )

        # Pipe collision
        if (
            ball_rect.colliderect(top_pipe)
            or ball_rect.colliderect(bottom_pipe)
        ):
            game_over = True

        # Top / bottom collision
        if ball_y - ball_radius <= 0:
            game_over = True

        if ball_y + ball_radius >= HEIGHT:
            game_over = True

    # ---------------- DRAW ----------------

    screen.fill(SKY)

    # Clouds
    pygame.draw.circle(
        screen,
        WHITE,
        (100, 80),
        25
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (130, 80),
        30
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (160, 80),
        22
    )

    # ---------------- PIPES ----------------

    pygame.draw.rect(
        screen,
        GREEN,
        (
            pipe_x,
            0,
            pipe_width,
            gap_y - pipe_gap // 2
        )
    )

    pygame.draw.rect(
        screen,
        DARK_GREEN,
        (
            pipe_x - 5,
            gap_y - pipe_gap // 2 - 20,
            pipe_width + 10,
            20
        )
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (
            pipe_x,
            gap_y + pipe_gap // 2,
            pipe_width,
            HEIGHT
        )
    )

    pygame.draw.rect(
        screen,
        DARK_GREEN,
        (
            pipe_x - 5,
            gap_y + pipe_gap // 2,
            pipe_width + 10,
            20
        )
    )

    # ---------------- BALL ----------------

    pygame.draw.circle(
        screen,
        YELLOW,
        (
            ball_x,
            int(ball_y)
        ),
        ball_radius
    )

    # Eyes
    pygame.draw.circle(
        screen,
        BLACK,
        (
            ball_x + 6,
            int(ball_y) - 5
        ),
        3
    )

    # ---------------- SCORE ----------------

    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (20, 20)
    )

    # ---------------- GAME OVER ----------------

    if game_over:

        over_text = big_font.render(
            "GAME OVER",
            True,
            RED
        )

        screen.blit(
            over_text,
            (
                WIDTH // 2
                - over_text.get_width() // 2,
                190
            )
        )

        final_text = font.render(
            f"Score: {score}",
            True,
            BLACK
        )

        screen.blit(
            final_text,
            (
                WIDTH // 2
                - final_text.get_width() // 2,
                270
            )
        )

        restart_text = font.render(
            "SPACE / CLICK = Restart",
            True,
            BLACK
        )

        screen.blit(
            restart_text,
            (
                WIDTH // 2
                - restart_text.get_width() // 2,
                330
            )
        )

    pygame.display.update()

pygame.quit()