import pygame
import sys


pygame.init()
size = WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode(size)
FPS = 60
clock = pygame.time.Clock()

is_menu = True


def terminate():    # Закрытие
    pygame.quit()
    sys.exit()


def start_game():    # Начало игра (закрытие меню)
    global is_menu
    is_menu = False


def start():    # Выполняется до начала игры
    while is_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()


def update():    # цикл...
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()


if __name__ == '__main__':
    start()    # Вызов старта
    while True:
        update()    # цикл...
