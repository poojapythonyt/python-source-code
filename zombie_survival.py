import math
import random
import pygame

# Zombie Survival — one-file Pygame game. No external assets required.
pygame.init()
WIDTH, HEIGHT = 1000, 650
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ZOMBIE SURVIVAL")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 20, bold=True)
SMALL = pygame.font.SysFont("consolas", 15)
BIG = pygame.font.SysFont("consolas", 54, bold=True)
MID = pygame.font.SysFont("consolas", 28, bold=True)

BG = (13, 18, 22)
GRID = (23, 32, 36)
WHITE = (235, 242, 238)
GREEN = (83, 220, 130)
RED = (238, 72, 76)
YELLOW = (255, 205, 85)
CYAN = (80, 220, 235)
PURPLE = (184, 100, 235)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def vec(x, y=None):
    return pygame.Vector2(x) if y is None else pygame.Vector2(x, y)

def draw_text(surface, text, font, color, pos, center=False):
    img = font.render(str(text), True, color)
    rect = img.get_rect()
    if center:
        rect.center = (int(pos[0]), int(pos[1]))
    else:
        rect.topleft = (int(pos[0]), int(pos[1]))
    surface.blit(img, rect)

def make_obstacles():
    obstacles = []
    spots = [
        (155, 150, 90, 54), (365, 115, 60, 105), (625, 135, 120, 48),
        (810, 210, 60, 115), (230, 355, 125, 48), (500, 300, 72, 95),
        (720, 455, 125, 48), (405, 500, 80, 52), (105, 505, 70, 70)
    ]
    for x, y, w, h in spots:
        obstacles.append(pygame.Rect(x, y, w, h))
    return obstacles

obstacles = make_obstacles()

def circle_rect_collision(pos, radius, rect):
    closest_x = clamp(pos.x, rect.left, rect.right)
    closest_y = clamp(pos.y, rect.top, rect.bottom)
    return (pos.x - closest_x) ** 2 + (pos.y - closest_y) ** 2 < radius ** 2

def move_circle(pos, delta, radius, blocks):
    pos.x += delta.x
    pos.x = clamp(pos.x, radius, WIDTH - radius)
    for rect in blocks:
        if circle_rect_collision(pos, radius, rect):
            if delta.x > 0: pos.x = rect.left - radius
            elif delta.x < 0: pos.x = rect.right + radius
    pos.y += delta.y
    pos.y = clamp(pos.y, radius + 48, HEIGHT - radius)
    for rect in blocks:
        if circle_rect_collision(pos, radius, rect):
            if delta.y > 0: pos.y = rect.top - radius
            elif delta.y < 0: pos.y = rect.bottom + radius
    return pos

class Particle:
    def __init__(self, pos, color, speed=180, life=0.35, radius=3):
        self.pos = vec(pos)
        angle = random.random() * math.tau
        self.vel = vec(math.cos(angle), math.sin(angle)) * random.uniform(speed * .25, speed)
        self.color = color
        self.life = life
        self.max_life = life
        self.radius = radius
    def update(self, dt):
        self.pos += self.vel * dt
        self.vel *= max(0, 1 - 3 * dt)
        self.life -= dt
    def draw(self, surf):
        if self.life > 0:
            r = max(1, int(self.radius * self.life / self.max_life))
            pygame.draw.circle(surf, self.color, (int(self.pos.x), int(self.pos.y)), r)

class Bullet:
    def __init__(self, pos, direction, damage=1, speed=680):
        self.pos = vec(pos)
        self.vel = vec(direction) * speed
        self.damage = damage
        self.life = 1.25
        self.radius = 4
    def update(self, dt):
        self.pos += self.vel * dt
        self.life -= dt
    def draw(self, surf):
        p = (int(self.pos.x), int(self.pos.y))
        pygame.draw.circle(surf, (255, 225, 120), p, 7)
        pygame.draw.circle(surf, (255, 255, 220), p, 3)

