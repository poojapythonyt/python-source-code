import pygame
import random
import time
import sys

pygame.init()

# =========================
# WINDOW
# =========================
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CODE BREAKER - Hacking Puzzle")

clock = pygame.time.Clock()

# =========================
# COLORS
# =========================
BG = (15, 18, 28)
PANEL = (25, 30, 45)
WHITE = (240, 240, 245)
GRAY = (120, 125, 140)
DARK_GRAY = (55, 60, 75)

GREEN = (50, 210, 120)
YELLOW = (245, 190, 50)
RED = (230, 70, 80)
BLUE = (70, 150, 255)
PURPLE = (170, 90, 240)

BLACK = (0, 0, 0)

# =========================
# FONTS
# =========================
FONT_BIG = pygame.font.Font(None, 64)
FONT_TITLE = pygame.font.Font(None, 52)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 24)
FONT_TINY = pygame.font.Font(None, 20)

# =========================
# GAME SETTINGS
# =========================
MAX_ATTEMPTS = 8

# =========================
# CREATE SECRET
# =========================
def create_secret():
    digits = list("0123456789")

    while True:
        random.shuffle(digits)
        code = "".join(digits[:4])

        # First digit should not be 0
        if code[0] != "0":
            return code


# =========================
# CHECK GUESS
# =========================
def check_guess(secret, guess):
    """
    Returns:
        exact   -> correct digit + correct position
        wrong   -> correct digit + wrong position
        absent  -> digit not present
    """

    result = []

    for i in range(4):
        if guess[i] == secret[i]:
            result.append("exact")

        elif guess[i] in secret:
            result.append("wrong")

        else:
            result.append("absent")

    return result


# =========================
# TEXT DRAW FUNCTION
# =========================
def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)

    if center:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))

    screen.blit(surface, rect)


# =========================
# GENERATE BUTTON
# =========================
def draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)

    draw_text(
        text,
        FONT_MEDIUM,
        WHITE,
        rect.centerx,
        rect.centery,
        center=True
    )


# =========================
# RESET GAME
# =========================
def reset_game():
    secret = create_secret()

    return {
        "secret": secret,
        "guess": "",
        "attempts": [],
        "score": 0,
        "level": 1,
        "start_time": time.time(),
        "game_over": False,
        "won": False,
        "message": "Enter a 4-digit code",
        "message_color": WHITE
    }


game = reset_game()


# =========================
# DRAW LEGEND
# =========================
def draw_legend():
    y = 125

    # Green
    pygame.draw.circle(screen, GREEN, (250, y), 9)
    draw_text(
        "Correct Place",
        FONT_SMALL,
        WHITE,
        270,
        y - 12
    )

    # Yellow
    pygame.draw.circle(screen, YELLOW, (470, y), 9)
    draw_text(
        "Wrong Place",
        FONT_SMALL,
        WHITE,
        490,
        y - 12
    )

    # Gray
    pygame.draw.circle(screen, GRAY, (670, y), 9)
    draw_text(
        "Not In Code",
        FONT_SMALL,
        WHITE,
        690,
        y - 12
    )


