import general
import pygame
import sys




is_menu = True


def terminate():    # Закрытие
    pygame.quit()
    sys.exit()


def start_game():    # Начало игра (закрытие меню)
    global is_menu
    is_menu = False


def start_screen():    # Выполняется до начала игры
    return
    while is_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()


def start():
    general.load_map()


def update():    # цикл...
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()

    general.screen.fill(pygame.Color((255, 255, 255)))

    general.all_sprites.update()
    general.all_sprites.draw(general.screen)

    pygame.display.flip()
    general.clock.tick(general.FPS)


if __name__ == '__main__':
    start()    # Вызов старта
    while True:
        update()    # цикл...
