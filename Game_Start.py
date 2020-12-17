import pygame
import random
import math
import time

from constants import *
from config import FPS

# проверка связи
pygame.init()
screen = pygame.display.set_mode(SCREENSIZE)  # , pygame.FULLSCREEN
clock = pygame.time.Clock()
pygame.display.set_caption('Super Game')
manna_upper_coordinates = Tree_constants.manna_coords
health_upper_coordinates = Tree_constants.health_coords
manna_upper_real_coordinates = Tree_constants.manna_real_coords
health_upper_real_coordinates = Tree_constants.health_real_coords


def load_image(name):
    return pygame.image.load('data/' + name)


# def music(name, volume=1):
#     if name[-3:] == 'mp3':
#         pygame.mixer.music.load('data/' + name)
#         pygame.mixer.music.play()
#         pygame.mixer.music.set_volume(volume)
#     elif name[-3:] == 'ogg' or name[-3:] == 'wav':
#         return pygame.mixer.Sound('data/' + name)
#     else:
#         print('error sound')


def static_labels():
    font = pygame.font.Font(None, 25)
    screen.blit(font.render(LABELS[0], 1, (255, 255, 255), (0, 0, 0)), (450, 100))
    pygame.draw.rect(screen, (123, 0, 123), (435, 90, 150, 30), 1)
    screen.blit(font.render(LABELS[1], 1, (255, 255, 255), (0, 0, 0)), (100 + xl, 150 + yl))
    pygame.draw.rect(screen, (123, 0, 123), (90 + xl, 140 + yl, 130, 30), 1)
    screen.blit(font.render(LABELS[2], 1, (255, 255, 255), (0, 0, 0)), (100 + xl, 350 + yl))
    pygame.draw.rect(screen, (123, 0, 123), (90 + xl, 340 + yl, 130, 30), 1)


screen_rect = (0, 0, WIDTH, HEIGHT)


class FireBall(pygame.sprite.Sprite):
    """Фаерболлы. Что умеют:
    при попадании в героя наносят ему дамаг и исчезают, при этом не убивают магов"""
    mage_fireball_image = pygame.transform.scale(load_image("fireball_mage.png"), (40, 40))
    hero_fireball_image = pygame.transform.scale(load_image("fireball_new.png"), (40, 40))

    def __init__(self, x, y, phi, *groups):
        super().__init__(*groups)
        if self in mage_fireballs:
            self.image = self.mage_fireball_image
        else:
            self.image = self.hero_fireball_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if self in mage_fireballs:
            self.v = MageFireBall_constants.v  # скорость фаерболла
        else:
            self.v = FireBall_constants.v
        self.phi = phi
        self.damage = MageFireBall_constants.damage  # его  урон

    def update(self, *args):
        if pygame.sprite.collide_mask(self, walls):
            self.kill()
        if self in mage_fireballs and self.rect.colliderect(hero):
            self.kill()
        else:
            self.rect.x += self.v * math.cos(self.phi)
            self.rect.y += self.v * math.sin(self.phi)
        if self.rect.colliderect(hero) and self in mage_fireballs:
            hero.change_health(-self.damage)


