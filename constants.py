# подписи к кнопка главного меню
LABELS = ['Clash of MIPT', 'Новая игра',  'Выход']

# размеры экрана
SCREENSIZE = WIDTH, HEIGHT = 1000, 600
#SCREENSIZE = WIDTH, HEIGHT = 1920, 1080


class FireBall_constants:
    v = 12 # скорость фаерболла

class MainHero_constants:
    gold = 100
    v = 5
    health = 100
    manna = 100


class MageFireBall_constants:
    v = 12  # скорость фаерболла
    damage = 5  # урон фаерболла


class Spell_constants:
    BLUE = (20, 20, 255)
    WHITE = (240, 240, 240)
    GREEN = (20, 240, 20)
    RED = (240, 30, 30)
    slow_motion_alpha = 0.25
    fast_motion_herov = 10
    normal_motion_herov = 5
    attack_coef = 2


class Tree_constants:
    manna_coords = [(804, 310), (-73, 500)]
    manna_real_coords = [(410, 250), (-430, 447)]
    health_coords = [(1720, 260)]
    health_real_coords = [(1312, 187)]

class Enemy_constants():
    v = 4  # скорость зомби
    health = 10  # его здоровье
    damage = 0.2  # наносимый урон
    slowing = 1  # коэффициент замедления от зелья
    RED = (255, 0, 0)  # цвет полоски здоровья


class Mage_constants():
    v = 4
    health = 10  # его здоровье
    damage = 0.2  # наносимый урон
    slowing = 1  # коэффициент замедления от зелья