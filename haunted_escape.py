import math
import random
import sys
import pygame

# HAUNTED ESCAPE — corrected movement, collision, keys, doors, traps and monster.
# Install: python -m pip install pygame
# Run:     python haunted_escape_fixed.py

pygame.init()
try:
    pygame.mixer.init()
    AUDIO_OK = True
except pygame.error:
    AUDIO_OK = False

WIDTH, HEIGHT = 1000, 650
TILE, COLS, ROWS = 50, 30, 18
WORLD_W, WORLD_H = TILE * COLS, TILE * ROWS
FPS, PLAYER_SPEED = 60, 185
PLAYER_SIZE = 28
MONSTER_W, MONSTER_H = 40, 46

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HAUNTED ESCAPE — FIXED")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 22, bold=True)
SMALL = pygame.font.SysFont("consolas", 16)
BIG = pygame.font.SysFont("consolas", 54, bold=True)

BLACK = (8, 7, 16)
FLOOR = (27, 25, 40)
FLOOR2 = (32, 29, 47)
WALL = (48, 37, 58)
WALL_EDGE = (102, 64, 112)
CYAN = (65, 235, 255)
PURPLE = (190, 80, 255)
GOLD = (255, 211, 75)
RED = (255, 65, 90)
WHITE = (245, 242, 255)
GREEN = (100, 245, 160)

def beep(freq=650, ms=90):
    if not AUDIO_OK:
        return
    try:
        rate = 22050
        n = int(rate * ms / 1000)
        buf = bytearray()
        for i in range(n):
            v = int(6000 * math.sin(2 * math.pi * freq * i / rate))
            buf.extend(v.to_bytes(2, "little", signed=True))
        pygame.mixer.Sound(buffer=bytes(buf)).play()
    except pygame.error:
        pass

def rect_for_cell(cx, cy):
    return pygame.Rect(cx*TILE, cy*TILE, TILE, TILE)

def build_map():
    # A connected floor plan: walls have clear gaps at every corridor crossing.
    g = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    for x in range(COLS):
        g[0][x] = g[ROWS-1][x] = 1
    for y in range(ROWS):
        g[y][0] = g[y][COLS-1] = 1

    # Horizontal room dividers with wide, intentional doorways.
    for y, gaps in [
        (4, [(3,5), (10,12), (18,20), (25,27)]),
        (8, [(2,4), (8,10), (15,17), (23,25)]),
        (12, [(4,6), (11,13), (19,21), (26,28)]),
    ]:
        for x in range(1, COLS-1):
            if not any(a <= x <= b for a,b in gaps):
                g[y][x] = 1

    # Vertical room dividers, with openings connecting the horizontal corridors.
    for x, gaps in [
        (6, [(2,3), (6,7), (10,11), (14,16)]),
        (13, [(1,2), (5,6), (9,10), (14,16)]),
        (20, [(2,3), (6,7), (10,11), (14,16)]),
        (26, [(1,2), (5,6), (9,10), (14,16)]),
    ]:
        for y in range(1, ROWS-1):
            if not any(a <= y <= b for a,b in gaps):
                g[y][x] = 1

    # Keep a guaranteed connected spine: left passage, central passage, and bottom route.
    for y in range(1, ROWS-1):
        g[y][2] = 0
        g[y][15] = 0
    for x in range(1, COLS-1):
        g[2][x] = 0
        g[6][x] = 0
        g[10][x] = 0
        g[15][x] = 0
    return g

base_grid = build_map()

def find_path_cells(start, grid):
    # BFS utility: used to ensure key and exit cells are connected.
    from collections import deque
    q = deque([start])
    seen = {start}
    while q:
        x,y = q.popleft()
        for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 < nx < COLS-1 and 0 < ny < ROWS-1 and grid[ny][nx] == 0 and (nx,ny) not in seen:
                seen.add((nx,ny))
                q.append((nx,ny))
    return seen