class Enemy(pygame.sprite.Sprite):
    """Класс врагов ближнего боя. Что умеют:
    1.получать дамаг от попадания фаерболла,
    2.бегать за героем, если он находится в радиусе видимости
    3.не объединяются в одного power-ranger-скелета"""

    def __init__(self, sheet, columns, rows, *groups):
        super().__init__(*groups)
        # скорость врага
        self.v = 0
        # коэффициент замедление от зелья
        self.alpha = 1

        # списки для харнения кадров анимаций
        self.frames_right = []
        self.frames_left = []
        self.frames_up = []
        self.frames_down = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames_right[self.cur_frame]

        self.rect = self.image.get_rect()
        w = self.rect.w
        h = self.rect.h
        self.mask = pygame.mask.from_surface(self.image)

        while True:
            self.rect.x = random.randint(walls.rect.x + w, walls.rect.x + walls.mask.get_size()[0] - w)
            self.rect.y = random.randint(walls.rect.y + h, walls.rect.y + walls.mask.get_size()[1] - h)
            if not pygame.sprite.collide_mask(self, walls):
                break

        self.vector = 1
        self.frame_count = 0
        self.health = 10
        self.damage = 0.2
        # проверка на застой
        self.stand = True

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)

        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                if j == 0:
                    self.frames_up.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))
                elif j == 1:
                    self.frames_right.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))
                elif j == 2:
                    self.frames_down.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))
                elif j == 3:
                    self.frames_left.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))

    def change_health(self, value):
        self.health += value
        if self.health <= 0:
            self.kill()
            hero.gold += 5
            hero.kills += 1

    def update(self, *args):
        # при попадании фаерболаа враг умирает
        for elem in fireballs:
            if self.rect.colliderect(elem):
                elem.kill()
                self.change_health(int(-5 * hero.attack_coef))

        # наносим урон герою
        if self.rect.colliderect(hero):
            hero.change_health(-self.damage)
            if hero.is_kicking:
                self.change_health(-0.3 * hero.attack_coef)
        # движение врагов
        lx = self.rect.x - hero.rect.x
        ly = self.rect.y - hero.rect.y
        l = lx ** 2 + ly ** 2
        if l < 400 ** 2 and not self.rect.colliderect(hero):
            self.v = int(4 * self.alpha)
            # задаем 4 возможных направления передвижений зомби
            x1 = {"vector": 1,
                  "dx": min(self.v, abs(lx)),
                  "dy": 0}
            x2 = {"vector": 2,
                  "dx": -min(self.v, abs(lx)),
                  "dy": 0}
            y1 = {"vector": 3,
                  "dx": 0,
                  "dy": min(self.v, abs(ly))}
            y2 = {"vector": 4,
                  "dx": 0,
                  "dy": -min(self.v, abs(ly))}
            ways = [0, 0]

            if lx > 0:
                ways[0] = x2
            elif lx != 0:
                ways[0] = x1
            if ly > 0:
                ways[1] = y2
            elif ly != 0:
                ways[1] = y1
            if abs(ly) > abs(lx):
                ways.reverse()

            for d in ways:
                if d != 0:
                    # выбираем путь наименьшей длины
                    self.rect.x += d["dx"]
                    self.rect.y += d["dy"]
                    zomb_collision = False
                    for enemy in enemy_group:
                        if enemy != self and pygame.sprite.collide_mask(self, enemy):
                            zomb_collision = True
                            break
                    if pygame.sprite.collide_mask(self, walls) or zomb_collision:  # проверяем его на пригодность
                        # если зомби зомби пересек спрайт стены, то отменяем действие
                        self.rect.x -= d["dx"]
                        self.rect.y -= d["dy"]
                    else:
                        # выходим, когда такое перемещение найдено
                        self.vector = d["vector"]
                        self.stand = False
                        break

        # обновляем картинки зомби
        if self.frame_count % 5 == 0 and not self.stand:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames_right)
            if self.vector == 1:
                self.image = self.frames_right[self.cur_frame]
            elif self.vector == 2:
                self.image = self.frames_left[self.cur_frame]
            elif self.vector == 3:
                self.image = self.frames_down[self.cur_frame]
            elif self.vector == 4:
                self.image = self.frames_up[self.cur_frame]
        self.frame_count += 1
        # отрисовываем полоску здоровья
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y, 5 * int(self.health), 5))

        self.stand = True