class Zombie:
    def __init__(self, wave, boss=False):
        self.boss = boss
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top": p = (random.randint(35, WIDTH-35), 70)
        elif side == "bottom": p = (random.randint(35, WIDTH-35), HEIGHT-25)
        elif side == "left": p = (25, random.randint(75, HEIGHT-25))
        else: p = (WIDTH-25, random.randint(75, HEIGHT-25))
        self.pos = vec(p)
        self.kind = "brute" if boss else random.choice(["walker", "runner", "brute"])
        self.radius = 25 if boss else (16 if self.kind == "brute" else 12 if self.kind == "runner" else 14)
        self.max_hp = (18 + wave * 3) if boss else (3 + wave // 3 if self.kind == "brute" else 2 + wave // 5)
        self.hp = self.max_hp
        self.speed = ((47 + wave * 1.5) if boss else (random.uniform(48, 66) + wave * 2 if self.kind == "walker" else random.uniform(82, 105) + wave * 2 if self.kind == "runner" else random.uniform(35, 48) + wave * 1.5)) * 0.8
        self.damage = 18 if boss else (13 if self.kind == "brute" else 8)
        self.attack_cd = 0
        self.flash = 0
    def update(self, dt, player, blocks):
        self.attack_cd = max(0, self.attack_cd - dt)
        self.flash = max(0, self.flash - dt)
        direction = player.pos - self.pos
        dist = direction.length()
        if dist > 0:
            direction = direction.normalize()
            # Simple steering around obstacles: try a perpendicular route if blocked.
            next_pos = self.pos + direction * self.speed * dt
            if any(circle_rect_collision(next_pos, self.radius, r) for r in blocks):
                left = vec(-direction.y, direction.x)
                right = -left
                options = [self.pos + left * self.speed * dt, self.pos + right * self.speed * dt]
                clear = [p for p in options if not any(circle_rect_collision(p, self.radius, r) for r in blocks)]
                if clear:
                    next_pos = min(clear, key=lambda p: p.distance_to(player.pos))
            self.pos = move_circle(self.pos, next_pos - self.pos, self.radius, blocks)
        if dist < self.radius + player.radius + 5 and self.attack_cd <= 0:
            player.health -= self.damage
            player.hit_flash = .22
            self.attack_cd = 0.9 if self.boss else 1.0
            player.vel_knock = (player.pos - self.pos)
            if player.vel_knock.length_squared():
                player.vel_knock = player.vel_knock.normalize() * 130
    def draw(self, surf):
        x, y = int(self.pos.x), int(self.pos.y)
        if self.boss:
            color = (153, 45, 61)
        elif self.kind == "runner":
            color = (228, 178, 66)
        elif self.kind == "brute":
            color = (125, 67, 72)
        else:
            color = (79, 178, 105)
        if self.flash > 0: color = (255, 245, 230)
        pygame.draw.circle(surf, (4, 7, 8), (x+3, y+4), self.radius+2)
        pygame.draw.circle(surf, color, (x, y), self.radius)
        pygame.draw.circle(surf, (45, 30, 32), (x-4, y-2), max(2, self.radius//5))
        pygame.draw.circle(surf, (255, 80, 70), (x+5, y-3), max(2, self.radius//6))
        # health bar
        bar_w = self.radius * 2
        pygame.draw.rect(surf, (55, 25, 29), (x-bar_w//2, y-self.radius-9, bar_w, 4))
        pygame.draw.rect(surf, GREEN, (x-bar_w//2, y-self.radius-9, int(bar_w * max(0, self.hp/self.max_hp)), 4))

class Medkit:
    def __init__(self, pos):
        self.pos = vec(pos)
        self.life = 12
    def update(self, dt): self.life -= dt
    def draw(self, surf):
        x, y = int(self.pos.x), int(self.pos.y)
        pygame.draw.circle(surf, (20, 35, 30), (x, y), 13)
        pygame.draw.rect(surf, (80, 220, 125), (x-3, y-8, 6, 16))
        pygame.draw.rect(surf, (80, 220, 125), (x-8, y-3, 16, 6))

class Player:
    def __init__(self):
        self.pos = vec(WIDTH/2, HEIGHT/2)
        self.radius = 15
        self.speed = 255
        self.health = 100
        self.max_health = 100
        self.ammo = 12
        self.mag_size = 12
        self.reserve = 96
        self.reload_time = 0
        self.fire_cd = 0
        self.hit_flash = 0
        self.vel_knock = vec(0, 0)
        self.facing = vec(1, 0)
    def update(self, dt, keys, blocks):
        direction = vec(0, 0)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: direction.x += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]: direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: direction.y += 1
        if direction.length_squared(): direction = direction.normalize()
        delta = direction * self.speed * dt + self.vel_knock * dt
        move_circle(self.pos, delta, self.radius, blocks)
        self.vel_knock *= max(0, 1 - 7 * dt)
        self.fire_cd = max(0, self.fire_cd - dt)
        self.hit_flash = max(0, self.hit_flash - dt)
        if self.reload_time > 0:
            self.reload_time -= dt
            if self.reload_time <= 0:
                needed = self.mag_size - self.ammo
                take = min(needed, self.reserve)
                self.ammo += take
                self.reserve -= take
    def reload(self):
        if self.reload_time <= 0 and self.ammo < self.mag_size and self.reserve > 0:
            self.reload_time = 1.0
    def shoot(self, target):
        if self.fire_cd > 0 or self.reload_time > 0: return None
        if self.ammo <= 0:
            self.reload()
            return None
        direction = vec(target) - self.pos
        if direction.length_squared() == 0: return None
        direction = direction.normalize()
        self.facing = direction
        self.ammo -= 1
        self.fire_cd = .16
        muzzle = self.pos + direction * 22
        return Bullet(muzzle, direction)

def reset_game():
    return {
        "player": Player(), "zombies": [], "bullets": [], "particles": [], "medkits": [],
        "wave": 1, "score": 0, "spawn_timer": 0.8, "wave_pause": 1.6,
        "state": "menu", "shake": 0, "message_timer": 0
    }

game = reset_game()
# decorative floor specks
specks = [(random.randrange(WIDTH), random.randrange(48, HEIGHT), random.choice([1, 1, 2])) for _ in range(180)]

def spawn_zombie(g):
    boss = g["wave"] % 5 == 0 and not any(z.boss for z in g["zombies"])
    g["zombies"].append(Zombie(g["wave"], boss))

def update_game(g, dt, keys, mouse_pos, mouse_down):
    p = g["player"]
    p.update(dt, keys, obstacles)
    if mouse_down:
        bullet = p.shoot(mouse_pos)
        if bullet: g["bullets"].append(bullet)
    for z in g["zombies"][:]:
        z.update(dt, p, obstacles)
        if z.hp <= 0:
            g["score"] += 25 if z.boss else (15 if z.kind == "brute" else 10)
            for _ in range(10 if z.boss else 6):
                g["particles"].append(Particle(z.pos, (112, 198, 108), speed=160, life=.5))
            if random.random() < .12:
                g["medkits"].append(Medkit(z.pos))
            g["zombies"].remove(z)
    for b in g["bullets"][:]:
        b.update(dt)
        hit = False
        if b.life <= 0 or not (0 <= b.pos.x <= WIDTH and 48 <= b.pos.y <= HEIGHT):
            g["bullets"].remove(b); continue
        if any(circle_rect_collision(b.pos, b.radius, r) for r in obstacles):
            g["bullets"].remove(b); continue
        for z in g["zombies"][:]:
            if b.pos.distance_squared_to(z.pos) < (b.radius + z.radius) ** 2:
                z.hp -= b.damage
                z.flash = .1
                for _ in range(3):
                    g["particles"].append(Particle(b.pos, (255, 100, 90), speed=90, life=.22, radius=2))
                g["bullets"].remove(b)
                hit = True
                break
        if hit: continue
    for kit in g["medkits"][:]:
        kit.update(dt)
        if kit.life <= 0:
            g["medkits"].remove(kit)
        elif kit.pos.distance_to(p.pos) < 27:
            p.health = min(p.max_health, p.health + 30)
            g["medkits"].remove(kit)
            g["message_timer"] = 1.1
    for part in g["particles"][:]:
        part.update(dt)
        if part.life <= 0: g["particles"].remove(part)
    g["spawn_timer"] -= dt
    if not g["zombies"]:
        g["wave_pause"] -= dt
        if g["wave_pause"] <= 0:
            g["wave"] += 1
            g["wave_pause"] = 2.0
            g["spawn_timer"] = .8
            spawn_zombie(g)
    elif g["spawn_timer"] <= 0 and len(g["zombies"]) < min(3 + g["wave"], 12):
        spawn_zombie(g)
        g["spawn_timer"] = max(.65, 1.8 - g["wave"] * .025)
    else:
        g["wave_pause"] = 2.0
    if p.health <= 0:
        p.health = 0
        g["state"] = "gameover"

def draw_background(surf):
    surf.fill(BG)
    for x in range(0, WIDTH, 40):
        pygame.draw.line(surf, GRID, (x, 48), (x, HEIGHT), 1)
    for y in range(48, HEIGHT, 40):
        pygame.draw.line(surf, GRID, (0, y), (WIDTH, y), 1)
    for x, y, r in specks:
        pygame.draw.circle(surf, (36, 48, 48), (x, y), r)
    pygame.draw.rect(surf, (19, 25, 28), (0, 0, WIDTH, 48))
    pygame.draw.line(surf, (52, 68, 67), (0, 48), (WIDTH, 48), 2)
    for i, r in enumerate(obstacles):
        pygame.draw.rect(surf, (4, 7, 8), r.move(5, 6), border_radius=8)
        pygame.draw.rect(surf, (55, 67, 66), r, border_radius=8)
        pygame.draw.rect(surf, (82, 99, 94), r.inflate(-8, -8), 2, border_radius=6)
        pygame.draw.line(surf, (38, 48, 47), (r.left+8, r.top+8), (r.right-8, r.bottom-8), 2)

def draw_hud(g):
    p = g["player"]
    pygame.draw.rect(screen, (35, 42, 45), (18, 12, 210, 18), border_radius=5)
    pygame.draw.rect(screen, RED if p.health < 30 else GREEN, (18, 12, int(210*p.health/p.max_health), 18), border_radius=5)
    draw_text(screen, f"HP {int(p.health)}/{p.max_health}", SMALL, WHITE, (24, 13))
    draw_text(screen, f"WAVE {g['wave']}", FONT, YELLOW, (270, 10))
    draw_text(screen, f"SCORE {g['score']}", FONT, WHITE, (400, 10))
    ammo_color = RED if p.ammo <= 3 else CYAN
    draw_text(screen, f"AMMO {p.ammo:02d}/{p.reserve:03d}", FONT, ammo_color, (600, 10))
    if p.reload_time > 0:
        draw_text(screen, "RELOADING...", SMALL, YELLOW, (810, 15))
    elif g["message_timer"] > 0:
        draw_text(screen, "+30 HEALTH", SMALL, GREEN, (810, 15))
    draw_text(screen, "WASD move  |  MOUSE aim  |  LMB shoot  |  R reload", SMALL, (170, 180, 180), (18, HEIGHT-24))

def draw_game(g):
    draw_background(screen)
    for kit in g["medkits"]: kit.draw(screen)
    for b in g["bullets"]: b.draw(screen)
    for z in g["zombies"]: z.draw(screen)
    for part in g["particles"]: part.draw(screen)
    p = g["player"]
    x, y = int(p.pos.x), int(p.pos.y)
    if p.hit_flash > 0:
        pygame.draw.circle(screen, (255, 255, 255), (x, y), p.radius+6)
    pygame.draw.circle(screen, (0, 0, 0), (x+3, y+4), p.radius+3)
    pygame.draw.circle(screen, (70, 165, 220), (x, y), p.radius)
    aim = vec(pygame.mouse.get_pos()) - p.pos
    if aim.length_squared():
        aim = aim.normalize()
        pygame.draw.line(screen, (195, 235, 245), (x, y), (int(x+aim.x*27), int(y+aim.y*27)), 4)
    pygame.draw.circle(screen, (210, 245, 255), (x-4, y-4), 4)
    # Crosshair
    mx, my = pygame.mouse.get_pos()
    pygame.draw.circle(screen, YELLOW, (mx, my), 9, 1)
    pygame.draw.line(screen, YELLOW, (mx-13, my), (mx-5, my), 1)
    pygame.draw.line(screen, YELLOW, (mx+5, my), (mx+13, my), 1)
    pygame.draw.line(screen, YELLOW, (mx, my-13), (mx, my-5), 1)
    pygame.draw.line(screen, YELLOW, (mx, my+5), (mx, my+13), 1)
    draw_hud(g)
    if g["wave_pause"] < 1.6 and not g["zombies"]:
        draw_text(screen, f"WAVE {g['wave'] + 1} INCOMING", MID, YELLOW, (WIDTH//2, 100), center=True)

def overlay():
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 185))
    screen.blit(s, (0, 0))

def main():
    global game
    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, .04)
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and game["state"] == "playing":
                    game["player"].reload()
                if event.key in (pygame.K_RETURN, pygame.K_SPACE) and game["state"] in ("menu", "gameover"):
                    game = reset_game()
                    game["state"] = "playing"
        if game["state"] == "playing":
            game["message_timer"] = max(0, game["message_timer"] - dt)
            update_game(game, dt, pygame.key.get_pressed(), mouse_pos, mouse_down)
            draw_game(game)
        else:
            draw_background(screen)
            if game["state"] == "menu":
                overlay()
                draw_text(screen, "ZOMBIE", BIG, GREEN, (WIDTH//2, 185), center=True)
                draw_text(screen, "SURVIVAL", BIG, WHITE, (WIDTH//2, 245), center=True)
                draw_text(screen, "The city fell. Make it through the waves.", MID, (190, 205, 195), (WIDTH//2, 315), center=True)
                draw_text(screen, "WASD / ARROWS  MOVE     MOUSE  AIM     LEFT CLICK  SHOOT", FONT, CYAN, (WIDTH//2, 380), center=True)
                draw_text(screen, "R RELOAD     PICK UP GREEN MEDKITS     EVERY 5TH WAVE: BOSS", FONT, YELLOW, (WIDTH//2, 415), center=True)
                draw_text(screen, "PRESS ENTER OR SPACE TO START", MID, WHITE, (WIDTH//2, 495), center=True)
            else:
                overlay()
                draw_text(screen, "YOU WERE OVERRUN", BIG, RED, (WIDTH//2, 210), center=True)
                draw_text(screen, f"FINAL SCORE: {game['score']}     WAVE: {game['wave']}", MID, WHITE, (WIDTH//2, 300), center=True)
                draw_text(screen, "PRESS ENTER OR SPACE TO TRY AGAIN", MID, YELLOW, (WIDTH//2, 390), center=True)
                draw_text(screen, "ESC TO QUIT", FONT, (180, 190, 190), (WIDTH//2, 445), center=True)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
