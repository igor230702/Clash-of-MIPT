import pygame
import random
from constants import LABELS, Frases, SCREENSIZE, WIDTH, HEIGHT
# проверка связи
pygame.init()
screen = pygame.display.set_mode(SCREENSIZE)  # , pygame.FULLSCREEN
clock = pygame.time.Clock()
pygame.display.set_caption('Super Game')


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
    if save:
        screen.blit(font.render(LABELS[2], 1, (255, 255, 255), (0, 0, 0)), (100 + xl, 200 + yl))
        pygame.draw.rect(screen, (123, 0, 123), (90 + xl, 190 + yl, 130, 30), 1)
    else:
        screen.blit(font.render(LABELS[2], 1, (100, 100, 100), (0, 0, 0)), (100 + xl, 200 + yl))
        pygame.draw.rect(screen, (123, 0, 123), (90 + xl, 190 + yl, 130, 30), 1)
    screen.blit(font.render(LABELS[3], 1, (255, 255, 255), (0, 0, 0)), (100 + xl, 250 + yl))
    pygame.draw.rect(screen, (123, 0, 123), (90 + xl, 240 + yl, 130, 30), 1)
    screen.blit(font.render(LABELS[4], 1, (255, 255, 255), (0, 0, 0)), (100 + xl, 300 + yl))
    pygame.draw.rect(screen, (123, 0, 123), (90 + xl, 290 + yl, 130, 30), 1)
    screen.blit(font.render(LABELS[5], 1, (255, 255, 255), (0, 0, 0)), (100 + xl, 350 + yl))
    pygame.draw.rect(screen, (123, 0, 123), (90 + xl, 340 + yl, 130, 30), 1)


def Saves(save='r'):
    global K, Flag, dialog, menu
    saves = open("saves.txt", save)
    if save == 'r':
        s = saves.readlines()
        if s == []:
            return False
        else:
            K, Flag, dialog, menu = int(s[0].split()[0]), *[bool(int(i)) for i in s[0].split()[1:]]
            return True
    if save == 'w':
        saves.write(str(K) + ' ' + str(int(Flag)) + ' ' + str(int(dialog)) + ' ' + str(int(menu)))


screen_rect = (0, 0, WIDTH, HEIGHT)


class FireBall(pygame.sprite.Sprite):
    """Фаерболлы. Что умеют:
    при попадании во врага убивают его и исчезают"""
    g = load_image("fireball.png").convert()
    image = pygame.transform.scale(g, (20, 20))

    def __init__(self, x, y, vector, *groups):
        super().__init__(*groups)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.v = 20
        self.vector = vector

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, enemy_group):
            self.kill()
        if not self.rect.colliderect(screen_rect):
            self.kill()
        else:
            if self.vector == 1:
                self.rect.x += self.v
            if self.vector == 2:
                self.rect.x -= self.v
            if self.vector == 3:
                self.rect.y -= self.v
            if self.vector == 4:
                self.rect.y += self.v


class Enemy(pygame.sprite.Sprite):
    """Класс врагов. Что умеют:
    1.умирать от попадания фаерболла,
    2.бегать за героем если он находится в радиусе видимости"""

    def __init__(self, sheet, columns, rows, *groups):
        super().__init__(*groups)
        # скорость врага
        self.v = 0
        self.frames_right = []
        self.frames_left = []
        self.frames_up = []
        self.frames_down = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames_right[self.cur_frame]
        self.rect = self.image.get_rect()
        while True:
            rand_x = random.randint(0, floor.mask.get_size()[0])
            rand_y = random.randint(0, floor.mask.get_size()[1])
            if floor.mask.get_at((rand_x, rand_y)) == 1:
                break
        self.rect.x = rand_x
        self.rect.y = rand_y

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

    def update(self, *args):
        # при попадании фаерболаа враг умирает
        for elem in fireballs:
            if self.rect.colliderect(elem):
                self.health -= 5
                elem.kill()
                if self.health <= 0:
                    self.kill()

        # наносим урон герою
        if self.rect.colliderect(hero):
            hero.change_health(-self.damage)

        # движение врагов
        if ((self.rect.x - hero.rect.x) ** 2 + (self.rect.y - hero.rect.y) ** 2) < 400**2 and not self.rect.colliderect(
                hero):
            self.v = 3
            # задаем 4 возможных направления передвижений зомби
            x1 = {"distance": (self.rect.x + self.v - hero.rect.x) ** 2 + (self.rect.y - hero.rect.y) ** 2,
                  "vector": 1,
                  "dx": self.v,
                  "dy": 0}
            x2 = {"distance": (self.rect.x - self.v - hero.rect.x) ** 2 + (self.rect.y - hero.rect.y) ** 2,
                  "vector": 2,
                  "dx": -self.v,
                  "dy": 0}
            y1 = {"distance": (self.rect.y + self.v - hero.rect.y) ** 2 + (self.rect.x - hero.rect.x) ** 2,
                  "vector": 3,
                  "dx": 0,
                  "dy": self.v}
            y2 = {"distance": (self.rect.y - self.v - hero.rect.y) ** 2 + (self.rect.x - hero.rect.x) ** 2,
                  "vector": 4,
                  "dx": 0,
                  "dy": -self.v}

            ways = [x1, x2, y1, y2]

            def optimal_way(ar):
                # выбираем путь наименьшей длины
                ok = min(ar, key=lambda i: i["distance"])
                self.rect.x += ok["dx"]
                self.rect.y += ok["dy"]
                if pygame.sprite.collide_mask(self, walls): # проверяем его на пригодность
                    # если зомби зомби пересек спрайт стены, то отменяем действие
                    self.rect.x -= ok["dx"]
                    self.rect.y -= ok["dy"]
                    # ищем другое допустимое перемещение
                    ways = [elem for elem in ar if elem != ok]
                    if ways:
                        optimal_way(ways)
                    else:
                        return

                else:
                    # выходим из рекурсии, когда такое перемещение найдено
                    self.vector = ok["vector"]
                    self.stand = False
                    return

            optimal_way(ways)


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


