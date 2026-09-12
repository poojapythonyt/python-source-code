import pygame
import random

pygame.init()

# Screen
WIDTH = 800
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Ping Pong")

clock = pygame.time.Clock()

# Colors
BLACK = (20, 20, 25)
WHITE = (255, 255, 255)
RED = (255, 70, 70)
BLUE = (70, 150, 255)
YELLOW = (255, 220, 60)

# Fonts
font = pygame.font.Font(None, 55)
big_font = pygame.font.Font(None, 80)

# Paddle settings
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100

# Player paddle
player = pygame.Rect(
    30,
    HEIGHT // 2 - PADDLE_HEIGHT // 2,
    PADDLE_WIDTH,
    PADDLE_HEIGHT
)

# Computer paddle
computer = pygame.Rect(
    WIDTH - 45,
    HEIGHT // 2 - PADDLE_HEIGHT // 2,
    PADDLE_WIDTH,
    PADDLE_HEIGHT
)

paddle_speed = 7
computer_speed = 5

# Ball
ball = pygame.Rect(
    WIDTH // 2 - 10,
    HEIGHT // 2 - 10,
    20,
    20
)

ball_speed_x = 6
ball_speed_y = 5

# Scores
player_score = 0
computer_score = 0

winning_score = 10

game_over = False


def reset_ball(direction):
    global ball_speed_x, ball_speed_y

    ball.center = (WIDTH // 2, HEIGHT // 2)

    ball_speed_x = 6 * direction
    ball_speed_y = random.choice([-5, 5])


def reset_game():
    global player_score, computer_score, game_over

    player_score = 0
    computer_score = 0

    player.centery = HEIGHT // 2
    computer.centery = HEIGHT // 2

    game_over = False

    reset_ball(random.choice([-1, 1]))


# Start game
reset_game()

running = True

while running:

    clock.tick(60)

    # ---------------- EVENTS ----------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r and game_over:
                reset_game()

    # ---------------- GAME LOGIC ----------------

    if not game_over:

        keys = pygame.key.get_pressed()

        # Player movement
        if keys[pygame.K_UP] and player.top > 0:
            player.y -= paddle_speed

        if keys[pygame.K_DOWN] and player.bottom < HEIGHT:
            player.y += paddle_speed

        # Computer AI
        if computer.centery < ball.centery:
            computer.y += computer_speed

        if computer.centery > ball.centery:
            computer.y -= computer_speed

        # Keep computer inside screen
        if computer.top < 0:
            computer.top = 0

        if computer.bottom > HEIGHT:
            computer.bottom = HEIGHT

        # Ball movement
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Top and bottom collision
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed_y *= -1

        # Player collision
        if ball.colliderect(player) and ball_speed_x < 0:

            ball.left = player.right

            ball_speed_x *= -1

            # Increase speed
            ball_speed_x *= 1.05
            ball_speed_y *= 1.05

        # Computer collision
        if ball.colliderect(computer) and ball_speed_x > 0:

            ball.right = computer.left

            ball_speed_x *= -1

            # Increase speed
            ball_speed_x *= 1.05
            ball_speed_y *= 1.05

        # Ball passes left side
        if ball.right < 0:

            computer_score += 1

            reset_ball(1)

        # Ball passes right side
        if ball.left > WIDTH:

            player_score += 1

            reset_ball(-1)

        # Check winner
        if player_score >= winning_score:

            game_over = True

        if computer_score >= winning_score:

            game_over = True

    # ---------------- DRAW ----------------

    screen.fill(BLACK)

    # Middle line
    for y in range(0, HEIGHT, 30):

        pygame.draw.rect(
            screen,
            WHITE,
            (WIDTH // 2 - 2, y, 4, 15)
        )

    # Player paddle
    pygame.draw.rect(
        screen,
        BLUE,
        player,
        border_radius=5
    )

    # Computer paddle
    pygame.draw.rect(
        screen,
        RED,
        computer,
        border_radius=5
    )

    # Ball
    pygame.draw.circle(
        screen,
        YELLOW,
        ball.center,
        10
    )

    # Player score
    player_text = font.render(
        str(player_score),
        True,
        BLUE
    )

    screen.blit(
        player_text,
        (WIDTH // 2 - 100, 25)
    )

    # Computer score
    computer_text = font.render(
        str(computer_score),
        True,
        RED
    )

    screen.blit(
        computer_text,
        (WIDTH // 2 + 70, 25)
    )

    # Game Over
    if game_over:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 180))

        screen.blit(
            overlay,
            (0, 0)
        )

        if player_score >= winning_score:

            message = big_font.render(
                "YOU WIN!",
                True,
                BLUE
            )

        else:

            message = big_font.render(
                "YOU LOST!",
                True,
                RED
            )

        screen.blit(
            message,
            (
                WIDTH // 2 - message.get_width() // 2,
                HEIGHT // 2 - 70
            )
        )

        restart = font.render(
            "Press R to Restart",
            True,
            WHITE
        )

        screen.blit(
            restart,
            (
                WIDTH // 2 - restart.get_width() // 2,
                HEIGHT // 2 + 30
            )
        )

    pygame.display.update()

pygame.quit()