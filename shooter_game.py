from pygame import *
from random import randint

m_w = display.set_mode((700, 500))
display.set_caption('Space')

background = transform.scale(image.load('galaxy.jpg'), (700, 500))
mixer.init()
mixer.music.load("space.ogg")
mixer.music.play()
fire = mixer.Sound('fire.ogg')

font.init()

def draw_result(text, color):
    image = font.SysFont("verdana", 40).render(text, True, color)
    rect = image.get_rect()
    m_w.blit(image, (350 - rect.w / 2, 250 - rect.h / 2))

def draw_counter(text, x, y):
    image = font.SysFont("verdana", 25).render(text, True, (255, 255, 255))
    m_w.blit(image, (x, y))

class GameSprite(sprite.Sprite):
    def __init__(self, filename, x, y, w, h):
        super().__init__()
        self.image = transform.scale(image.load(filename), (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self):
        m_w.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, filename, x, y, w, h, speed):
        super().__init__(filename, x, y, w, h)
        self.speed = speed
        self.ammo = 10
        self.reload_time = 1
        self.reset()

    def update(self):
        global dt
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 0:
            self.rect.x -= self.speed * dt

        if keys[K_d] and self.rect.x < 700 - self.rect.w:
            self.rect.x += self.speed * dt

        if self.is_reloading:
            self.reload_progress += dt

            if self.reload_progress > self.reload_time:
                self.is_reloading = False
                self.cur_ammo = self.ammo

    def fire(self):
        if self.is_reloading:
            return

        self.cur_ammo -= 1

        if self.cur_ammo == 0:
            self.is_reloading = True
            self.reload_progress = 0

        bullet = Bullet('bullet.png', 16, 32)
        bullet.rect.centerx = self.rect.centerx
        bullet.rect.y = self.rect.top
        bullets.add(bullet)
        fire.play()

    def reset(self):
        self.is_reloading = False
        self.cur_ammo = self.ammo
        self.reload_progress = 0
        self.rect.centerx = 350
        self.rect.y = 400

class Enemy(GameSprite):
    def __init__(self, filename, w, h):
        super().__init__(filename, 0, 0, w, h)
        self.pos_y = 0
        self.reset()

    def reset(self):
        self.rect.x = randint(5, 695 - self.rect.w)
        self.pos_y = randint(-200, -self.rect.h)
        self.rect.y = self.pos_y
        self.speed = randint(50, 150)

    def update(self):
        global dt, enemy_counter
        self.pos_y += self.speed * dt
        self.rect.y = self.pos_y
        if self.rect.y > 500:
            self.reset()
            enemy_counter += 1

class Bullet(GameSprite):
    def __init__(self, filename, w, h):
        super().__init__(filename, 0, 0, w, h)
        self.speed = 715

    def update(self):
        self.rect.y -= self.speed * dt

        if self.rect.y < -self.rect.h:
            self.kill()

class Asteroid(GameSprite):
    def __init__(self, filename, w, h):
        super().__init__(filename, 0, 0, w, h)
        self.pos_y = 0
        self.reset()

    def reset(self):
        self.rect.x = randint(5, 695 - self.rect.w)
        self.pos_y = randint(-200, -self.rect.h)
        self.rect.y = self.pos_y
        self.speed = randint(50, 150)

    def update(self):
        global dt, enemy_counter
        self.pos_y += self.speed * dt
        self.rect.y = self.pos_y
        

enemies = sprite.Group()
enemies.add(Enemy('ufo.png', 96, 48))
enemies.add(Enemy('ufo.png', 96, 48))
enemies.add(Enemy('ufo.png', 96, 48))
enemies.add(Enemy('ufo.png', 96, 48))
enemies.add(Enemy('ufo.png', 96, 48))
enemies.add(Enemy('ufo.png', 96, 48))

asteroids = sprite.Group()
asteroids.add(Asteroid('asteroid.png', 64, 64))
asteroids.add(Asteroid('asteroid.png', 64, 64))

bullets = sprite.Group()

player = Player('rocket.png', 300, 430, 64, 64, 500)

dt = 0
clock = time.Clock()

enemy_counter = 0
killed_score = 0

game = True
finished = False
result = 0

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False

        elif e.type == KEYDOWN:
            if finished and e.key == K_r:
                finished = False
                player.reset()
                enemy_counter = 0
                killed_score = 0
                bullets.empty()

                for enemy in enemies:
                    enemy.reset()

                for asteroid in asteroids:
                    asteroid.reset()

            elif not finished and e.key == K_SPACE:
                player.fire()
            
        elif e.type == MOUSEBUTTONDOWN:
            if not finished and e.button == 1:
                player.fire()

    if not finished:
        player.update()
        bullets.update()
        enemies.update()
        asteroids.update()

        collides = sprite.groupcollide(enemies, bullets, False, True)
        for monster in collides:
            killed_score += 1
            monster.reset()

        sprite.groupcollide(asteroids, bullets, False, True)

        if (sprite.spritecollide(player, enemies, False) 
            or enemy_counter >= 5 
            or sprite.spritecollide(player, asteroids, False)
        ):
            finished = True
            result = 'lose'

        if killed_score >= 40:
            finished = True
            result = 'win'

    m_w.blit(background, (0, 0))

    bullets.draw(m_w)
    player.draw()
    enemies.draw(m_w)
    asteroids.draw(m_w)
    
    draw_counter(f'Убито: {killed_score}', 5, 5)
    draw_counter(f'Пропущено: {enemy_counter}', 5, 40)
    draw_counter(f'{player.cur_ammo} / {player.ammo}', 600, 460)
     
    if finished:
        if result == "win":
            draw_result("You win", (0, 255, 10))
        else:
            draw_result("You lose", (250, 10, 0))

    display.update()

    dt = clock.tick(120) / 1000