class MainHero(pygame.sprite.Sprite):
    """Класс главного героя. Что умеет:
    1. бегает
    2. стреляет фаерболлами
    to-do
    3. анимация ближнего боя"""
    image = load_image("hero.png")

    def __init__(self, frames_right, frames_left, frames_stand_left, frames_stand_right, frames_left_shouting,frames_right_shouting, start_pos, *groups):
        super().__init__(*groups)
        self.frames_right = frames_right
        self.frames_left = frames_left
        self.frames_stand_left = frames_stand_left
        self.frames_stand_right = frames_stand_right
        self.frames_right_shouting = frames_right_shouting
        self.frames_left_shouting = frames_left_shouting
        self.cur_frame = 0
        self.frame_count = 0
        self.image = self.frames_right[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = start_pos[0]
        self.rect.y = start_pos[1]
        self.mask = pygame.mask.from_surface(self.image)
        #self.mask = pygame.mask.from_surface(pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA))
        #self.mask = self.rect
        self.vector = 1
        # скорость гг
        self.v = 5
        self.vector_left_right = 1
        self.vector_stand = 1
        self.health = 100
        # проверка на остановку
        self.stand = True
        # чтобы перс не застрявал в верхних стенах
        self.in_wall_prison = False
        # проверка на стрельбу
        self.is_shouting = False

    def update(self, *args):
        buttons = pygame.key.get_pressed()
        pygame.draw.rect(screen, (255, 0, 0), (WIDTH - 130, 20, int(hero.health), 10))
<<<<<<< HEAD
        if buttons[pygame.K_SPACE]:
            self.is_shouting = True
        else:
            self.is_shouting = False
        if buttons[pygame.K_UP]:  # and not pygame.sprite.collide_mask(self, walls):
=======
        if buttons[pygame.K_UP]:
>>>>>>> 42b83b66d7583c74ab2a65174e17c83e512c3fb5
            self.vector = 3
            self.rect.y -= self.v
            if  pygame.sprite.collide_mask(self, walls):
                self.rect.y += self.v
            else:
                self.stand = False

        if buttons[pygame.K_DOWN]:
            self.vector = 4
            self.rect.y += self.v
            if pygame.sprite.collide_mask(self, walls):
                self.rect.y -= self.v
            else:
                self.stand = False
        if buttons[pygame.K_RIGHT]:
            self.vector = 1
            self.vector_left_right = 1
            self.rect.x += self.v
            if pygame.sprite.collide_mask(self, walls):
                self.rect.x -= self.v
            else:
                self.stand = False
        if buttons[pygame.K_LEFT]:
            self.vector = 2
            self.vector_left_right = 2
            self.rect.x -= self.v
            if pygame.sprite.collide_mask(self, walls):
                self.rect.x += self.v
            else:
                self.stand = False

        if self.frame_count % 5 == 0:
            if not self.is_shouting:
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
            else:
                if not self.stand:
                    if self.vector_left_right == 1:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_right_shouting)
                        self.image = self.frames_right_shouting[self.cur_frame]
                    if self.vector_left_right == 2:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_left_shouting)
                        self.image = self.frames_left_shouting[self.cur_frame]
                else:
                    if self.vector_left_right == 1:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_right)
                        self.image = self.frames_stand_right[self.cur_frame]
                    if self.vector_left_right == 2:
                        self.cur_frame = (self.cur_frame + 1) % len(self.frames_left)
                        self.image = self.frames_stand_left[self.cur_frame]



        if not (buttons[pygame.K_UP] or buttons[pygame.K_DOWN] or buttons[pygame.K_RIGHT] or buttons[pygame.K_LEFT]):
            self.stand = True
        self.frame_count += 1

    def fire(self):
        FireBall(self.rect.x, self.rect.y, self.vector, all_sprites, fireballs)
    def change_health(self, value):
        self.health += value
        if self.health < 0:
            self.health = 0


