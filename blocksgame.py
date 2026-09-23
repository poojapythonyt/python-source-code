import pygame
import random

pygame.init()

# Screen
WIDTH = 600
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Falling Blocks Puzzle")

clock = pygame.time.Clock()

# Grid
CELL = 30
COLS = 10
ROWS = 20

GRID_WIDTH = COLS * CELL
GRID_HEIGHT = ROWS * CELL

OFFSET_X = (WIDTH - GRID_WIDTH) // 2
OFFSET_Y = 50

# Colors
BLACK = (15, 15, 20)
WHITE = (240, 240, 240)
GRAY = (50, 50, 60)

COLORS = [
    (0, 220, 220),
    (0, 100, 255),
    (255, 150, 0),
    (255, 220, 0),
    (0, 220, 100),
    (170, 70, 220),
    (240, 60, 70)
]

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],

    [
        [1, 0, 0],
        [1, 1, 1]
    ],

    [
        [0, 0, 1],
        [1, 1, 1]
    ],

    [
        [1, 1],
        [1, 1]
    ],

    [
        [0, 1, 1],
        [1, 1, 0]
    ],

    [
        [0, 1, 0],
        [1, 1, 1]
    ],

    [
        [1, 1, 0],
        [0, 1, 1]
    ]
]

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 70)


def create_grid():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]


def new_piece():

    shape = random.choice(SHAPES)

    return {
        "shape": [row[:] for row in shape],
        "x": COLS // 2 - len(shape[0]) // 2,
        "y": 0,
        "color": random.choice(COLORS)
    }


def rotate_piece(piece):

    shape = piece["shape"]

    rotated = [
        list(row)
        for row in zip(*shape[::-1])
    ]

    old_shape = piece["shape"]

    piece["shape"] = rotated

    if collision(piece):

        piece["shape"] = old_shape


def collision(piece):

    shape = piece["shape"]

    for y, row in enumerate(shape):

        for x, cell in enumerate(row):

            if not cell:
                continue

            new_x = piece["x"] + x
            new_y = piece["y"] + y

            if new_x < 0 or new_x >= COLS:
                return True

            if new_y >= ROWS:
                return True

            if new_y >= 0 and grid[new_y][new_x] is not None:
                return True

    return False


def lock_piece(piece):

    shape = piece["shape"]

    for y, row in enumerate(shape):

        for x, cell in enumerate(row):

            if cell:

                grid_y = piece["y"] + y
                grid_x = piece["x"] + x

                if 0 <= grid_y < ROWS:
                    grid[grid_y][grid_x] = piece["color"]


def clear_lines():

    global grid

    new_grid = []

    cleared = 0

    for row in grid:

        if all(cell is not None for cell in row):

            cleared += 1

        else:
            new_grid.append(row)

    while len(new_grid) < ROWS:
        new_grid.insert(
            0,
            [None for _ in range(COLS)]
        )

    grid = new_grid

    return cleared


def draw_grid():

    for y in range(ROWS):

        for x in range(COLS):

            rect = pygame.Rect(
                OFFSET_X + x * CELL,
                OFFSET_Y + y * CELL,
                CELL,
                CELL
            )

            pygame.draw.rect(
                screen,
                GRAY,
                rect,
                1
            )

            if grid[y][x] is not None:

                pygame.draw.rect(
                    screen,
                    grid[y][x],
                    rect.inflate(-2, -2),
                    border_radius=4
                )


def draw_piece(piece):

    shape = piece["shape"]

    for y, row in enumerate(shape):

        for x, cell in enumerate(row):

            if cell:

                rect = pygame.Rect(
                    OFFSET_X + (piece["x"] + x) * CELL,
                    OFFSET_Y + (piece["y"] + y) * CELL,
                    CELL,
                    CELL
                )

                pygame.draw.rect(
                    screen,
                    piece["color"],
                    rect.inflate(-2, -2),
                    border_radius=4
                )


def reset_game():

    global grid
    global current_piece
    global score
    global game_over
    global fall_timer
    global fall_speed

    grid = create_grid()

    current_piece = new_piece()

    score = 0

    game_over = False

    fall_timer = 0

    fall_speed = 500


reset_game()

running = True

while running:

    dt = clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if not game_over:

                if event.key == pygame.K_LEFT:

                    current_piece["x"] -= 1

                    if collision(current_piece):
                        current_piece["x"] += 1

                elif event.key == pygame.K_RIGHT:

                    current_piece["x"] += 1

                    if collision(current_piece):
                        current_piece["x"] -= 1

                elif event.key == pygame.K_UP:

                    rotate_piece(current_piece)

                elif event.key == pygame.K_DOWN:

                    current_piece["y"] += 1

                    if collision(current_piece):

                        current_piece["y"] -= 1

                elif event.key == pygame.K_SPACE:

                    while not collision(current_piece):
                        current_piece["y"] += 1

                    current_piece["y"] -= 1

                    lock_piece(current_piece)

                    lines = clear_lines()

                    score += lines * 100

                    current_piece = new_piece()

                    if collision(current_piece):
                        game_over = True

            else:

                if event.key == pygame.K_r:
                    reset_game()

    if not game_over:

        fall_timer += dt

        if fall_timer >= fall_speed:

            fall_timer = 0

            current_piece["y"] += 1

            if collision(current_piece):

                current_piece["y"] -= 1

                lock_piece(current_piece)

                lines = clear_lines()

                if lines == 1:
                    score += 100
                elif lines == 2:
                    score += 250
                elif lines == 3:
                    score += 500
                elif lines >= 4:
                    score += 1000

                current_piece = new_piece()

                if collision(current_piece):
                    game_over = True

            # Increase speed
            fall_speed = max(
                100,
                500 - (score // 500) * 40
            )

    # Draw
    screen.fill(BLACK)

    draw_grid()

    if not game_over:
        draw_piece(current_piece)

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

    # Controls
    control_text = font.render(
        "← → Move   ↑ Rotate   ↓ Drop   SPACE Hard Drop",
        True,
        WHITE
    )

    screen.blit(
        control_text,
        (35, HEIGHT - 35)
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

        text = big_font.render(
            "GAME OVER",
            True,
            (240, 70, 70)
        )

        screen.blit(
            text,
            (
                WIDTH // 2 - text.get_width() // 2,
                HEIGHT // 2 - 80
            )
        )

        final_score = font.render(
            f"Final Score: {score}",
            True,
            WHITE
        )

        screen.blit(
            final_score,
            (
                WIDTH // 2 - final_score.get_width() // 2,
                HEIGHT // 2
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
                HEIGHT // 2 + 50
            )
        )

    pygame.display.flip()

pygame.quit()