class Mage(pygame.sprite.Sprite):
    """Класс магов. Что умеют:
        1.получать дамаг от попадания фаерболла,
        2.бегать за героем, даржась на дистанции от него; стрелять в героя фаерболлами
        3.не объединяются в одного power-ranger-мага"""

    def __init__(self, sheet, columns, rows, *groups):
        super().__init__(*groups)
        # скорость врага
        self.v = 0
        # коэффициент замедления
        self.alpha = 1
        self.frames_right = []
        self.frames_left = []
        self.frames_up = []
        self.frames_down = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames_right[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        w = self.rect.w
        h = self.rect.h

        while True:
            self.rect.x = random.randint(walls.rect.x + w, walls.rect.x + walls.mask.get_size()[0] - w)
            self.rect.y = random.randint(walls.rect.y + h, walls.rect.y + walls.mask.get_size()[1] - h)
            if not pygame.sprite.collide_mask(self, walls):
                break

        self.vector = 1
        self.frame_count = 0
        self.health = 10
        # проверка на застой
        self.stand = True

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)

        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                if j == 0:
                    self.frames_up.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))
                elif j == 1:
                    self.frames_right.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))
                elif j == 2:
                    self.frames_down.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))
                elif j == 3:
                    self.frames_left.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))

    def change_health(self, value):
        self.health += value
        if self.health <= 0:
            self.kill()
            hero.gold += 10
            hero.kills += 1
            if len(shop) < 8:
                shop.append(random.choice(possible_spells))

    def update(self, *args):
        for elem in fireballs:
            if self.rect.colliderect(elem):
                elem.kill()
                self.change_health(int(-5 * hero.attack_coef))
        if self.rect.colliderect(hero):
            if hero.is_kicking:
                self.change_health(-0.3 * hero.attack_coef)

        # движение врагов
        lx = self.rect.x - hero.rect.x
        ly = self.rect.y - hero.rect.y
        l = lx ** 2 + ly ** 2
        far = 200 ** 2 < l < 400 ** 2
        near = l < 180 ** 2
        if far or near:
            self.v = int(4 * self.alpha)
            x1 = {"vector": 1,
                  "dx": self.v,
                  "dy": 0}
            x2 = {"vector": 2,
                  "dx": -self.v,
                  "dy": 0}
            y1 = {"vector": 3,
                  "dx": 0,
                  "dy": self.v}
            y2 = {"vector": 4,
                  "dx": 0,
                  "dy": -self.v}
            ways = [0, 0]

            if lx > 0 and far or lx < 0 and near:
                ways[0] = x2
            else:
                ways[0] = x1
            if ly > 0 and far or ly < 0 and near:
                ways[1] = y2
            else:
                ways[1] = y1
            if (abs(ly) > abs(lx)) == far:
                ways.reverse()

            for d in ways:
                self.rect.x += d["dx"]
                self.rect.y += d["dy"]
                zomb_collision = False
                for mag in mages_group:
                    if mag != self and pygame.sprite.collide_mask(self, mag):
                        zomb_collision = True
                        break
                if pygame.sprite.collide_mask(self, walls) or zomb_collision:  # проверяем его на пригодность
                    # если зомби зомби пересек спрайт стены, то отменяем действие
                    self.rect.x -= d["dx"]
                    self.rect.y -= d["dy"]
                else:
                    # выходим, когда такое перемещение найдено
                    self.vector = d["vector"]
                    self.stand = False
                    break

        # обновляем картинки зомби
        if self.frame_count % 5 == 0 and not self.stand:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames_right)
            if self.vector == 1:
                self.image = self.frames_right[self.cur_frame]
            elif self.vector == 2:
                self.image = self.frames_left[self.cur_frame]
            elif self.vector == 3:
                self.image = self.frames_down[self.cur_frame]
            elif self.vector == 4:
                self.image = self.frames_up[self.cur_frame]
        self.frame_count += 1
        # отрисовываем полоску здоровья
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y, 5 * int(self.health), 5))

        self.stand = True

    def fire(self):
        # этот кусок кода нужен для определения угла выстрела (магом в сторону героя)
        x, y = hero.rect.x, hero.rect.y
        if y - self.rect.y > 0 and x - self.rect.x > 0:
            tan = (y - self.rect.y) / (x - self.rect.x)
            phi = math.atan(tan)
        if y - self.rect.y > 0 > x - self.rect.x:
            tan = (y - self.rect.y) / (x - self.rect.x)
            phi = math.atan(tan) + math.pi
        if y - self.rect.y < 0 and x - self.rect.x < 0:
            tan = (y - self.rect.y) / (x - self.rect.x)
            phi = math.atan(tan) + math.pi
        if y - self.rect.y < 0 < x - self.rect.x:
            tan = (y - self.rect.y) / (x - self.rect.x)
            phi = math.atan(tan)
        if y == self.rect.y:
            if x - self.rect.x > 0:
                phi = 0
            elif x - self.rect.x < 0:
                phi = math.pi
        if x == self.rect.x:
            if y - self.rect.y > 0:
                phi = math.pi / 2
            elif y - self.rect.y < 0:
                phi = - math.pi / 2
        FireBall(self.rect.x + 35, self.rect.y + 10, phi, all_sprites, mage_fireballs)


