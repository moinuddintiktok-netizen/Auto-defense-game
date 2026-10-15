"""
PYTHON AUTO DEFENSE: OVERDRIVE
Created by Chishti Bro Computers & Developers
Founder: Moinuddin Chishti

A vertical neon sci-fi auto-defense shooter built with Pygame.
Controls:
  A/D or Left/Right : Move ship
  Mouse             : Move ship
  SPACE              : Burst/overdrive ability
  P / ESC            : Pause
  R                  : Restart
  M                  : Toggle sound flag
  F11                : Fullscreen
"""
import math
import random
import sys
import json
from pathlib import Path

import pygame

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

W, H = 900, 900
FPS = 60
TITLE = "PYTHON AUTO DEFENSE: OVERDRIVE"
SAVE_FILE = Path.home() / ".python_auto_defense.json"

BG = (4, 8, 20)
WHITE = (236, 250, 255)
CYAN = (50, 225, 255)
BLUE = (50, 115, 255)
PURPLE = (190, 75, 255)
PINK = (255, 50, 165)
GOLD = (255, 202, 70)
GREEN = (65, 255, 165)
RED = (255, 65, 90)
MUTED = (105, 140, 175)

screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
FONT_S = pygame.font.SysFont("consolas", 16, bold=True)
FONT_M = pygame.font.SysFont("consolas", 22, bold=True)
FONT_L = pygame.font.SysFont("consolas", 34, bold=True)
FONT_XL = pygame.font.SysFont("consolas", 49, bold=True)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def label(surf, text, fnt, color, pos, center=False):
    img = fnt.render(str(text), True, color)
    rect = img.get_rect()
    rect.center = pos if center else rect.center
    if not center:
        rect.topleft = pos
    shadow = fnt.render(str(text), True, (0, 20, 35))
    surf.blit(shadow, rect.move(2, 2))
    surf.blit(img, rect)
    return rect

def neon_box(surf, rect, color, radius=8):
    rect = pygame.Rect(rect)
    for width, alpha in ((8, 18), (4, 45)):
        layer = pygame.Surface((rect.w + 18, rect.h + 18), pygame.SRCALPHA)
        pygame.draw.rect(layer, (*color, alpha), layer.get_rect(), width=width, border_radius=radius+4)
        surf.blit(layer, (rect.x-9, rect.y-9))
    pygame.draw.rect(surf, color, rect, width=2, border_radius=radius)

class Particle:
    def __init__(self, x, y, color, speed=1):
        a = random.random() * math.tau
        v = random.uniform(45, 260) * speed
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = math.cos(a)*v, math.sin(a)*v
        self.life = self.maxlife = random.uniform(.25, .75)
        self.color = color
        self.size = random.randint(2, 5)
    def update(self, dt):
        self.life -= dt
        self.x += self.vx*dt
        self.y += self.vy*dt
        self.vx *= .985
        self.vy *= .985
    def draw(self, surf):
        if self.life > 0:
            r = max(1, int(self.size*self.life/self.maxlife))
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), r)

class FloatingText:
    def __init__(self, x, y, text, color):
        self.x, self.y, self.text, self.color = x, y, text, color
        self.life = 1.0
    def update(self, dt):
        self.life -= dt
        self.y -= 34*dt
    def draw(self, surf):
        if self.life > 0:
            img = FONT_S.render(self.text, True, self.color)
            img.set_alpha(int(255*min(1, self.life*2)))
            surf.blit(img, img.get_rect(center=(int(self.x), int(self.y))))

class Bullet:
    def __init__(self, x, y, vx=0, vy=-620, color=CYAN, damage=1, homing=False):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.color, self.damage, self.homing = color, damage, homing
        self.radius = 4
    def update(self, dt, enemies):
        if self.homing and enemies:
            target = min(enemies, key=lambda e: (e.x-self.x)**2+(e.y-self.y)**2)
            dx, dy = target.x-self.x, target.y-self.y
            length = max(1, math.hypot(dx, dy))
            self.vx += dx/length*400*dt
            self.vy += dy/length*400*dt
            speed = math.hypot(self.vx, self.vy)
            if speed > 680:
                self.vx, self.vy = self.vx/speed*680, self.vy/speed*680
        self.x += self.vx*dt
        self.y += self.vy*dt
    def draw(self, surf):
        pygame.draw.line(surf, self.color, (int(self.x), int(self.y+10)), (int(self.x), int(self.y-8)), 4)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y-7)), 2)