# =========================
# DRAW ATTEMPT
# =========================
def draw_attempt(guess, statuses, y, attempt_number):
    draw_text(
        f"{attempt_number}.",
        FONT_SMALL,
        GRAY,
        85,
        y + 18
    )

    start_x = 145
    box_size = 65
    gap = 18

    for i in range(4):

        x = start_x + i * (box_size + gap)

        # Digit box
        pygame.draw.rect(
            screen,
            PANEL,
            (x, y, box_size, box_size),
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            WHITE,
            (x, y, box_size, box_size),
            2,
            border_radius=8
        )

        draw_text(
            guess[i],
            FONT_BIG,
            WHITE,
            x + box_size // 2,
            y + box_size // 2,
            center=True
        )

        # Status color
        if statuses[i] == "exact":
            color = GREEN
            label = "CORRECT"

        elif statuses[i] == "wrong":
            color = YELLOW
            label = "WRONG"

        else:
            color = GRAY
            label = "NO"

        # Status indicator
        pygame.draw.circle(
            screen,
            color,
            (x + box_size // 2, y + box_size + 13),
            7
        )

        # Status text
        draw_text(
            label,
            FONT_TINY,
            color,
            x + box_size // 2,
            y + box_size + 35,
            center=True
        )


# =========================
# DRAW CURRENT INPUT
# =========================
def draw_input():
    draw_text(
        "YOUR CODE",
        FONT_SMALL,
        BLUE,
        85,
        575
    )

    start_x = 250
    box_size = 65
    gap = 18

    for i in range(4):

        x = start_x + i * (box_size + gap)

        if i < len(game["guess"]):
            color = BLUE
        else:
            color = DARK_GRAY

        pygame.draw.rect(
            screen,
            PANEL,
            (x, 565, box_size, box_size),
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            color,
            (x, 565, box_size, box_size),
            3,
            border_radius=8
        )

        if i < len(game["guess"]):
            draw_text(
                game["guess"][i],
                FONT_BIG,
                WHITE,
                x + box_size // 2,
                565 + box_size // 2,
                center=True
            )


# =========================
# DRAW GAME
# =========================
def draw_game():
    screen.fill(BG)

    # Title
    draw_text(
        "CODE BREAKER",
        FONT_TITLE,
        BLUE,
        WIDTH // 2,
        45,
        center=True
    )

    draw_text(
        "Find the secret 4-digit code",
        FONT_SMALL,
        GRAY,
        WIDTH // 2,
        85,
        center=True
    )

    draw_legend()

    # Score
    draw_text(
        f"Score: {game['score']}",
        FONT_SMALL,
        WHITE,
        780,
        30
    )

    draw_text(
        f"Level: {game['level']}",
        FONT_SMALL,
        WHITE,
        780,
        60
    )

    # Timer
    time_limit = max(20, 45 - (game["level"] - 1) * 3)

    elapsed = int(time.time() - game["start_time"])
    remaining = max(0, time_limit - elapsed)

    timer_color = GREEN

    if remaining <= 10:
        timer_color = RED

    draw_text(
        f"Time: {remaining}s",
        FONT_SMALL,
        timer_color,
        780,
        90
    )

    # Attempts
    y = 155

    for i, attempt in enumerate(game["attempts"]):

        draw_attempt(
            attempt["guess"],
            attempt["statuses"],
            y,
            i + 1
        )

        y += 62

    draw_input()

    # Message
    draw_text(
        game["message"],
        FONT_SMALL,
        game["message_color"],
        WIDTH // 2,
        650,
        center=True
    )

    pygame.display.flip()


# =========================
# NEXT LEVEL
# =========================
def next_level():
    game["level"] += 1
    game["score"] += 100

    game["secret"] = create_secret()
    game["guess"] = ""
    game["attempts"] = []
    game["start_time"] = time.time()
    game["message"] = "New level! Crack the code!"
    game["message_color"] = GREEN


# =========================
# SUBMIT GUESS
# =========================
def submit_guess():

    guess = game["guess"]

    if len(guess) != 4:
        game["message"] = "Enter exactly 4 digits!"
        game["message_color"] = RED
        return

    if len(set(guess)) != 4:
        game["message"] = "Digits must be different!"
        game["message_color"] = RED
        return

    statuses = check_guess(
        game["secret"],
        guess
    )

    game["attempts"].append({
        "guess": guess,
        "statuses": statuses
    })

    exact_count = statuses.count("exact")
    wrong_count = statuses.count("wrong")

    # WIN
    if exact_count == 4:

        game["score"] += 500
        game["message"] = "CODE CRACKED! Press N for next level."
        game["message_color"] = GREEN
        game["won"] = True

        return

    # Attempts finished
    if len(game["attempts"]) >= MAX_ATTEMPTS:

        game["message"] = (
            f"GAME OVER! Code was {game['secret']}. Press R to restart."
        )

        game["message_color"] = RED
        game["game_over"] = True

        return

    game["message"] = (
        f"{exact_count} correct place | "
        f"{wrong_count} wrong place"
    )

    game["message_color"] = WHITE

    game["guess"] = ""


# =========================
# MAIN LOOP
# =========================
running = True

while running:

    # Check timer
    if not game["game_over"] and not game["won"]:

        time_limit = max(
            20,
            45 - (game["level"] - 1) * 3
        )

        elapsed = int(
            time.time() - game["start_time"]
        )

        if elapsed >= time_limit:

            game["message"] = (
                f"TIME UP! Code was {game['secret']}. "
                f"Press R to restart."
            )

            game["message_color"] = RED
            game["game_over"] = True

    # Events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            # ESC
            if event.key == pygame.K_ESCAPE:
                running = False

            # Restart
            elif event.key == pygame.K_r:

                game = reset_game()

            # Next level
            elif event.key == pygame.K_n and game["won"]:

                next_level()

            # Only accept input during active game
            elif not game["game_over"] and not game["won"]:

                # Number keys
                if event.unicode.isdigit():

                    digit = event.unicode

                    # First digit cannot be zero
                    if len(game["guess"]) == 0 and digit == "0":
                        game["message"] = "First digit cannot be 0!"
                        game["message_color"] = RED

                    # No duplicate digits
                    elif digit in game["guess"]:

                        game["message"] = "Don't repeat digits!"
                        game["message_color"] = RED

                    # Maximum 4 digits
                    elif len(game["guess"]) < 4:

                        game["guess"] += digit
                        game["message"] = "Press ENTER to check"
                        game["message_color"] = WHITE

                # Backspace
                elif event.key == pygame.K_BACKSPACE:

                    game["guess"] = game["guess"][:-1]

                # Enter
                elif event.key == pygame.K_RETURN:

                    submit_guess()

    # Draw
    draw_game()

    clock.tick(60)


pygame.quit()
sys.exit()