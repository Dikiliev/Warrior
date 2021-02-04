import pygame
import os


size = WIDTH, HEIGHT = 1920, 1080
FPS = 60

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
borders_group = pygame.sprite.Group()
traps_group = pygame.sprite.Group()
buttons_group = pygame.sprite.Group()

camera = Camera((0, 0))


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