class Enemy:
    def __init__(self, lane, wave, kind="scout"):
        self.lane = lane
        self.x = 110 + lane*85
        self.y = -random.randint(30, 160)
        self.kind = kind
        self.hp = 1 if kind == "scout" else (3 if kind == "tank" else 2)
        self.maxhp = self.hp
        self.speed = random.uniform(95, 145) + wave*5
        if kind == "tank":
            self.speed *= .7
            self.radius = 20
            self.color = PURPLE
        elif kind == "swift":
            self.speed *= 1.45
            self.radius = 12
            self.color = GOLD
        else:
            self.radius = 15
            self.color = RED
        self.phase = random.random()*math.tau
    def update(self, dt, wave):
        self.y += self.speed*dt
        self.phase += dt*3
        if self.kind == "swift":
            self.x += math.sin(self.phase)*45*dt
        else:
            self.x += math.sin(self.phase)*12*dt
    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        pts = [(x, y-self.radius), (x+self.radius, y-2), (x+self.radius//2, y+self.radius), (x-self.radius//2, y+self.radius), (x-self.radius, y-2)]
        pygame.draw.polygon(surf, self.color, pts)
        pygame.draw.polygon(surf, WHITE, pts, 2)
        pygame.draw.circle(surf, (255, 220, 230), (x, y), 3)
        if self.maxhp > 1:
            bar = pygame.Rect(x-self.radius, y-self.radius-9, self.radius*2, 4)
            pygame.draw.rect(surf, (50, 30, 50), bar)
            pygame.draw.rect(surf, GREEN, (bar.x, bar.y, int(bar.w*self.hp/self.maxhp), bar.h))

class PowerUp:
    TYPES = ["rapid", "spread", "shield", "repair", "drone", "bomb"]
    COLORS = {"rapid": GOLD, "spread": PURPLE, "shield": BLUE, "repair": GREEN, "drone": CYAN, "bomb": PINK}
    SYMBOLS = {"rapid": "R", "spread": "3", "shield": "S", "repair": "+", "drone": "D", "bomb": "B"}
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.kind = random.choice(self.TYPES)
        self.rect = pygame.Rect(int(x-14), int(y-14), 28, 28)
    def update(self, dt):
        self.y += 125*dt
        self.rect.center = int(self.x), int(self.y)
    def draw(self, surf):
        c = self.COLORS[self.kind]
        pygame.draw.circle(surf, c, self.rect.center, 15, 2)
        label(surf, self.SYMBOLS[self.kind], FONT_S, c, self.rect.center, True)

class Game:
    def __init__(self):
        try:
            self.best = int(json.loads(SAVE_FILE.read_text()).get("best", 0))
        except Exception:
            self.best = 0
        self.fullscreen = False
        self.reset()
    def reset(self):
        self.score = 0
        self.wave = 1
        self.lives = 3
        self.combo = 0
        self.max_combo = 0
        self.kills = 0
        self.state = "menu"
        self.player_x = W/2
        self.player_y = H-105
        self.player_speed = 470
        self.hp = 100
        self.shield = 0
        self.rapid = 0
        self.spread = 0
        self.drone = 0
        self.fire_timer = 0
        self.spawn_timer = 0
        self.wave_kills = 0
        self.bomb_ready = True
        self.bullets, self.enemy_bullets, self.enemies, self.powerups = [], [], [], []
        self.particles, self.texts = [], []
        self.shake = 0
        self.stars = [(random.randrange(W), random.randrange(H), random.choice([1,1,2])) for _ in range(100)]
        self.lanes = [110+i*85 for i in range(9)]
    def save(self):
        try:
            SAVE_FILE.write_text(json.dumps({"best": self.best}))
        except Exception:
            pass
    def burst(self, x, y, color, n=14):
        self.particles.extend(Particle(x, y, color, random.uniform(.5,1.25)) for _ in range(n))
    def pop(self, x, y, text, color=WHITE):
        self.texts.append(FloatingText(x, y, text, color))
    def spawn_enemy(self):
        lane = random.randrange(9)
        roll = random.random()
        kind = "tank" if self.wave >= 3 and roll < .18 else ("swift" if roll < .42 else "scout")
        self.enemies.append(Enemy(lane, self.wave, kind))
    def shoot(self):
        self.bullets.append(Bullet(self.player_x-12, self.player_y-18, color=CYAN))
        self.bullets.append(Bullet(self.player_x+12, self.player_y-18, color=BLUE))
        if self.spread > 0:
            self.bullets.append(Bullet(self.player_x, self.player_y-15, -150, -570, PURPLE))
            self.bullets.append(Bullet(self.player_x, self.player_y-15, 150, -570, PURPLE))
        if self.drone > 0:
            self.bullets.append(Bullet(self.player_x-50, self.player_y-4, -30, -600, GREEN, homing=True))
            self.bullets.append(Bullet(self.player_x+50, self.player_y-4, 30, -600, GREEN, homing=True))
    def activate_bomb(self):
        if self.bomb_ready:
            for e in self.enemies[:]:
                self.burst(e.x, e.y, PINK, 8)
                self.score += 50
            self.enemies.clear()
            self.enemy_bullets.clear()
            self.bomb_ready = False
            self.pop(self.player_x, self.player_y-75, "NEXUS PULSE!", PINK)
            self.shake = .25
    def apply_power(self, kind):
        if kind == "rapid": self.rapid = 9
        elif kind == "spread": self.spread = 10
        elif kind == "shield": self.shield = 8
        elif kind == "repair": self.hp = min(100, self.hp+35)
        elif kind == "drone": self.drone = 10
        elif kind == "bomb": self.bomb_ready = True
        self.pop(self.player_x, self.player_y-55, kind.upper()+" UPGRADE", PowerUp.COLORS[kind])
    def events(self):
        mouse_x = None
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.save(); pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    pygame.display.set_mode((0,0), pygame.FULLSCREEN) if self.fullscreen else pygame.display.set_mode((W,H), pygame.RESIZABLE)
                elif e.key in (pygame.K_p, pygame.K_ESCAPE):
                    if self.state == "playing": self.state = "paused"
                    elif self.state == "paused": self.state = "playing"
                elif e.key == pygame.K_r:
                    self.reset(); self.state = "playing"
                elif e.key == pygame.K_SPACE:
                    if self.state in ("menu","gameover"):
                        self.reset(); self.state = "playing"
                    elif self.state == "paused": self.state = "playing"
                    else: self.activate_bomb()
            if e.type == pygame.MOUSEMOTION:
                mouse_x = e.pos[0]*W/max(1, pygame.display.get_surface().get_width())
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.state in ("menu","gameover"):
                    self.reset(); self.state = "playing"
                elif self.state == "paused": self.state = "playing"
                else: self.activate_bomb()
            if e.type in (pygame.FINGERMOTION, pygame.FINGERDOWN):
                mouse_x = e.x*W
                if e.type == pygame.FINGERDOWN and self.state == "menu":
                    self.state = "playing"
        return mouse_x
    def update(self, dt, mouse_x):
        for p in self.particles: p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]
        for t in self.texts: t.update(dt)
        self.texts = [t for t in self.texts if t.life > 0]
        if self.state != "playing": return
        keys = pygame.key.get_pressed()
        direction = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.player_x += direction*self.player_speed*dt
        if mouse_x is not None:
            self.player_x += (mouse_x-self.player_x)*min(1,dt*12)
        self.player_x = clamp(self.player_x, 75, W-75)
        for attr in ("shield","rapid","spread","drone"):
            setattr(self, attr, max(0, getattr(self, attr)-dt))
        self.fire_timer -= dt
        if self.fire_timer <= 0:
            self.shoot()
            self.fire_timer = .105 if self.rapid > 0 else .23
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = max(.22, .85-self.wave*.035)
        for b in self.bullets:
            b.update(dt, self.enemies)
        self.bullets = [b for b in self.bullets if -30 < b.y < H+30 and -30 < b.x < W+30]
        for e in self.enemies:
            e.update(dt, self.wave)
        for p in self.powerups: p.update(dt)
        # Player projectiles hit enemies.
        for b in self.bullets[:]:
            hit = None
            for e in self.enemies:
                if (e.x-b.x)**2+(e.y-b.y)**2 < (e.radius+7)**2:
                    hit = e; break
            if hit:
                hit.hp -= b.damage
                if b in self.bullets: self.bullets.remove(b)
                self.burst(b.x,b.y,hit.color,3)
                if hit.hp <= 0 and hit in self.enemies:
                    self.enemies.remove(hit)
                    self.score += 100 + min(self.combo, 20)*10
                    self.combo += 1
                    self.max_combo = max(self.max_combo,self.combo)
                    self.kills += 1; self.wave_kills += 1
                    self.burst(hit.x,hit.y,hit.color,15)
                    self.pop(hit.x,hit.y,"+100",GOLD)
                    if random.random() < .13:
                        self.powerups.append(PowerUp(hit.x,hit.y))
        # Enemy bullets and enemy contact damage.
        for eb in self.enemy_bullets[:]:
            eb[1] += eb[2]*dt
            if eb[1] > H: self.enemy_bullets.remove(eb); continue
            if self.shield <= 0 and abs(eb[0]-self.player_x)<23 and abs(eb[1]-self.player_y)<25:
                self.enemy_bullets.remove(eb); self.hp -= 12; self.shake=.12
        for e in self.enemies[:]:
            if e.y > H-160:
                self.enemies.remove(e)
                if self.shield <= 0:
                    self.hp -= 18 if e.kind=="tank" else 10
                    self.burst(self.player_x,self.player_y,RED,8)
                    self.shake=.12
        for p in self.powerups[:]:
            if abs(p.x-self.player_x)<42 and abs(p.y-self.player_y)<35:
                self.apply_power(p.kind); self.powerups.remove(p); self.burst(p.x,p.y,PowerUp.COLORS[p.kind],12)
            elif p.y > H+20: self.powerups.remove(p)
        self.hp = clamp(self.hp,0,100)
        if self.hp <= 0:
            self.state="gameover"; self.best=max(self.best,self.score); self.save()
        if self.wave_kills >= self.wave*12:
            self.wave += 1; self.wave_kills = 0
            self.hp = min(100,self.hp+12)
            self.pop(W/2, H*.35, f"WAVE {self.wave} INCOMING", CYAN)
        if self.shake > 0: self.shake -= dt
    def background(self, surf):
        surf.fill(BG)
        for x,y,r in self.stars:
            yy = (y + pygame.time.get_ticks()*.025) % H
            pygame.draw.circle(surf,(20,45,78),(x,int(yy)),r)
        for x in self.lanes:
            pygame.draw.line(surf,(12,28,52),(x,90),(x,H-70),1)
            pygame.draw.line(surf,(22,65,100),(x-18,H-130),(x-18,H-75),2)
            pygame.draw.line(surf,(22,65,100),(x+18,H-130),(x+18,H-75),2)
        pygame.draw.line(surf,(20,70,110),(35,78),(W-35,78),2)
        pygame.draw.line(surf,CYAN,(35,78),(180,78),3)
        pygame.draw.line(surf,PURPLE,(W-180,78),(W-35,78),3)
    def draw_player(self, surf):
        x,y=int(self.player_x),int(self.player_y)
        if self.shield>0:
            pygame.draw.circle(surf,BLUE,(x,y),45,3)
            pygame.draw.circle(surf,(45,100,220),(x,y),51,1)
        # Engine glow
        pygame.draw.polygon(surf,(20,100,255),[(x-14,y+20),(x,y+48),(x+14,y+20)])
        pygame.draw.polygon(surf,CYAN,[(x-30,y+12),(x-14,y-15),(x+14,y-15),(x+30,y+12),(x+12,y+8),(x,y+22),(x-12,y+8)])
        pygame.draw.polygon(surf,WHITE,[(x-30,y+12),(x-14,y-15),(x+14,y-15),(x+30,y+12),(x+12,y+8),(x,y+22),(x-12,y+8)],2)
        pygame.draw.polygon(surf,PURPLE,[(x-8,y-9),(x,y-22),(x+8,y-9)])
        if self.drone>0:
            for dx in (-52,52):
                pygame.draw.circle(surf,GREEN,(x+dx,y+5),9,2)
                pygame.draw.circle(surf,WHITE,(x+dx,y+5),3)
    def draw_hud(self,surf):
        label(surf,"PYTHON AUTO DEFENSE",FONT_M,CYAN,(24,18))
        label(surf,"OVERDRIVE // SECTOR 07",FONT_S,MUTED,(26,45))
        label(surf,f"SCORE {self.score:07d}",FONT_M,WHITE,(W/2,28),True)
        label(surf,f"BEST {max(self.best,self.score):07d}",FONT_S,GOLD,(W/2,53),True)
        label(surf,f"WAVE {self.wave:02d}",FONT_M,GOLD,(W-150,20))
        label(surf,f"COMBO x{self.combo}",FONT_S,PINK,(W-150,48))
        # health bar
        pygame.draw.rect(surf,(25,35,58),(24,H-42,220,13),border_radius=6)
        pygame.draw.rect(surf,GREEN if self.hp>35 else RED,(24,H-42,int(220*self.hp/100),13),border_radius=6)
        label(surf,f"HULL {int(self.hp)}%",FONT_S,WHITE,(24,H-66))
        label(surf,"SPACE: NEXUS PULSE" if self.bomb_ready else "PULSE RECHARGING",FONT_S,PINK if self.bomb_ready else MUTED,(W-260,H-42))
        active=[]
        if self.rapid>0: active.append(f"RAPID {self.rapid:.0f}s")
        if self.spread>0: active.append(f"SPREAD {self.spread:.0f}s")
        if self.shield>0: active.append(f"SHIELD {self.shield:.0f}s")
        if self.drone>0: active.append(f"DRONES {self.drone:.0f}s")
        if active: label(surf,"  |  ".join(active),FONT_S,GREEN,(W/2,H-15),True)
    def overlay(self,surf,title,lines,color):
        shade=pygame.Surface((W,H),pygame.SRCALPHA); shade.fill((1,4,15,220)); surf.blit(shade,(0,0))
        neon_box(surf,(70,H/2-190,W-140,380),color,18)
        label(surf,title,FONT_XL,color,(W/2,H/2-125),True)
        for i,line in enumerate(lines):
            label(surf,line,FONT_M if i==0 else FONT_S,WHITE if i==0 else MUTED,(W/2,H/2-45+i*38),True)
        label(surf,"CHISHTI BRO COMPUTERS & DEVELOPERS",FONT_S,GOLD,(W/2,H/2+145),True)
    def draw(self):
        self.background(screen)
        self.draw_hud(screen)
        for b in self.bullets: b.draw(screen)
        for eb in self.enemy_bullets:
            pygame.draw.circle(screen,PINK,(int(eb[0]),int(eb[1])),5)
            pygame.draw.circle(screen,WHITE,(int(eb[0]),int(eb[1])),2)
        for e in self.enemies: e.draw(screen)
        for p in self.powerups: p.draw(screen)
        self.draw_player(screen)
        for p in self.particles: p.draw(screen)
        for t in self.texts: t.draw(screen)
        if self.state=="menu":
            self.overlay(screen,"AUTO DEFENSE",["SURVIVE THE NEON SWARM","Auto-fire • 9 lanes • Boss-grade waves • Upgrade drops","Move: A/D or arrows or mouse / touch","SPACE: Nexus Pulse clears enemies • P: Pause","PRESS SPACE OR TAP TO START"],CYAN)
        elif self.state=="paused":
            self.overlay(screen,"PAUSED",["Defenses on standby","Press P / ESC or tap to resume"],GOLD)
        elif self.state=="gameover":
            self.overlay(screen,"HULL BREACHED",[f"Final score: {self.score}","Enemies destroyed: "+str(self.kills)+f"  •  Best combo: x{self.max_combo}","Press R or SPACE to restart"],PINK)
        surf=pygame.display.get_surface()
        if surf.get_size()!=(W,H):
            surf.blit(pygame.transform.smoothscale(screen,surf.get_size()),(0,0))
        pygame.display.flip()
    def run(self):
        while True:
            dt=min(clock.tick(FPS)/1000,.035)
            mx=self.events()
            self.update(dt,mx)
            self.draw()

if __name__=="__main__":
    Game().run()