class MainHero(pygame.sprite.Sprite):
    """Класс главного героя. Что умеет:
    1. бегает
    2. стреляет фаерболлами
    3. дерется в ближнем бою
    """
    image = load_image("hero.png")

    def __init__(self, frames_right, frames_left, frames_stand_left, frames_stand_right, frames_left_shouting,
                 frames_right_shouting, frames_left_kicking, frames_right_kicking, frames_stand_left_shouting,
                 frames_stand_right_shouting, frames_stand_left_kick, frames_stand_right_kick, start_pos, *groups):
        super().__init__(*groups)
        self.frames_right = frames_right  # кадры движения вправо
        self.frames_left = frames_left  # кадры движения влево
        self.frames_stand_left = frames_stand_left  # кадры застоя влево
        self.frames_stand_right_shouting = frames_stand_right_shouting  # кадры стрельбы вправо стоя
        self.frames_stand_left_shouting = frames_stand_left_shouting  # кадры стрельбы влево стоя
        self.frames_stand_right_kick = frames_stand_right_kick  # кадры удара вправо стоя
        self.frames_stand_left_kick = frames_stand_left_kick  # кадры удара вправо стоя
        self.frames_stand_right = frames_stand_right  # кадры застоя вправо
        self.frames_right_shouting = frames_right_shouting  # кадры выстрела вправо
        self.frames_left_shouting = frames_left_shouting  # кадры выстрела влево
        self.frames_right_kicking = frames_right_kicking  # кадры удара вправо
        self.frames_left_kicking = frames_left_kicking  # кадры удара влево
        self.cur_frame = 0
        self.frame_count = 0
        self.gold = MainHero_constants.gold  # золото, за которое покупаются зелья
        self.kills = 0  # киллы
        self.attack_coef = 1  # множитель при нанесении урона
        self.image = self.frames_right[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = start_pos[0]
        self.rect.y = start_pos[1]
        self.realx = self.realy = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.vector = 1  # направление движения
        self.v = MainHero_constants.v  # скорость
        self.vector_left_right = 1
        self.health = MainHero_constants.health  # хп
        self.manna = MainHero_constants.manna  # манна
        self.stand = True  # проверка на остановку
        self.is_shouting = False  # проверка на стрельбу
        self.is_kicking = False  # проверка на рукопашку

    def update(self, *args):

        buttons = pygame.key.get_pressed()
        pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 130, 20, 100, 10))  # белый фон
        pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 130, 40, 100, 10))  # под полосками
        pygame.draw.rect(screen, (255, 0, 0), (WIDTH - 130, 20, int(hero.health), 10))  # отрисовка полоски ХП
        pygame.draw.rect(screen, (0, 0, 255), (WIDTH - 130, 40, int(hero.manna), 10))  # отрисовка полоски манны

        screen.blit(pygame.font.Font(None, 30).render('Kills: ' + str(self.kills), 1, (255, 0, 0)),
                    (WIDTH - 240, 20))  # отрисовка количества киллов
        screen.blit(pygame.font.Font(None, 30).render('Gold: ' + str(self.gold), 1, (255, 211, 25)),
                    (WIDTH - 240, 40))  # отрисовка количества золота
        if pygame.mouse.get_pressed()[0] and (self.manna >= 10) and (
                pygame.mouse.get_pos()[0] > 100):  # проверка на стрельбу
            self.is_shouting = True
        else:
            self.is_shouting = False
        if buttons[pygame.K_e] and (self.manna >= 5):  # проверка на удар
            self.is_kicking = True
        else:
            self.is_kicking = False
        if buttons[pygame.K_w]:  # движение вперед
            self.vector = 3
            self.rect.y -= self.v
            if pygame.sprite.collide_mask(self, walls):
                self.rect.y += self.v
            else:
                self.stand = False

        if buttons[pygame.K_s]:  # движение назад
            self.vector = 4
            self.rect.y += self.v
            if pygame.sprite.collide_mask(self, walls):
                self.rect.y -= self.v
            else:
                self.stand = False
        if buttons[pygame.K_d]:  # движение вправо
            self.vector = 1
            self.vector_left_right = 1
            self.rect.x += self.v
            if pygame.sprite.collide_mask(self, walls):
                self.rect.x -= self.v
            else:
                self.stand = False
        if buttons[pygame.K_a]:  # движение влево
            self.vector = 2
            self.vector_left_right = 2
            self.rect.x -= self.v
            if pygame.sprite.collide_mask(self, walls):
                self.rect.x += self.v
            else:
                self.stand = False

        if self.frame_count % 5 == 0:
            hero.change_manna(0.2)
            for i in manna_upper_real_coordinates:  # вблизи ли герой дерева подъема манны
                if (hero.realx - (i[0])) ** 2 + (hero.realy - (i[1])) ** 2 < 10000:
                    hero.change_manna(0.5)
            for i in health_upper_real_coordinates:  # вблизи ли герой дерева подъема здоровья
                if (hero.realx - (i[0])) ** 2 + (hero.realy - (i[1])) ** 2 < 10000:
                    hero.change_health(0.5)

            # анимации
            if not self.is_shouting and not self.is_kicking:  # просто идет или стоит
                if not self.stand:
                    if self.vector_left_right == 1:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_right)
                        self.image = self.frames_right[self.cur_frame]
                    if self.vector_left_right == 2:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_left)
                        self.image = self.frames_left[self.cur_frame]
                else:
                    if self.vector_left_right == 1:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_right)
                        self.image = self.frames_stand_right[self.cur_frame]
                    if self.vector_left_right == 2:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_left)
                        self.image = self.frames_stand_left[self.cur_frame]
            elif self.is_shouting and not self.is_kicking:  # стреляет

                if not self.stand:
                    if self.vector_left_right == 1:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_right_shouting)
                        self.image = self.frames_right_shouting[self.cur_frame]
                    if self.vector_left_right == 2:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_left_shouting)
                        self.image = self.frames_left_shouting[self.cur_frame]
                elif self.stand:
                    if self.vector_left_right == 1:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_right)
                        self.image = self.frames_stand_right_shouting[self.cur_frame]
                    if self.vector_left_right == 2:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_left)
                        self.image = self.frames_stand_left_shouting[self.cur_frame]
            else:  # ближний бой
                hero.change_manna(-3)
                if not self.stand:
                    if self.vector_left_right == 1:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_right_kicking)
                        self.image = self.frames_right_kicking[self.cur_frame]
                    if self.vector_left_right == 2:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_left_kicking)
                        self.image = self.frames_left_kicking[self.cur_frame]
                else:
                    if self.vector_left_right == 1:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_right)
                        self.image = self.frames_stand_right_kick[self.cur_frame]
                    if self.vector_left_right == 2:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_left)
                        self.image = self.frames_stand_left_kick[self.cur_frame]

        if not (buttons[pygame.K_UP] or buttons[pygame.K_DOWN] or buttons[pygame.K_RIGHT] or buttons[
            pygame.K_LEFT]):  # если ничего не нажато, то герой стоит
            self.stand = True
        self.frame_count += 1

    def hero_fire(self):
        # этот кусок кода нужен для определения угла выстрела (в сторону мышки при нажатии пробела)
        x, y = pygame.mouse.get_pos()
        if y - hero.rect.y > 0 and x - hero.rect.x > 0:
            tan = (y - hero.rect.y) / (x - hero.rect.x)
            phi = math.atan(tan)
        if y - hero.rect.y > 0 > x - hero.rect.x:
            tan = (y - hero.rect.y) / (x - hero.rect.x)
            phi = math.atan(tan) + math.pi
        if y - hero.rect.y < 0 and x - hero.rect.x < 0:
            tan = (y - hero.rect.y) / (x - hero.rect.x)
            phi = math.atan(tan) + math.pi
        if y - hero.rect.y < 0 < x - hero.rect.x:
            tan = (y - hero.rect.y) / (x - hero.rect.x)
            phi = math.atan(tan)
        if y == hero.rect.y:
            if x - hero.rect.x > 0:
                phi = 0
            elif x - hero.rect.x < 0:
                phi = math.pi
        if x == hero.rect.x:
            if y - hero.rect.y > 0:
                phi = math.pi / 2
            elif y - hero.rect.y < 0:
                phi = - math.pi / 2

        FireBall(self.rect.x + 10, self.rect.y - 5, phi, all_sprites, fireballs) # пускаем файербол под нужным углом
        hero.change_manna(-10)

    def change_health(self, value):  # изменение хп
        if (self.health + value <= 100) and (self.health + value >= 0):
            self.health += value
        elif self.health + value <= 0:
            self.health = 0
        else:
            self.health = 100

    def change_manna(self, value):  # изменение манны
        if (self.manna + value <= 100) and (self.manna + value >= 0):
            self.manna += value
        elif self.manna + value <= 0:
            self.manna = 0
        else:
            self.manna = 100


