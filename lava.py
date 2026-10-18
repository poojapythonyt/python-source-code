
import math, random, pygame
pygame.init()
W,H=1000,650
screen=pygame.display.set_mode((W,H)); pygame.display.set_caption('LAVA ESCAPE: ENDLESS RUN')
clock=pygame.time.Clock(); F=pygame.font.SysFont('consolas',22,bold=True); S=pygame.font.SysFont('consolas',16,bold=True); T=pygame.font.SysFont('consolas',62,bold=True)
WHITE=(245,247,255); CYAN=(70,235,255); GOLD=(255,215,70); ORANGE=(255,115,28); RED=(255,65,55)
def text(msg,font,col,x,y,center=False):
    im=font.render(msg,True,col); r=im.get_rect(); r.center=(x,y) if center else (x,y); r.center=(x,y) if center else r.center
    if not center:r.topleft=(x,y)
    screen.blit(im,r)
def platform(x,y,w,kind='normal'): return {'r':pygame.Rect(int(x),int(y),int(w),18),'kind':kind,'lit':False}
def reset():
    global player,vx,vy,ground,camera,plats,pickups,nextx,nexty,lava,score,coins,height,elapsed,parts,state,jbuf,coyote
    player=pygame.Rect(100,470,30,42); vx=vy=0.; ground=False; camera=0.
    plats=[platform(25,535,190),platform(270,480,135),platform(465,420,125),platform(660,360,135),platform(450,300,120),platform(235,245,130,'checkpoint'),platform(35,190,125)]
    nextx,nexty=245,135; pickups=[]; lava=710.; score=coins=0; height=elapsed=0.; parts=[]; state='menu'; jbuf=coyote=0.
def emit(x,y,n,c):
    for _ in range(n):parts.append([float(x),float(y),random.uniform(-150,150),random.uniform(-230,-35),random.uniform(.25,.7),random.randint(2,5),c])