def make_game():
    global grid, player, player_x, player_y, health, score, keys, traps, doors
    global monster_x, monster_y, monster_stun, monster_target, monster_wander
    global hurt_timer, state, camera_x, camera_y, win_message_timer

    grid = [r[:] for r in base_grid]
    player_x, player_y = TILE*2+10.0, TILE*2+10.0
    player = pygame.Rect(round(player_x), round(player_y), PLAYER_SIZE, PLAYER_SIZE)
    health, score = 70, 0
    hurt_timer = 0.0
    win_message_timer = 0.0
    camera_x = camera_y = 0

    # These cells are deliberately on the guaranteed connected passages.
    key_cells = [(8,2), (18,6), (23,10)]
    keys = [{"rect": pygame.Rect(x*TILE+16, y*TILE+16, 18, 18), "taken": False}
            for x,y in key_cells]

    trap_cells = [(5,2), (10,6), (18,10), (24,15), (8,10), (22,6),
                  (4,6), (17,2), (27,10), (12,15), (7,6), (16,10),
                  (21,2), (25,6), (9,15)]
    traps = [{"rect": pygame.Rect(x*TILE+6, y*TILE+6, TILE-12, TILE-12),
              "active": True, "timer": random.uniform(0.15,0.7)} for x,y in trap_cells]

    # Doors sit directly on the open horizontal route. One collected key opens each door.
    door_cells = [(11,6), (18,10), (24,15)]
    doors = [{"rect": pygame.Rect(x*TILE+14, y*TILE+5, 22, TILE-10), "open": False}
             for x,y in door_cells]

    monster_x, monster_y = 25*TILE+10.0, 10*TILE+10.0
    monster_stun = 0.0
    monster_target = (monster_x, monster_y)
    monster_wander = 0.0
    state = "playing"

