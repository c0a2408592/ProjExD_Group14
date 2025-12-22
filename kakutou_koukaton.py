import math
import pygame as pg
import sys
import os

# =====================
# 初期設定
# =====================
WIDTH, HEIGHT = 1000, 600
FLOOR = HEIGHT - 50
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Mini Street Fighter MAX")
clock = pg.time.Clock()

# =====================
# ファイター
# =====================
class Fighter(pg.sprite.Sprite):
    def __init__(self, x, color, keys):
        super().__init__()
        self.image = pg.Surface((60, 120))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, FLOOR)

        self.vx = 0
        self.vy = 0
        self.on_ground = True
        self.hp = 100
        self.energy = 100
        self.keys = keys
        self.facing = 1
        self.cooltime = 0
        self.throw_cool = 0

    def update(self, key_lst):
        self.vx = 0

        if key_lst[self.keys["left"]]:
            self.vx = -6
            self.facing = -1
        if key_lst[self.keys["right"]]:
            self.vx = 6
            self.facing = 1

        if key_lst[self.keys["jump"]] and self.on_ground:
            self.vy = -20
            self.on_ground = False

        self.vy += 1
        self.rect.x += self.vx
        self.rect.y += self.vy

        if self.rect.bottom >= FLOOR:
            self.rect.bottom = FLOOR
            self.vy = 0
            self.on_ground = True

        if self.cooltime > 0:
            self.cooltime -= 1
        if self.throw_cool > 0:
            self.throw_cool -= 1

        if self.energy < 100:
            self.energy += 0.1

# =====================
# 通常攻撃
# =====================
class Attack(pg.sprite.Sprite):
    def __init__(self, fighter):
        super().__init__()
        self.image = pg.Surface((40, 20))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()

        if fighter.facing == 1:
            self.rect.midleft = fighter.rect.midright
        else:
            self.rect.midright = fighter.rect.midleft

        self.life = 10

    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()

# =====================
# 飛び道具
# =====================
class Projectile(pg.sprite.Sprite):
    def __init__(self, fighter, kind):
        super().__init__()
        self.owner = fighter      # ← 所有者
        self.kind = kind          # ← 種類
        self.facing = fighter.facing

        if kind == "beam":  # 手裏剣
            self.image = pg.image.load("fig/syuriken.png").convert_alpha()
            self.image = pg.transform.scale(self.image, (40, 40))
            self.speed = 12
            self.damage = 10

        elif kind == "bomb":  # 螺旋丸
            self.image = pg.image.load("fig/rasengan1.png").convert_alpha()
            self.image = pg.transform.scale(self.image, (120, 120))
            self.speed = 8
            self.damage = 15

        elif kind == "rasensyuriken":  # 🔥 螺旋手裏剣
            self.image = pg.image.load("fig/rasensyuriken.png").convert_alpha()
            self.image = pg.transform.scale(self.image, (100, 100))
            self.speed = 8          # 螺旋丸と同じ
            self.damage = 30        # 高威力

        if self.facing == -1:
            self.image = pg.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()

        if self.facing == 1:
            self.rect.midleft = fighter.rect.midright
        else:
            self.rect.midright = fighter.rect.midleft

    def update(self):
        self.rect.x += self.speed * self.facing
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

# class Projectile(pg.sprite.Sprite):
#     def __init__(self, fighter, kind):
#         super().__init__()
#         self.facing = fighter.facing

#         if kind == "beam":
#             self.image = pg.image.load("fig/syuriken.png")
#             self.image = pg.transform.scale(self.image, (40, 40))
#             self.speed = 12
#             self.damage = 10
#         else:
#             self.image = pg.image.load("fig/rasengan1.png")
#             self.image = pg.transform.scale(self.image, (120, 120))
#             self.speed = 8
#             self.damage = 15

#         if self.facing == 1:
#             self.image = pg.transform.flip(self.image, True, False)

#         self.rect = self.image.get_rect()

#         if self.facing == 1:
#             self.rect.midleft = fighter.rect.midright
#         else:
#             self.rect.midright = fighter.rect.midleft

#     def update(self):
#         self.rect.x += self.speed * self.facing
#         if self.rect.right < 0 or self.rect.left > WIDTH:
#             self.kill()