def makebg():
    b=pygame.Surface((W,H)); a=(10,16,42); z=(49,25,48)
    for y in range(H):
        t=y/H; pygame.draw.line(b,tuple(round(a[i]*(1-t)+z[i]*t) for i in range(3)),(0,y),(W,y))
    for x,pk,w in [(-70,310,300),(130,360,340),(390,285,340),(650,335,300),(830,280,300)]:pygame.draw.polygon(b,(24,24,48),[(x,H),(x+w//2,pk),(x+w,H)])
    for _ in range(120):pygame.draw.circle(b,random.choice([(66,80,123),(104,64,66),(62,104,125)]),(random.randrange(W),random.randrange(H)),random.choice([1,1,2]))
    return b
BG=makebg(); reset()
def generate():
    global nextx,nexty
    while nexty>camera-900:
        gap=64; nexty-=gap; w=random.randint(95,145); nextx=max(12,min(W-w-12,nextx+random.randint(-205,205)))
        kind='checkpoint' if int(abs(nexty)//900)!=int(abs(nexty+gap)//900) else 'normal'; plats.append(platform(nextx,nexty,w,kind))
        if random.random()<.68:pickups.append({'x':nextx+w//2,'y':nexty-30,'type':'coin','taken':False,'phase':random.random()*6.28})
        if random.random()<.1:pickups.append({'x':nextx+random.randint(20,max(21,w-20)),'y':nexty-28,'type':'boost','taken':False,'phase':random.random()*6.28})
def drawworld():
    for p in plats:
        q=p['r']; r=pygame.Rect(q.x,round(q.y-camera),q.w,q.h); pygame.draw.rect(screen,(29,36,64),r,border_radius=5); pygame.draw.rect(screen,GOLD if p['kind']=='checkpoint' else (105,133,177),(r.x,r.y,r.w,5),border_radius=3)
        for x in range(r.x+12,r.right-5,30):pygame.draw.line(screen,(46,59,91),(x,r.y+8),(x+7,r.bottom-3),2)
        if p['kind']=='checkpoint':pygame.draw.circle(screen,GOLD,(r.centerx,r.y-7),4)
    for it in pickups:
        if it['taken']:continue
        x=int(it['x']); y=int(it['y']-camera+math.sin(elapsed*4+it['phase'])*4)
        if -30<y<H+30:
            if it['type']=='coin':pygame.draw.circle(screen,(120,76,15),(x,y),11); pygame.draw.circle(screen,GOLD,(x,y),8); pygame.draw.circle(screen,(255,245,160),(x-2,y-3),2)
            else:pygame.draw.circle(screen,(32,120,92),(x,y),12); pygame.draw.circle(screen,(80,255,170),(x,y),8,2); pygame.draw.polygon(screen,(150,255,205),[(x,y-6),(x+5,y),(x,y+6),(x-5,y)])
def drawlava():
    sy=int(lava-camera)
    if sy<H:
        sy=max(-12,sy); pygame.draw.rect(screen,(110,30,19),(0,sy-8,W,H-sy+8)); pygame.draw.rect(screen,(255,70,22),(0,sy,W,H-sy)); pygame.draw.rect(screen,(255,170,38),(0,sy,W,6))
        for i in range(22):
            x=(i*59+int(elapsed*90))%(W+35)-15; y=sy+15+int(math.sin(elapsed*4+i)*5); pygame.draw.ellipse(screen,(255,random.randint(105,175),24),(x,y,20,7))
def hud():
    pygame.draw.rect(screen,(8,12,29),(15,14,270,91),border_radius=12); pygame.draw.rect(screen,(67,83,128),(15,14,270,91),2,border_radius=12)
    text(f'SCORE {score:06d}',F,WHITE,29,24); text(f'COINS {coins:03d}',S,GOLD,30,58); text(f'HEIGHT {int(height):04d} m',S,CYAN,145,58)
    pygame.draw.rect(screen,(37,43,64),(W-220,22,190,14),border_radius=7); danger=max(0,min(1,(H-(lava-camera))/H)); pygame.draw.rect(screen,ORANGE,(W-220,22,int(190*danger),14),border_radius=7); text('LAVA DANGER',S,WHITE,W-220,43)
    text('A/D or arrows: move   SPACE: jump   P: pause   R: restart',S,(205,214,240),W//2,H-27,True)
def overlay(title,subtitle,color,lines):
    shade=pygame.Surface((W,H),pygame.SRCALPHA); shade.fill((4,7,20,210)); screen.blit(shade,(0,0)); text(title,T,color,W//2,H//2-110,True); text(subtitle,F,WHITE,W//2,H//2-40,True)
    for i,line in enumerate(lines):text(line,S,(196,208,236),W//2,H//2+10+i*27,True)
def start():
    global state; state='playing'
running=True
while running:
    dt=min(clock.tick(60)/1000,0.033)
    for e in pygame.event.get():
        if e.type==pygame.QUIT:running=False
        elif e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE:running=False
            elif e.key==pygame.K_r:reset(); start()
            elif e.key==pygame.K_p:state='paused' if state=='playing' else ('playing' if state=='paused' else state)
            elif e.key in (pygame.K_SPACE,pygame.K_w,pygame.K_UP):
                if state=='menu':start()
                elif state=='gameover':reset();start()
                elif state=='playing':jbuf=.15
        elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            if state in ('menu','gameover'):
                if state=='gameover':reset()
                start()
    if state=='playing':
        elapsed+=dt; keys=pygame.key.get_pressed(); direction=int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]); vx=direction*310; player.x=max(0,min(W-player.w,player.x+round(vx*dt))); oldbottom=player.bottom
        jbuf=max(0,jbuf-dt); coyote=.12 if ground else max(0,coyote-dt)
        if jbuf>0 and coyote>0:vy=-625;ground=False;coyote=0;jbuf=0;emit(player.centerx,player.bottom,8,CYAN)
        vy+=1550*dt; player.y+=round(vy*dt); ground=False
        if vy>=0:
            for p in plats:
                r=p['r']
                if player.right>r.left and player.left<r.right and oldbottom<=r.top+8 and player.bottom>=r.top:
                    player.bottom=r.top;vy=0;ground=True
                    if p['kind']=='checkpoint' and not p['lit']:p['lit']=True;emit(r.centerx,r.top,16,GOLD)
                    break
        for it in pickups:
            if not it['taken'] and player.colliderect(pygame.Rect(int(it['x']-10),int(it['y']-10),20,20)):
                it['taken']=True
                if it['type']=='coin':coins+=1;score+=100;emit(it['x'],it['y'],10,GOLD)
                else:vy=-790;ground=False;emit(it['x'],it['y'],14,(80,255,170))
        target=player.centery-H*.56
        if target<camera:camera+=(target-camera)*min(1,dt*5)
        height=max(height,max(0,(535-player.y)/10));score+=int(height*dt*.35);lava-=(30+min(elapsed*.9,63))*dt
        if player.bottom>=lava or player.top>camera+H+80:state='gameover';emit(player.centerx,player.centery,32,ORANGE)
        generate();plats=[p for p in plats if p['r'].top<camera+H+220];pickups=[p for p in pickups if p['y']<camera+H+240 and not(p['taken'] and p['y']>camera+H)]
    for p in parts[:]:
        p[0]+=p[2]*dt;p[1]+=p[3]*dt;p[3]+=380*dt;p[4]-=dt
        if p[4]<=0:parts.remove(p)
    screen.blit(BG,(0,0))
    for i in range(24):pygame.draw.circle(screen,(108,57,49),((i*47+int(elapsed*20))%W,(i*83+int(elapsed*29))%H),2)
    drawworld();drawlava()
    for p in parts:
        sy=int(p[1]-camera)
        if -10<=sy<=H:pygame.draw.circle(screen,p[6],(int(p[0]),sy),max(1,int(p[5]*min(1,p[4]*2))))
    pr=pygame.Rect(player.x,round(player.y-camera),player.w,player.h); glow=pygame.Surface((70,80),pygame.SRCALPHA);pygame.draw.ellipse(glow,(50,220,255,35),(5,5,60,65));screen.blit(glow,(pr.centerx-35,pr.centery-40));pygame.draw.rect(screen,(34,43,76),pr,border_radius=7);pygame.draw.rect(screen,CYAN,(pr.x+4,pr.y+6,pr.w-8,10),border_radius=4);pygame.draw.rect(screen,(180,255,255),(pr.x+7,pr.y+8,pr.w-14,3),border_radius=2);pygame.draw.rect(screen,(83,102,153),(pr.x+4,pr.bottom-9,8,7),border_radius=2);pygame.draw.rect(screen,(83,102,153),(pr.right-12,pr.bottom-9,8,7),border_radius=2)
    hud()
    if state=='menu':overlay('LAVA ESCAPE','ENDLESS PLATFORM SURVIVAL',CYAN,('Climb forever while the lava rises!','Collect coins and green jump boosts.','SPACE / W / UP to start','A/D or arrows move | P pause | R restart'))
    elif state=='paused':overlay('PAUSED','Take a breath — the lava waits for nobody.',GOLD,('Press P to continue','Press R to restart'))
    elif state=='gameover':overlay('GAME OVER',f'Score: {score}   Coins: {coins}   Height: {int(height)} m',RED,('Press SPACE or click to try again','Press R to restart immediately','Tip: jump before reaching the edge!'))
    pygame.display.flip()
pygame.quit()