def collides_wall(rect, include_doors=True):
    # Use the tile just inside each edge; Rect.right/bottom are exclusive in Pygame.
    left = max(0, rect.left // TILE)
    right = min(COLS-1, max(0, (rect.right-1) // TILE))
    top = max(0, rect.top // TILE)
    bottom = min(ROWS-1, max(0, (rect.bottom-1) // TILE))
    for ty in range(top, bottom+1):
        for tx in range(left, right+1):
            if grid[ty][tx] and rect.colliderect(rect_for_cell(tx,ty)):
                return True
    if include_doors:
        for door in doors:
            if not door["open"] and rect.colliderect(door["rect"]):
                return True
    return False

def move_entity(x, y, dx, dy, width, height, include_doors=True):
    # Small substeps prevent tunnelling and never use an unbounded collision loop.
    rect = pygame.Rect(round(x), round(y), width, height)
    steps = max(1, math.ceil(max(abs(dx), abs(dy)) / 4))
    sx, sy = dx/steps, dy/steps
    for _ in range(steps):
        test = rect.copy()
        test.x = round(rect.x + sx)
        if not collides_wall(test, include_doors):
            rect.x = test.x
        test = rect.copy()
        test.y = round(rect.y + sy)
        if not collides_wall(test, include_doors):
            rect.y = test.y
    return float(rect.x), float(rect.y), rect

def text(s, font, color, x, y, center=False):
    img = font.render(s, True, color)
    r = img.get_rect()
    r.center = (x,y) if center else r.center
    if not center:
        r.topleft = (x,y)
    screen.blit(img,r)

def glow(color, center, radius):
    x,y = int(center[0]), int(center[1])
    for r,a in ((radius+12,18),(radius+6,34)):
        surf = pygame.Surface((r*2,r*2),pygame.SRCALPHA)
        pygame.draw.circle(surf,(*color,a),(r,r),r)
        screen.blit(surf,(x-r,y-r))
    pygame.draw.circle(screen,color,(x,y),radius)

def draw_game():
    global camera_x, camera_y
    camera_x = max(0,min(WORLD_W-WIDTH, player.centerx-WIDTH//2))
    camera_y = max(0,min(WORLD_H-HEIGHT, player.centery-HEIGHT//2))
    ox,oy = int(camera_x),int(camera_y)
    screen.fill(BLACK)

    for y in range(ROWS):
        for x in range(COLS):
            r = rect_for_cell(x,y).move(-ox,-oy)
            if r.right < 0 or r.left > WIDTH or r.bottom < 0 or r.top > HEIGHT:
                continue
            if grid[y][x]:
                pygame.draw.rect(screen,WALL,r)
                pygame.draw.rect(screen,WALL_EDGE,r,2)
            else:
                pygame.draw.rect(screen,FLOOR2 if (x+y)%2 else FLOOR,r)
                pygame.draw.rect(screen,(43,37,56),r,1)

    for d in doors:
        r=d["rect"].move(-ox,-oy)
        pygame.draw.rect(screen,(20,65,58) if d["open"] else (76,38,76),r,border_radius=5)
        pygame.draw.rect(screen,GREEN if d["open"] else PURPLE,r,2,border_radius=5)
        if not d["open"]:
            pygame.draw.circle(screen,GOLD,r.center,3)

    for t in traps:
        r=t["rect"].move(-ox,-oy)
        col=RED if t["active"] else (86,66,94)
        pygame.draw.rect(screen,(48,20,39),r,border_radius=5)
        pygame.draw.rect(screen,col,r,2,border_radius=5)
        if t["active"]:
            for k in range(3):
                xx=r.left+8+k*11
                pygame.draw.line(screen,col,(xx,r.top+6),(xx+7,r.bottom-6),2)

    for k in keys:
        if not k["taken"]:
            r=k["rect"].move(-ox,-oy)
            glow(GOLD,r.center,6)
            pygame.draw.circle(screen,WHITE,r.center,2)
            pygame.draw.line(screen,GOLD,(r.centerx+4,r.centery),(r.centerx+12,r.centery),3)

    exit_rect=pygame.Rect(28*TILE+8,15*TILE+8,34,34)
    er=exit_rect.move(-ox,-oy)
    glow(CYAN,er.center,12)
    pygame.draw.rect(screen,WHITE,er,2,border_radius=5)

    # Monster
    mr=pygame.Rect(round(monster_x)-ox,round(monster_y)-oy,MONSTER_W,MONSTER_H)
    glow(RED,(mr.centerx,mr.centery),18)
    pygame.draw.ellipse(screen,(54,13,30),mr)
    pygame.draw.circle(screen,WHITE,(mr.x+11,mr.y+15),3)
    pygame.draw.circle(screen,WHITE,(mr.x+28,mr.y+15),3)

    # Player
    pr=player.move(-ox,-oy)
    glow(CYAN,pr.center,11)
    pygame.draw.rect(screen,(16,61,78),pr,border_radius=6)
    pygame.draw.rect(screen,CYAN,pr,2,border_radius=6)
    pygame.draw.circle(screen,WHITE,(pr.centerx+4,pr.centery-3),3)

    # HUD and readable objective
    pygame.draw.rect(screen,(10,9,20),(0,0,WIDTH,48))
    pygame.draw.line(screen,PURPLE,(0,47),(WIDTH,47),2)
    text("HAUNTED ESCAPE",FONT,CYAN,12,11)
    text(f"KEYS {sum(k['taken'] for k in keys)}/{len(keys)}",SMALL,GOLD,255,15)
    text(f"SCORE {score}",SMALL,WHITE,390,15)
    text("HP",SMALL,WHITE,555,15)
    pygame.draw.rect(screen,(75,25,43),(590,16,130,17),border_radius=4)
    pygame.draw.rect(screen,GREEN if health>35 else RED,(590,16,int(130*max(0,health)/100),17),border_radius=4)
    text("E: OPEN DOOR",SMALL,(210,190,220),755,15)

def door_near_player():
    for d in doors:
        if not d["open"] and player.inflate(24,24).colliderect(d["rect"]):
            return d
    return None

def interact():
    global score
    d=door_near_player()
    if d is None:
        return
    if sum(k["taken"] for k in keys)>0:
        d["open"]=True
        score+=25
        beep(800,100)
    else:
        beep(180,120)

def update_monster(dt):
    global monster_x,monster_y,monster_stun,monster_target,monster_wander
    if monster_stun>0:
        monster_stun=max(0,monster_stun-dt)
        return
    dx=player.centerx-(monster_x+15)
    dy=player.centery-(monster_y+17)
    dist=math.hypot(dx,dy)
    if dist<700 and dist>1:
        vx,vy=dx/dist,dy/dist
    else:
        monster_wander-=dt
        if monster_wander<=0:
            cx=int(monster_x//TILE); cy=int(monster_y//TILE)
            candidates=[]
            for _ in range(30):
                tx=max(1,min(COLS-2,cx+random.randint(-5,5)))
                ty=max(1,min(ROWS-2,cy+random.randint(-4,4)))
                if grid[ty][tx]==0:
                    candidates.append((tx*TILE+10,ty*TILE+10))
            if candidates:
                monster_target=random.choice(candidates)
            monster_wander=random.uniform(1,2)
        dx,dy=monster_target[0]-monster_x,monster_target[1]-monster_y
        dist=math.hypot(dx,dy)
        if dist<2:
            return
        vx,vy=dx/dist,dy/dist
    monster_x,monster_y,_=move_entity(monster_x,monster_y,vx*175*dt,vy*175*dt,MONSTER_W,MONSTER_H,True)

def update(dt):
    global player_x,player_y,player,health,score,state,hurt_timer,monster_stun
    keysdown=pygame.key.get_pressed()
    dx=(int(keysdown[pygame.K_d] or keysdown[pygame.K_RIGHT])-int(keysdown[pygame.K_a] or keysdown[pygame.K_LEFT]))*PLAYER_SPEED*dt
    dy=(int(keysdown[pygame.K_s] or keysdown[pygame.K_DOWN])-int(keysdown[pygame.K_w] or keysdown[pygame.K_UP]))*PLAYER_SPEED*dt
    length=math.hypot(dx,dy)
    if length>PLAYER_SPEED*dt and length:
        dx*=PLAYER_SPEED*dt/length
        dy*=PLAYER_SPEED*dt/length
    player_x,player_y,player=move_entity(player_x,player_y,dx,dy,PLAYER_SIZE,PLAYER_SIZE,True)

    for k in keys:
        if not k["taken"] and player.colliderect(k["rect"]):
            k["taken"]=True
            score+=100
            beep(980,100)

    for t in traps:
        t["timer"]-=dt
        if t["timer"]<=0:
            t["active"]=not t["active"]
            t["timer"]=random.uniform(.3,.7)
        if t["active"] and player.colliderect(t["rect"]) and hurt_timer<=0:
            health-=25
            hurt_timer=.75
            beep(150,130)

    hurt_timer=max(0,hurt_timer-dt)
    update_monster(dt)
    mr=pygame.Rect(round(monster_x),round(monster_y),MONSTER_W,MONSTER_H)
    if player.colliderect(mr) and hurt_timer<=0:
        health-=35
        hurt_timer=1
        monster_stun=.3
        beep(110,160)
    if health<=0:
        health=0
        state="gameover"
        return

    exit_rect=pygame.Rect(28*TILE+8,15*TILE+8,34,34)
    if player.colliderect(exit_rect):
        if all(k["taken"] for k in keys):
            state="win"
            score+=250
            beep(1100,250)

def draw_menu():
    screen.fill((9,7,20))
    for i in range(10):
        x=25+i*105
        h=130+(i*53%180)
        pygame.draw.rect(screen,(25,17,42),(x,460-h,70,h))
        pygame.draw.polygon(screen,(40,23,55),((x-8,460-h),(x+35,420-h),(x+78,460-h)))
    text("HAUNTED",BIG,PURPLE,WIDTH//2,130,True)
    text("ESCAPE",BIG,CYAN,WIDTH//2,190,True)
    text("Collect all 3 keys. Avoid the red monster and traps.",FONT,WHITE,WIDTH//2,275,True)
    text("MOVE: WASD / ARROW KEYS",SMALL,WHITE,WIDTH//2,330,True)
    text("E: OPEN A NEARBY DOOR  |  ESC: QUIT",SMALL,GOLD,WIDTH//2,360,True)
    text("PRESS ENTER TO START",FONT,GREEN,WIDTH//2,430,True)

def overlay(title,subtitle,color):
    shade=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
    shade.fill((4,3,12,210))
    screen.blit(shade,(0,0))
    text(title,BIG,color,WIDTH//2,235,True)
    text(subtitle,FONT,WHITE,WIDTH//2,310,True)
    text("Press R to restart",SMALL,CYAN,WIDTH//2,360,True)

def main():
    global state
    state="menu"
    while True:
        dt=min(clock.tick(FPS)/1000,0.03)
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if state=="menu" and e.key in (pygame.K_RETURN,pygame.K_SPACE):
                    make_game()
                    beep(650,90)
                elif state in ("gameover","win") and e.key in (pygame.K_r,pygame.K_RETURN):
                    make_game()
                elif state=="playing" and e.key==pygame.K_e:
                    interact()

        if state=="menu":
            draw_menu()
        else:
            if state=="playing":
                update(dt)
            draw_game()
            if state=="gameover":
                overlay("GAME OVER","You were caught. Try again!",RED)
            elif state=="win":
                overlay("YOU ESCAPED!",f"Final score: {score}",GREEN)
        pygame.display.flip()

if __name__=="__main__":
    main()