# =====================
# 投げ技
# =====================
def try_throw(attacker, defender):
    if attacker.throw_cool > 0:
        return

    dist = abs(attacker.rect.centerx - defender.rect.centerx)
    height = abs(attacker.rect.bottom - defender.rect.bottom)

    if dist < 70 and height < 20:
        defender.hp -= 20

        # 🔥 強制後退（ノックバック）
        knock = 140
        defender.rect.x += knock * attacker.facing
        defender.vy = -15
        defender.on_ground = False

        attacker.energy = min(100, attacker.energy + 10)
        attacker.throw_cool = 40

# =====================
# メイン処理
# =====================
def main():
    fighters = pg.sprite.Group()
    attacks = pg.sprite.Group()
    projectiles = pg.sprite.Group()

    p1 = Fighter(200, (0, 100, 255), {
        "left": pg.K_a,
        "right": pg.K_d,
        "jump": pg.K_w,
        "attack": pg.K_f,
        "beam": pg.K_g,
        "bomb": pg.K_h,
        "throw": pg.K_t
    })

    p2 = Fighter(700, (255, 80, 80), {
        "left": pg.K_LEFT,
        "right": pg.K_RIGHT,
        "jump": pg.K_UP,
        "attack": pg.K_RSHIFT,
        "beam": pg.K_RALT,
        "bomb": pg.K_DELETE,
        "throw": pg.K_m   # ← Mキー
    })

    fighters.add(p1, p2)

    font = pg.font.Font(None, 50)
    small = pg.font.Font(None, 28)

    running = True
    while running:
        screen.fill((25, 25, 25))
        key_lst = pg.key.get_pressed()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.KEYDOWN:
                # 通常攻撃
                if event.key == p1.keys["attack"] and p1.cooltime == 0:
                    attacks.add(Attack(p1))
                    p1.cooltime = 15
                if event.key == p2.keys["attack"] and p2.cooltime == 0:
                    attacks.add(Attack(p2))
                    p2.cooltime = 15

                # 飛び道具
                if event.key == p1.keys["beam"] and p1.energy >= 20:
                    projectiles.add(Projectile(p1, "beam"))
                    p1.energy -= 20
                if event.key == p1.keys["bomb"] and p1.energy >= 30:
                    projectiles.add(Projectile(p1, "bomb"))
                    p1.energy -= 30

                if event.key == p2.keys["beam"] and p2.energy >= 20:
                    projectiles.add(Projectile(p2, "beam"))
                    p2.energy -= 20
                if event.key == p2.keys["bomb"] and p2.energy >= 30:
                    projectiles.add(Projectile(p2, "bomb"))
                    p2.energy -= 30

                # 投げ技
                if event.key == p1.keys["throw"]:
                    try_throw(p1, p2)
                if event.key == p2.keys["throw"]:
                    try_throw(p2, p1)

        fighters.update(key_lst)
        attacks.update()
        projectiles.update()

        import math
import pygame as pg
import sys
import os

# =====================
# 初期設定
# =====================
WIDTH, HEIGHT = 1000, 600
FLOOR = HEIGHT - 50
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Mini Street Fighter MAX")
clock = pg.time.Clock()

# =====================
# ファイター
# =====================
class Fighter(pg.sprite.Sprite):
    def __init__(self, x, color, keys):
        super().__init__()
        self.image = pg.Surface((60, 120))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, FLOOR)

        self.vx = 0
        self.vy = 0
        self.on_ground = True
        self.hp = 100
        self.energy = 100
        self.keys = keys
        self.facing = 1
        self.cooltime = 0
        self.throw_cool = 0

    def update(self, key_lst):
        self.vx = 0

        if key_lst[self.keys["left"]]:
            self.vx = -6
            self.facing = -1
        if key_lst[self.keys["right"]]:
            self.vx = 6
            self.facing = 1

        if key_lst[self.keys["jump"]] and self.on_ground:
            self.vy = -20
            self.on_ground = False

        self.vy += 1
        self.rect.x += self.vx
        self.rect.y += self.vy

        if self.rect.bottom >= FLOOR:
            self.rect.bottom = FLOOR
            self.vy = 0
            self.on_ground = True

        if self.cooltime > 0:
            self.cooltime -= 1
        if self.throw_cool > 0:
            self.throw_cool -= 1

        if self.energy < 100:
            self.energy += 0.1