class Spikes(pygame.sprite.Sprite):
    """Реализация ловушек с шипамии. На изображениях traps_active.png и traps_passive.png
    прорисованы состояния ловушек, которые меняются со временем. Если ловушка активна,
    то она наносит урон юнитам, пересекающим ее спрайт(кроме магов, они парят над шипами. """
    image_active = load_image('traps_active.png')
    image_passive = load_image('traps_passive.png')

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = self.image_passive
        self.mask = pygame.mask.from_surface(self.image_active)
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = -5
        self.frames_count = 1
        self.active = False
        self.hero_damage = 5
        self.zombie_damage = 1

    def switch_phase(self):  # меняем фазу ловушки
        self.active = not self.active
        if self.image == self.image_passive:
            self.image = self.image_active
        else:
            self.image = self.image_passive

    def update(self, *args):
        if self.active:
            self.do_damage()
        if self.active and self.frames_count % 60 == 0:
            self.switch_phase()
            self.frames_count = 1
        if not self.active and self.frames_count % 180 == 0:
            self.switch_phase()
            self.frames_count = 1
        self.frames_count += 1

    def do_damage(self):
        # for zombie in enemy_group
        if self.frames_count % 20 == 0:
            if pygame.sprite.collide_mask(self, hero):
                hero.change_health(-self.hero_damage)
            # a = pygame.sprite.groupcollide(traps, enemy_group, dokillb=False, dokilla=False)
            # a[self].change_health(-self.zombie_damage)
            for zombie in enemy_group:
                if pygame.sprite.collide_mask(self, zombie):
                    zombie.change_health(-self.zombie_damage)


class Walls(pygame.sprite.Sprite):
    """"Тупо стены"""
    image = load_image('стены_1.png')
    image_mask = load_image('стены_1(ok).png')  ###???

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.mask = pygame.mask.from_surface(self.image_mask)

    def update(self, *args):
        # камон, это же стены
        pass


class Tree(pygame.sprite.Sprite):
    '''Класс рисуемых деревьев, могут стоять'''

    def __init__(self, tree_image, coords, *groups):
        super().__init__(*groups)
        self.image = tree_image
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

    def update(self, *args):
        # камон, это же стены(деревья)
        pass


