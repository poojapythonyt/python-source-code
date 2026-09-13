import pygame
import random

pygame.init()

# Screen
WIDTH = 500
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 Python Game")

clock = pygame.time.Clock()

# Colors
BACKGROUND = (35, 35, 45)
GRID_COLOR = (70, 70, 80)
EMPTY_COLOR = (55, 55, 65)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREEN = (80, 200, 120)
YELLOW = (255, 210, 70)

# Fonts
title_font = pygame.font.Font(None, 55)
number_font = pygame.font.Font(None, 45)
small_font = pygame.font.Font(None, 32)

# Grid
SIZE = 4
CELL_SIZE = 100
GAP = 10

START_X = 35
START_Y = 150

# Game variables
board = []
score = 0
game_over = False
won = False


def create_board():
    return [[0 for _ in range(SIZE)] for _ in range(SIZE)]


def add_random_tile():

    empty_cells = []

    for row in range(SIZE):
        for col in range(SIZE):

            if board[row][col] == 0:
                empty_cells.append((row, col))

    if empty_cells:

        row, col = random.choice(empty_cells)

        board[row][col] = random.choice([2, 2, 2, 4])


def reset_game():

    global board, score, game_over, won

    board = create_board()

    score = 0
    game_over = False
    won = False

    add_random_tile()
    add_random_tile()


def move_left():

    global score

    moved = False

    for row in range(SIZE):

        # Remove zeros
        numbers = [x for x in board[row] if x != 0]

        # Merge
        new_row = []
        i = 0

        while i < len(numbers):

            if i + 1 < len(numbers) and numbers[i] == numbers[i + 1]:

                value = numbers[i] * 2

                new_row.append(value)

                score += value

                i += 2

            else:

                new_row.append(numbers[i])

                i += 1

        # Add zeros
        new_row += [0] * (SIZE - len(new_row))

        if new_row != board[row]:
            moved = True

        board[row] = new_row

    return moved


def move_right():

    global score

    moved = False

    for row in range(SIZE):

        numbers = [x for x in board[row] if x != 0]

        numbers.reverse()

        new_row = []

        i = 0

        while i < len(numbers):

            if i + 1 < len(numbers) and numbers[i] == numbers[i + 1]:

                value = numbers[i] * 2

                new_row.append(value)

                score += value

                i += 2

            else:

                new_row.append(numbers[i])

                i += 1

        new_row += [0] * (SIZE - len(new_row))

        new_row.reverse()

        if new_row != board[row]:
            moved = True

        board[row] = new_row

    return moved


def transpose():

    global board

    board = [list(row) for row in zip(*board)]


def move_up():

    transpose()

    moved = move_left()

    transpose()

    return moved


def move_down():

    transpose()

    moved = move_right()

    transpose()

    return moved


def can_move():

    # Empty cell exists
    for row in range(SIZE):
        for col in range(SIZE):

            if board[row][col] == 0:
                return True

    # Check horizontal matches
    for row in range(SIZE):
        for col in range(SIZE - 1):

            if board[row][col] == board[row][col + 1]:
                return True

    # Check vertical matches
    for row in range(SIZE - 1):
        for col in range(SIZE):

            if board[row][col] == board[row + 1][col]:
                return True

    return False


def check_win():

    for row in board:
        if 2048 in row:
            return True

    return False


def draw_board():

    screen.fill(BACKGROUND)

    # Title
    title = title_font.render(
        "2048 GAME",
        True,
        WHITE
    )

    screen.blit(
        title,
        (
            WIDTH // 2 - title.get_width() // 2,
            25
        )
    )

    # Score
    score_text = small_font.render(
        f"Score: {score}",
        True,
        YELLOW
    )

    screen.blit(
        score_text,
        (35, 95)
    )

    # Grid
    for row in range(SIZE):

        for col in range(SIZE):

            x = START_X + col * (CELL_SIZE + GAP)
            y = START_Y + row * (CELL_SIZE + GAP)

            value = board[row][col]

            # Empty cell
            pygame.draw.rect(
                screen,
                EMPTY_COLOR,
                (x, y, CELL_SIZE, CELL_SIZE),
                border_radius=8
            )

            if value != 0:

                pygame.draw.rect(
                    screen,
                    GREEN,
                    (x, y, CELL_SIZE, CELL_SIZE),
                    border_radius=8
                )

                number = number_font.render(
                    str(value),
                    True,
                    BLACK
                )

                screen.blit(
                    number,
                    (
                        x + CELL_SIZE // 2 - number.get_width() // 2,
                        y + CELL_SIZE // 2 - number.get_height() // 2
                    )
                )

    # Game Over
    if game_over:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 180))

        screen.blit(overlay, (0, 0))

        if won:

            message = title_font.render(
                "YOU WIN!",
                True,
                GREEN
            )

        else:

            message = title_font.render(
                "GAME OVER",
                True,
                WHITE
            )

        screen.blit(
            message,
            (
                WIDTH // 2 - message.get_width() // 2,
                HEIGHT // 2 - 50
            )
        )

        restart = small_font.render(
            "Press R to Restart",
            True,
            YELLOW
        )

        screen.blit(
            restart,
            (
                WIDTH // 2 - restart.get_width() // 2,
                HEIGHT // 2 + 20
            )
        )


# Start
reset_game()

running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # Restart
            if event.key == pygame.K_r:
                reset_game()

            if not game_over:

                moved = False

                if event.key == pygame.K_LEFT:
                    moved = move_left()

                elif event.key == pygame.K_RIGHT:
                    moved = move_right()

                elif event.key == pygame.K_UP:
                    moved = move_up()

                elif event.key == pygame.K_DOWN:
                    moved = move_down()

                # Add tile after successful move
                if moved:

                    add_random_tile()

                    if check_win():

                        won = True
                        game_over = True

                    elif not can_move():

                        game_over = True

    draw_board()

    pygame.display.update()

pygame.quit()