# =====================
# 通常攻撃
# =====================
class Attack(pg.sprite.Sprite):
    def __init__(self, fighter):
        super().__init__()
        self.image = pg.Surface((40, 20))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()

        if fighter.facing == 1:
            self.rect.midleft = fighter.rect.midright
        else:
            self.rect.midright = fighter.rect.midleft

        self.life = 10

    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()

# =====================
# 飛び道具
# =====================
class Projectile(pg.sprite.Sprite):
    def __init__(self, fighter, kind):
        super().__init__()
        self.owner = fighter      # ← 所有者
        self.kind = kind          # ← 種類
        self.facing = fighter.facing
        self.angle = 0          
        self.rotate_speed = 0

        if kind == "beam":  # 手裏剣
            self.original_image = pg.image.load("fig/syuriken.png").convert_alpha()
            self.original_image = pg.transform.scale(self.original_image, (40, 40))
            self.image = self.original_image
            self.speed = 12
            self.damage = 10
            self.rotate_speed = 20


        elif kind == "bomb":  # 螺旋丸
            self.original_image = pg.image.load("fig/rasengan1.png").convert_alpha()
            self.original_image = pg.transform.scale(self.original_image, (120, 120))
            self.image = self.original_image
            self.speed = 8
            self.damage = 15
            self.rotate_speed = 0


        elif kind == "rasensyuriken":  # 🔥 螺旋手裏剣
            self.original_image = pg.image.load("fig/rasensyuriken.png").convert_alpha()
            self.original_image = pg.transform.scale(self.original_image, (100, 100))
            self.image = self.original_image
            self.speed = 8
            self.damage = 30
            self.rotate_speed = 10


        if self.facing == -1:
            self.image = pg.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()

        if self.facing == 1:
            self.rect.midleft = fighter.rect.midright
        else:
            self.rect.midright = fighter.rect.midleft

    def update(self):
        self.rect.x += self.speed * self.facing
        if self.rotate_speed != 0:
            self.angle = (self.angle + self.rotate_speed) % 360
            center = self.rect.center
            self.image = pg.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=center)
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

# class Projectile(pg.sprite.Sprite):
#     def __init__(self, fighter, kind):
#         super().__init__()
#         self.facing = fighter.facing

#         if kind == "beam":
#             self.image = pg.image.load("fig/syuriken.png")
#             self.image = pg.transform.scale(self.image, (40, 40))
#             self.speed = 12
#             self.damage = 10
#         else:
#             self.image = pg.image.load("fig/rasengan1.png")
#             self.image = pg.transform.scale(self.image, (120, 120))
#             self.speed = 8
#             self.damage = 15

#         if self.facing == 1:
#             self.image = pg.transform.flip(self.image, True, False)

#         self.rect = self.image.get_rect()

#         if self.facing == 1:
#             self.rect.midleft = fighter.rect.midright
#         else:
#             self.rect.midright = fighter.rect.midleft

#     def update(self):
#         self.rect.x += self.speed * self.facing
#         if self.rect.right < 0 or self.rect.left > WIDTH:
#             self.kill()

# =====================
# 投げ技
# =====================
def try_throw(attacker, defender):
    if attacker.throw_cool > 0:
        return

    dist = abs(attacker.rect.centerx - defender.rect.centerx)
    height = abs(attacker.rect.bottom - defender.rect.bottom)

    if dist < 70 and height < 20:
        defender.hp -= 20

        # 🔥 強制後退（ノックバック）
        knock = 140
        defender.rect.x += knock * attacker.facing
        defender.vy = -15
        defender.on_ground = False

        attacker.energy = min(100, attacker.energy + 10)
        attacker.throw_cool = 40