class Floor(pygame.sprite.Sprite):
    """"Тупо стены"""
    image = load_image('фон_1.png')

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect.x = 23
        self.rect.y = 45
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):
        # камон, это же пол
        pass


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        if obj is hero:  # пересчитываем координаты героя в базисе карты/мира
            hero.realx -= self.dx
            hero.realy -= self.dy

    # позиционировать камеру на объекте target
    def update(self, *args):
        self.dx = -(args[0].rect.x + args[0].rect.w // 2 - WIDTH // 2)
        self.dy = -(args[0].rect.y + args[0].rect.h // 2 - HEIGHT // 2)


camera = Camera()


# fps = 60
xl, yl = 0, 50

gamerun = True
gameover = False
menu = True
lvl = False
# music('TownTheme.mp3')
fon = load_image('фон_1.png')
walls = load_image('стены_1(new).png')
# начальное положение фоновых объектов
x_fon, y_fon = 23, 45
x_walls, y_walls = 0, 0
is_hero = False

is_shield_timer = True  # включен ли щит
fixed_hero_health = 0  # уровень здоровья при включеннном щите


class Timer:
    '''Класс таймер. Визуализирует оставшееся время действия зелья.
    time - оставшееся время
    color - тип таймера, и его цвет
    def update - обновляем таймер и проверяем нужно ли продолжать применять зелье'''

    def __init__(self, time, color):
        self.time = time
        self.color = color

    def update(self):
        global is_shield_timer, fixed_hero_health
        if self.time < time.time():
            # если время вышло - восстанавливаем изменения
            if self.color == Spell_constants.BLUE:
                for i in enemy_group:
                    i.alpha = 1
                for i in mages_group:
                    i.alpha = 1
            elif self.color == Spell_constants.WHITE:
                is_shield_timer = True
            elif self.color == Spell_constants.GREEN:
                hero.v = Spell_constants.normal_motion_herov
            elif self.color == Spell_constants.RED:
                hero.attack_coef = 1
            active_spell.remove(self)
            del self
        else:
            # если время еще не вышло - применяем изменения
            if self.color == Spell_constants.BLUE:
                for i in enemy_group:
                    i.alpha = Spell_constants.slow_motion_alpha  # замедляем врагов
                for i in mages_group:
                    i.alpha = Spell_constants.slow_motion_alpha  # замедляем магов
            elif self.color == Spell_constants.GREEN:
                hero.v = Spell_constants.fast_motion_herov  # ускоряем героя
            elif self.color == Spell_constants.WHITE:
                if is_shield_timer:
                    fixed_hero_health = hero.health  # узнаем уровень здоровья врага и фиксируем
                    is_shield_timer = False
                if not is_shield_timer:
                    hero.health = fixed_hero_health
            elif self.color == Spell_constants.RED:
                hero.attack_coef = Spell_constants.attack_coef  # увеличиваем урон


class Spell:
    '''Класс зелье. Хранит информацию в себе о зелье. Объекты класса содержатся в магазине.'''

    def __init__(self, image, price, type):
        self.image = image
        self.price = price
        self.type = type


active_spell = []  # примененные зелья
possible_spells = [Spell(load_image('spell.png'), 50, "gold"), Spell(load_image('fspell.png'), 20, "freeze"),
                   Spell(load_image('shield.png'), 20, "shield"), Spell(load_image('hspell.png'), 40, "health"),
                   Spell(load_image('sspell.png'), 20, "speed"),
                   Spell(load_image('rspell.png'), 30, "rage")]  # весь ассортимент зелий
shop = [Spell(load_image('spell.png'), 50, "gold"), Spell(load_image('fspell.png'), 20, "freeze"),
        Spell(load_image('shield.png'), 20, "shield"), Spell(load_image('hspell.png'), 40, "health"),
        Spell(load_image('sspell.png'), 20, "speed"), Spell(load_image('rspell.png'), 30, "rage")]  # зелья в магазине

hero_images = [[load_image("bomzh_vprapo_okonchat0.png"), load_image("bomzh_vprapo_okonchat1.png"),
                load_image("bomzh_vprapo_okonchat2.png"), load_image("bomzh_vprapo_okonchat3.png"),
                load_image("bomzh_vprapo_okonchat4.png"), load_image("bomzh_vprapo_okonchat5.png"),
                load_image("bomzh_vprapo_okonchat6.png"),
                load_image("bomzh_vprapo_okonchat7.png")],
               [load_image("bomzh_vlevo_okonchat0.png"), load_image("bomzh_vlevo_okonchat1.png"),
                load_image("bomzh_vlevo_okonchat2.png"), load_image("bomzh_vlevo_okonchat3.png"),
                load_image("bomzh_vlevo_okonchat4.png"), load_image("bomzh_vlevo_okonchat5.png"),
                load_image("bomzh_vlevo_okonchat6.png"), load_image("bomzh_vlevo_okonchat7.png")],
               [load_image("stait_vlevo00.png"), load_image("stait_vlevo01.png"),
                load_image("stait_vlevo02.png"), load_image("stait_vlevo03.png"),
                load_image("stait_vlevo04.png"), load_image("stait_vlevo14.png"),
                load_image("stait_vlevo15.png"), load_image("stait_vlevo16.png"),
                load_image("stait_vlevo17.png")],
               [load_image("stait_vpravo00.png"), load_image("stait_vpravo01.png"),
                load_image("stait_vpravo02.png"), load_image("stait_vpravo03.png"),
                load_image("stait_vpravo04.png"), load_image("stait_vpravo14.png"),
                load_image("stait_vpravo15.png"), load_image("stait_vpravo16.png"),
                load_image("stait_vpravo17.png")],
               [load_image("bomzh_vlevo_shout0.png"), load_image("bomzh_vlevo_shout1.png"),
                load_image("bomzh_vlevo_shout2.png"), load_image("bomzh_vlevo_shout3.png"),
                load_image("bomzh_vlevo_shout4.png"), load_image("bomzh_vlevo_shout5.png"),
                load_image("bomzh_vlevo_shout6.png"), load_image("bomzh_vlevo_shout7.png")],
               [load_image("bomzh_vprapo_shout0.png"), load_image("bomzh_vprapo_shout1.png"),
                load_image("bomzh_vprapo_shout2.png"), load_image("bomzh_vprapo_shout3.png"),
                load_image("bomzh_vprapo_shout4.png"), load_image("bomzh_vprapo_shout5.png"),
                load_image("bomzh_vprapo_shout6.png"),
                load_image("bomzh_vprapo_shout7.png")],
               [load_image("bomzh_vlevo_kick0.png"), load_image("bomzh_vlevo_kick1.png"),
                load_image("bomzh_vlevo_kick2.png"), load_image("bomzh_vlevo_kick3.png"),
                load_image("bomzh_vlevo_kick4.png"), load_image("bomzh_vlevo_kick5.png"),
                load_image("bomzh_vlevo_kick6.png"), load_image("bomzh_vlevo_kick7.png")],
               [load_image("bomzh_vprapo_kick0.png"), load_image("bomzh_vprapo_kick1.png"),
                load_image("bomzh_vprapo_kick2.png"), load_image("bomzh_vprapo_kick3.png"),
                load_image("bomzh_vprapo_kick4.png"), load_image("bomzh_vprapo_kick5.png"),
                load_image("bomzh_vprapo_kick6.png"),
                load_image("bomzh_vprapo_kick7.png")],
               [load_image("stait_vlevo_shout0.png"), load_image("stait_vlevo_shout1.png"),
                load_image("stait_vlevo_shout2.png"), load_image("stait_vlevo_shout3.png"),
                load_image("stait_vlevo_shout4.png"), load_image("stait_vlevo_shout5.png"),
                load_image("stait_vlevo_shout6.png"), load_image("stait_vlevo_shout7.png"),
                load_image("stait_vlevo_shout8.png")],
               [load_image("stait_vpravo_shout0.png"), load_image("stait_vpravo_shout1.png"),
                load_image("stait_vpravo_shout2.png"), load_image("stait_vpravo_shout3.png"),
                load_image("stait_vpravo_shout4.png"), load_image("stait_vpravo_shout5.png"),
                load_image("stait_vpravo_shout6.png"), load_image("stait_vpravo_shout7.png"),
                load_image("stait_vpravo_shout8.png")],
               [load_image("stait_vlevo_kick0.png"), load_image("stait_vlevo_kick1.png"),
                load_image("stait_vlevo_kick2.png"), load_image("stait_vlevo_kick3.png"),
                load_image("stait_vlevo_kick4.png"), load_image("stait_vlevo_kick5.png"),
                load_image("stait_vlevo_kick6.png"), load_image("stait_vlevo_kick7.png"),
                load_image("stait_vlevo_kick8.png")],
               [load_image("stait_vpravo_kick0.png"), load_image("stait_vpravo_kick1.png"),
                load_image("stait_vpravo_kick2.png"), load_image("stait_vpravo_kick3.png"),
                load_image("stait_vpravo_kick4.png"), load_image("stait_vpravo_kick5.png"),
                load_image("stait_vpravo_kick6.png"), load_image("stait_vpravo_kick7.png"),
                load_image("stait_vpravo_kick8.png")]]

while gamerun:
    font = pygame.font.Font(None, 20)
    if menu:
        screen.fill((10, 10, 10))
        screen.blit(pygame.transform.scale(load_image('worldmap.png'), (WIDTH, HEIGHT)), (0, 0))
        static_labels()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gamerun = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if event.button == 1 and (90 < (x - xl) < 220) and (140 < (y - yl) < 170):
                    # dialog = True
                    lvl = True
                    menu = False
    elif lvl:
        if not is_hero:
            all_sprites = pygame.sprite.Group()
            enemy_group = pygame.sprite.Group()
            fireballs = pygame.sprite.Group()
            traps = pygame.sprite.Group()
            mages_group = pygame.sprite.Group()
            mage_fireballs = pygame.sprite.Group()
            objects = pygame.sprite.Group()

            mage_counter = 0  # счётчик, чтобы стреляли маги
            lvl_num = 1  # номер уровня
            # создаем необходимые спрайты
            is_hero = True
            floor = Floor(all_sprites)
            walls = Walls(all_sprites)
            spikes = Spikes(all_sprites, traps)
            hero = MainHero(*hero_images,
                            (800, 300),
                            all_sprites)
            for i in manna_upper_coordinates:  # рисуем деревья манны
                Tree(pygame.transform.scale(load_image("manna_upper.png"), (234, 275)), i, all_sprites, objects)
            for i in health_upper_coordinates:  # рисуем деревья здоровья
                Tree(pygame.transform.scale(load_image("health_upper.png"), (177, 273)), i, all_sprites, objects)

        if not (mages_group or enemy_group):  # переход на следующий уровень
            for i in range(lvl_num):
                Enemy(load_image("bloody_zombie-NESW.png"), 3, 4, all_sprites, enemy_group)
                Mage(pygame.transform.scale(load_image("mage-NESW.png"), (150, 200)), 3, 4, all_sprites, mages_group)
                lvl_num += 1
        mage_counter += 1
        for mage in mages_group:
            if mage_counter % 100 == 0 and (mage.rect.x - hero.rect.x) ** 2 + (
                    mage.rect.y - hero.rect.y) ** 2 <= 400 ** 2:
                mage.fire()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                lvl = False
                gamerun = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (event.button == 1) and (hero.manna >= 10) and (pygame.mouse.get_pos()[0] > 100):
                    hero.hero_fire()
                elif (event.button == 1) and (pygame.mouse.get_pos()[0] < 100):  # если кликаем на магазин
                    y = pygame.mouse.get_pos()[1]
                    n = (y - 10) // 70
                    if shop[n].price <= hero.gold:  # если покупка возможна
                        hero.gold -= shop[n].price
                        type = shop[n].type
                        if type == "gold":
                            hero.gold *= 2
                        elif type == 'health':
                            hero.health = 100
                        else:
                            if type == "freeze":
                                color = Spell_constants.BLUE
                            elif type == "shield":
                                color = Spell_constants.WHITE
                            elif type == "speed":
                                color = Spell_constants.GREEN
                            else:
                                color = Spell_constants.RED
                            flag = False
                            for element in active_spell:  # если такое зелье еще активно, то просто добавляем к времени действия 30 сек
                                if element.color == color:
                                    element.time += 30
                                    flag = True
                            if not flag:  # иначе, добавляем новый таймер для этого зелья
                                active_spell.append(Timer(time.time() + 30, color))
                        del shop[n]
                    if 0 < n < len(shop):
                        if shop[n].price <= hero.gold:  # если покупка возможна
                            hero.gold -= shop[n].price
                            type = shop[n].type
                            if type == "gold":
                                hero.gold *= 2
                            elif type == 'health':
                                hero.health = 100
                            else:
                                if type == "freeze":
                                    color = Spell_constants.BLUE
                                elif type == "shield":
                                    color = Spell_constants.WHITE
                                elif type == "speed":
                                    color = Spell_constants.GREEN
                                else:
                                    color = Spell_constants.RED
                                flag = False
                                for element in active_spell:  # если такое зелье еще активно, то просто добавляем к времени действия 30 сек
                                    if element.color == color:
                                        element.time += 30
                                        flag = True
                                if not flag:  # иначе, добавляем новый таймер для этого зелья
                                    active_spell.append(Timer(time.time() + 30, color))
                            del shop[n]

        screen.fill((0, 0, 0))
        if hero.health == 0:
            lvl = False
            gameover = True
            is_hero = False
        camera.update(hero)
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.draw(screen)
        all_sprites.update(event)
        pygame.draw.rect(screen, (90, 39, 41), (0, 0, 100, 600))
        for i in range(len(shop)):  # для каждого зелья в магазине рисуем его
            screen.blit(shop[i].image, (20, 10 + i * 70))
            screen.blit(pygame.font.Font(None, 20).render(str(shop[i].price), 1, (255, 255, 25)),
                        (60, 70 + i * 70))
        for i in active_spell:  # для каждого активного зелья рисуем оставшееся время
            screen.blit(pygame.font.Font(None, 20).render(str(int(i.time - time.time())), 1, i.color),
                        (500 - active_spell.index(i) * 40, 20))
            i.update()

    elif gameover:
        screen.fill((0, 0, 0))
        screen.blit(pygame.font.Font(None, 40).render('Game over', 1, (255, 0, 0), (0, 0, 0)), (WIDTH / 2 - 60, 100))
        screen.blit(pygame.font.Font(None, 30).render('Kills: ' + str(hero.kills), 1, (255, 0, 0)),
                    (WIDTH / 2 - 60, 150))  # отрисовка количества киллов
        screen.blit(font.render('Вернуться в меню.', 1, (255, 0, 0), (0, 0, 0)), (430, 410))
        pygame.draw.rect(screen, (123, 0, 123), (400, 400, 200, 30), 1)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if event.button == 1 and (400 < x < 600) and (400 < y < 430):
                    gameover = False
                    menu = True
    pygame.display.update()
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
