import pygame
from components import Transform, Camera, Sprite
from characters import Character
import os


size = WIDTH, HEIGHT = 1920, 1080
FPS = 60

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
borders_group = pygame.sprite.Group()
traps_group = pygame.sprite.Group()
buttons_group = pygame.sprite.Group()

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


weapons = cut_sheet(load_image('Weapons.png'), 1, 3)
bullets = cut_sheet(load_image('Bullets.png'), 1, 3)

camera = Camera(Transform((0, 0)))
player = None


KEY_PLATFORM = {'up left': 0,   'up': 1,   'up right': 2,
                'left': 4,      '': 4,    'right': -1,
                'down left': 4, 'down': 4, 'down right': 5,
                'descent': 3, '.': None,
                'bridge left': 6, 'bridge': 7, 'bridge right': 8,
                'thorns up': 9, 'thorns': 11, 'thorns down': 10,
                'iron left': 0, 'iron': 1, 'iron right': 2}


map_txt = open('data/level.txt').read().split()
platforms = cut_sheet(load_image('platforms.png'), 3, 4)
platforms.append(cut_sheet(load_image('platforms.png'), 3, 4, (200, 80)))

irons = cut_sheet(load_image('platforms2.png'), 3, 1)


def load_map():
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

            elif platform == 't':
                pass


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