# =====================
# メイン処理
# =====================
def main():
    fighters = pg.sprite.Group()
    attacks = pg.sprite.Group()
    projectiles = pg.sprite.Group()

    p1 = Fighter(200, (0, 100, 255), {
        "left": pg.K_a,
        "right": pg.K_d,
        "jump": pg.K_w,
        "attack": pg.K_f,
        "beam": pg.K_g,
        "bomb": pg.K_h,
        "throw": pg.K_t
    })

    p2 = Fighter(700, (255, 80, 80), {
        "left": pg.K_LEFT,
        "right": pg.K_RIGHT,
        "jump": pg.K_UP,
        "attack": pg.K_RSHIFT,
        "beam": pg.K_RALT,
        "bomb": pg.K_DELETE,
        "throw": pg.K_m   # ← Mキー
    })

    fighters.add(p1, p2)

    font = pg.font.Font(None, 50)
    small = pg.font.Font(None, 28)

    running = True
    while running:
        screen.fill((25, 25, 25))
        key_lst = pg.key.get_pressed()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.KEYDOWN:
                # 通常攻撃
                if event.key == p1.keys["attack"] and p1.cooltime == 0:
                    attacks.add(Attack(p1))
                    p1.cooltime = 15
                if event.key == p2.keys["attack"] and p2.cooltime == 0:
                    attacks.add(Attack(p2))
                    p2.cooltime = 15

                # 飛び道具
                if event.key == p1.keys["beam"] and p1.energy >= 20:
                    projectiles.add(Projectile(p1, "beam"))
                    p1.energy -= 20
                if event.key == p1.keys["bomb"] and p1.energy >= 30:
                    projectiles.add(Projectile(p1, "bomb"))
                    p1.energy -= 30

                if event.key == p2.keys["beam"] and p2.energy >= 20:
                    projectiles.add(Projectile(p2, "beam"))
                    p2.energy -= 20
                if event.key == p2.keys["bomb"] and p2.energy >= 30:
                    projectiles.add(Projectile(p2, "bomb"))
                    p2.energy -= 30

                # 投げ技
                if event.key == p1.keys["throw"]:
                    try_throw(p1, p2)
                if event.key == p2.keys["throw"]:
                    try_throw(p2, p1)

        fighters.update(key_lst)
        attacks.update()
        projectiles.update()

        # =====================
        # 飛び道具融合判定
        # =====================
        for p1_proj in projectiles:
            for p2_proj in projectiles:
                if p1_proj == p2_proj:
                    continue

                # 同じプレイヤー ＆ 種類が違う
                if (p1_proj.owner == p2_proj.owner and
                    {p1_proj.kind, p2_proj.kind} == {"beam", "bomb"} and
                    pg.sprite.collide_rect(p1_proj, p2_proj)):

                    # 融合位置
                    x = (p1_proj.rect.centerx + p2_proj.rect.centerx) // 2
                    y = (p1_proj.rect.centery + p2_proj.rect.centery) // 2

                    # 削除
                    p1_proj.kill()
                    p2_proj.kill()

                    # 🔥 螺旋手裏剣生成
                    new_proj = Projectile(p1_proj.owner, "rasensyuriken")
                    new_proj.rect.center = (x, y)
                    projectiles.add(new_proj)

                    break


        # ヒット判定
        if pg.sprite.spritecollide(p1, attacks, True):
            p1.hp -= 5
        if pg.sprite.spritecollide(p2, attacks, True):
            p2.hp -= 5

        for proj in pg.sprite.spritecollide(p1, projectiles, True):
            p1.hp -= proj.damage
        for proj in pg.sprite.spritecollide(p2, projectiles, True):
            p2.hp -= proj.damage

        # 描画
        fighters.draw(screen)
        attacks.draw(screen)
        projectiles.draw(screen)

        # HP & ENERGY
        pg.draw.rect(screen, (0,255,0), (50,30, max(0,p1.hp*2),20))
        pg.draw.rect(screen, (255,255,0), (50,55, max(0,p1.energy*2),15))

        pg.draw.rect(screen, (0,255,0), (WIDTH-250,30, max(0,p2.hp*2),20))
        pg.draw.rect(screen, (255,255,0), (WIDTH-250,55, max(0,p2.energy*2),15))

        if p1.hp <= 0 or p2.hp <= 0:
            winner = "P2 WIN!" if p1.hp <= 0 else "P1 WIN!"
            screen.blit(font.render(winner, True, (255,0,0)),
                        (WIDTH//2-100, HEIGHT//2-40))
            pg.display.update()
            pg.time.delay(2000)
            return

        pg.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pg.quit()
    sys.exit()

