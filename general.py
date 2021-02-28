import pygame
import random
from components import Transform, Camera, Sprite, Particle, Bandages
from characters import Character, Enemy
import os
import sys

size = WIDTH, HEIGHT = 1920, 1080
FPS = 60

# Группы спрайтов
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
borders_group = pygame.sprite.Group()
ropes_group = pygame.sprite.Group()
buttons_group = pygame.sprite.Group()
weapons_group = pygame.sprite.Group()
bandages_group = pygame.sprite.Group()

pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f'Файл с изображением \'{fullname}\' не найден')
        sys.exit()
    image = pygame.image.load(fullname)

    if color_key:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def cut_sheet(sheet, columns, rows, custom=False):
    rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                       sheet.get_height() // rows)
    if custom:
        frame_location = (custom[0], custom[1])
        frame = sheet.subsurface(pygame.Rect(
            frame_location, rect.size))

        return frame

    frames = []
    for j in range(rows):
        for i in range(columns):
            frame_location = (rect.w * i, rect.h * j)
            frames.append(sheet.subsurface(pygame.Rect(
                frame_location, rect.size)))

    return frames


weapons = cut_sheet(load_image('Weapons.png'), 1, 8)     # Спрайты оружии
bullets = cut_sheet(load_image('Bullets.png'), 1, 3)     # Спрайты патронов

camera = Camera(Transform((0, 0)))
player = None

# Все враги
ENEMIES = [{'weapon': 'pistol', 'animator': 'Enem4', 'hp': 100, 'radius': 200},
           {'weapon': 'ak_47', 'animator': 'Enem2', 'hp': 300, 'radius': 100},
           {'weapon': 'shotgun', 'animator': 'Enem2', 'hp': 300, 'radius': 200},
           {'weapon': 'sniper', 'animator': 'Enem1', 'hp': 200, 'radius': 0},
           {'weapon': 'minigun', 'animator': 'Enem3', 'hp': 1500, 'radius': 400}]

# Платформы
KEY_PLATFORM = {'up left': 0, 'up': 1, 'up right': 2,
                'left': 4, '': 4, 'right': -1,
                'down left': 4, 'down': 4, 'down right': 5,
                'descent': 3, '.': None,
                'bridge left': 6, 'bridge': 7, 'bridge right': 8,
                'thorns up': 9, 'thorns': 11, 'thorns down': 10,
                'iron left': 0, 'iron': 1, 'iron right': 2}

map_txt = open('data/level.txt').read().split()     # Текстовый файл карты
platforms = cut_sheet(load_image('platforms.png'), 3, 4)     # платформы
platforms.append(cut_sheet(load_image('platforms.png'), 3, 4, (200, 80)))

irons = cut_sheet(load_image('platforms2.png'), 3, 1)     # Железные платформы

# Звуки
Sound = pygame.mixer.Sound
SOUND_HIT = Sound('data/Audio/hit.mp3')
SOUND_BLOOD = Sound('data/Audio/blood.mp3')
SOUNDS = [Sound('data/Audio/pistol.mp3'), Sound('data/Audio/gun.mp3'),
          Sound('data/Audio/machine_gun.mp3'), Sound('data/Audio/sniper.mp3'),
          Sound('data/Audio/psg.mp3'), Sound('data/Audio/shotgun.mp3')]


def load_map():     # Загрузка карты
    for y in range(len(map_txt)):
        for x in range(len(map_txt[y])):
            platform = map_txt[y][x]
            if platform == '#':
                platform = '#-'

                key = up_or_down(x, y, platform)
                key += ' ' + right_or_left(x, y, platform)

                if key == ' ' and map_txt[y][x + 1] in platform and map_txt[y - 1][x] in platform \
                        and map_txt[y - 1][x + 1] not in platform:
                    key = 'descent'

                Sprite(platforms[KEY_PLATFORM[key.strip(' ')]], Transform((x * 100, y * 100)), borders_group)

            elif platform == '-':
                key = 'bridge '
                key += right_or_left(x, y, platform)
                Sprite(platforms[KEY_PLATFORM[key.strip(' ')]], Transform((x * 100, y * 100)), borders_group)

            elif platform == '=':
                key = 'iron '
                key += right_or_left(x, y, platform)
                Sprite(irons[KEY_PLATFORM[key.strip(' ')]], Transform((x * 100, y * 100)), borders_group)
                if 'left' in key:
                    Sprite(load_image('Tros.png'), Transform((x * 100 + 40, y * 100 - 2000)))
                elif 'right' in key:
                    Sprite(load_image('Tros.png'), Transform((x * 100 + 50, y * 100 - 2000)))

            elif platform == '|':
                for i in range(20):
                    Sprite(load_image('rope.png'), Transform((x * 100, y * 100 - 100 * i)), ropes_group)
            elif platform == 'f':
                Sprite(load_image('flag.png'), Transform((x * 100, y * 100)))
            elif platform == 'b':
                Bandages(load_image('bandages.png'), Transform((x * 100, y * 100)))

    # Добавление врагов после прогрузки карты для того, что бы плаформы не были на врагах
    for y in range(len(map_txt)):
        for x in range(len(map_txt[y])):
            platform = map_txt[y][x]
            if platform == '1':
                Enemy(0, Transform((x * 100, y * 100)))
            elif platform == '2':
                Enemy(1, Transform((x * 100, y * 100)))
            elif platform == '3':
                Enemy(2, Transform((x * 100, y * 100)))
            elif platform == '4':
                Enemy(3, Transform((x * 100, y * 100)))
            elif platform == '5':
                Enemy(4, Transform((x * 100, y * 100)))


def right_or_left(x, y, platform):
    if map_txt[y][x + 1] not in platform:
        return 'right'
    elif map_txt[y][x - 1] not in platform:
        return 'left'
    return ''


def up_or_down(x, y, platform):
    if map_txt[y - 1][x] not in platform:
        return 'up'
    elif map_txt[y + 1][x] not in platform:
        return 'down'
    return ''


# Спрайты частиц
PARTICLE_IMAGES = [load_image('blood.png'), load_image('ground_particle.png')]


def create_particles(pos, index_img=0, count=20):     # Создание частиц
    for i in range(count):
        Particle(PARTICLE_IMAGES[index_img], Transform((pos[0], pos[1])),
                 pygame.math.Vector2(random.randrange(-700, 700), random.randrange(-800, 700)))


def health_indicator():     # Индикатор здоровья
    font = pygame.font.Font(None, 70)
    text = font.render(str(player.hp), True, (255, 20, 85))
    screen.blit(text, (100, 50))
    pygame.draw.rect(screen, (255, 20, 85), (250, 50, 300, 40))
    pygame.draw.rect(screen, (255, 20, 85), (250, 50, player.hp / 3, 40))