class Walls(pygame.sprite.Sprite):
    """"Тупо стены"""
    image = load_image('стены_1.png')
    image_mask = load_image('стены_1(ok).png')###???

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

    # позиционировать камеру на объекте target
    def update(self, *args):
        self.dx = -(args[0].rect.x + args[0].rect.w // 2 - WIDTH // 2)
        self.dy = -(args[0].rect.y + args[0].rect.h // 2 - HEIGHT // 2)


def draw_trap():
    global k
    im1 = load_image('trap1.png')
    im0 = load_image('trap0.png')
    f = load_image('firetrap.png')
    if int(str(k)[-2::]) < 50:
        screen.blit(im0, (100, 100))
    else:
        screen.blit(im1, (100, 100))
        screen.blit(f, (200, 200))
    k += 1


camera = Camera()

all_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
fireballs = pygame.sprite.Group()

k = 0
fps = 60
K = -1
xl, yl = 0, 50
save = False
Flag = False
# если хотим увидеть предысторию, то надо поставить значение True
dialog = False
gamerun = True
menu = True
lvl = False
#music('TownTheme.mp3')
fon = load_image('фон_1.png')
walls = load_image('стены_1(new).png')
# начальное положение фоновых объектов
x_fon, y_fon = 23, 45
x_walls, y_walls = 0, 0
future = False
is_hero = False
while gamerun:
    if dialog:
        font = pygame.font.Font(None, 20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gamerun = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if Flag is False and K < 14:
                        K += 1
                        Flag = True
                    elif Flag is True and K < 14:
                        K += 1
                    else:
                        Flag = False
                        lvl = True
                        dialog = False
        screen.fill((10, 10, 10))
        if Flag:
            if K not in [2, 5]:
                screen.blit(font.render(Frases[K], 1, (255, 0, 0), (0, 0, 0)), (0, 401))
            elif K == 2:
                screen.blit(font.render(Frases[K], 1, (255, 0, 0), (0, 0, 0)), (0, 401))
            elif K == 5:
                pass
        pygame.draw.line(screen, (123, 0, 123), [0, 400], [1000, 400], 1)
        pygame.display.flip()
    elif menu:
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
                if event.button == 1 and (90 < (x - xl) < 220) and (340 < (y - yl) < 370):
                    Saves('w')
                    gamerun = False
                if event.button == 1 and (90 < (x - xl) < 220) and ((290 < (y - yl) < 320) or (240 < (y - yl) < 270)):
                    future = True
                    menu = False
    elif lvl:
        if not is_hero:
            is_hero = True
            floor = Floor(all_sprites)
            walls = Walls(all_sprites)
            hero = MainHero([load_image("bomzh_vprapo_okonchat0.png"), load_image("bomzh_vprapo_okonchat1.png"),
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
                             load_image("bomzh_vprapo_shout7.png")], (800, 300),
                            all_sprites)
            for i in range(5):
                Enemy(load_image("bloody_zombie-NESW.png"), 3, 4, all_sprites, enemy_group)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                lvl = False
                gamerun = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    hero.fire()

        screen.fill((0, 0, 0))
        camera.update(hero)
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.draw(screen)
        all_sprites.update(event)

    elif future:
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 25)
        screen.blit(font.render('Эта опция появится в будущих версиях.', 1, (255, 0, 0), (0, 0, 0)), (100, 100))
        screen.blit(font.render('Вернуться в меню.', 1, (255, 0, 0), (0, 0, 0)), (420, 410))
        pygame.draw.rect(screen, (123, 0, 123), (400, 400, 200, 30), 1)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if event.button == 1 and (400 < x < 600) and (400 < y < 430):
                    future = False
                    menu = True
    pygame.display.update()
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
