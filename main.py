import general
from general import load_image
from components import Camera, RigidBody, Transform, Background, Animator, Sprite, Button
from characters import Character, Weapon, Enemy
import pygame
import sys
from time import sleep

is_game = True
is_menu = True


def terminate():    # Закрытие
    pygame.quit()
    sys.exit()


def start_game():    # Начало игра (закрытие меню)
    global is_menu
    is_menu = False


def start_screen():    # Выполняется до начала игры
    # создание кнопок
    menu_buttons = [Sprite(general.load_image('fon.jpg'), Transform((0, 0))),
                    Sprite(general.load_image('title.png'), Transform((560, 80))),
                    Button(general.load_image('btn_start.png'), Transform((710, 500)), start_game,
                           general.buttons_group),
                    Button(general.load_image('btn_exit.png'), Transform((760, 700)), terminate,
                           general.buttons_group)]
    while is_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                general.buttons_group.update(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
        general.all_sprites.update()
        general.all_sprites.draw(general.screen)
        pygame.display.flip()
        general.clock.tick(general.FPS)
    # удаление кнопок
    for btn in menu_buttons:
        btn.kill()


def finish():
    Background(general.load_image('fon.jpg'), Transform((0, 0))),
    Background(general.load_image('end.png'), Transform((560, 80))),
    while True:
        for event in pygame.event.get():
            if event.type != pygame.MOUSEMOTION:
                terminate()
        general.all_sprites.update()
        general.all_sprites.draw(general.screen)
        pygame.display.flip()
        general.clock.tick(general.FPS)


def game_over():
    Background(general.load_image('fon.jpg'), Transform((0, 0))),
    Background(general.load_image('gameover.png'), Transform((560, 80))),
    while True:
        for event in pygame.event.get():
            if event.type != pygame.MOUSEMOTION:
                terminate()
        general.all_sprites.update()
        general.all_sprites.draw(general.screen)
        pygame.display.flip()
        general.clock.tick(general.FPS)


cursor = None
is_player_attack = False


def start():
    global cursor

    general.load_map()

    player = Character('Pers', Transform((100, 100)), group=general.player_group)
    general.player = player

    general.camera = Camera(Transform((0, 0), parent=player.transform_), offset=(-900, -540))

    player.animator = Animator('Pers')

    weapon = Weapon('pistol', player.transform_)
    player.select_weapon(weapon)

    Weapon('ak_47', pos=(2300, 950))
    Weapon('shotgun', pos=(2450, 950))
    Weapon('rifle', pos=(2600, 950))

    Weapon('machine gun', pos=(14800, 1750))
    Weapon('p90', pos=(15000, 1750))
    Weapon('sniper', pos=(15200, 1750))

    cursor = Background(load_image('cursor.png'), Transform((100, 100)))


direction = 0
direction_y = 0  # для лазанья по веревкам
mouse_pos = (0, 0)


def update():    # цикл...
    global direction, direction_y, mouse_pos, is_player_attack
    if not general.player.is_alive:
        game_over()

    for event in pygame.event.get():
        if not general.player.is_alive:
            terminate()
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                direction = 1
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                direction = -1

            elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                if general.player.on_rope_stay:
                    direction_y = -1
                else:
                    general.player.jump()

            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if general.player.on_rope_stay:
                    direction_y = 1

            elif event.key == pygame.K_ESCAPE:
                terminate()
            elif event.key == pygame.K_e:
                general.player.select_weapon()

        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_RIGHT, pygame.K_d) and direction == 1:
                direction = 0
            elif event.key in (pygame.K_LEFT, pygame.K_a) and direction == -1:
                direction = 0

            elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                direction_y = 0

            elif event.key in (pygame.K_DOWN, pygame.K_s):
                direction_y = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                is_player_attack = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_player_attack = False

        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            cursor.transform_.set_pos(mouse_pos[0] - 10, mouse_pos[1] - 10)
            general.camera.transform_.pos = general.camera.offset + (cursor.transform_.pos - pygame.math.Vector2(960, 540)) * 0.2
            if cursor.transform_.x() > 940:
                general.player.is_flip = False
            else:
                general.player.is_flip = True

            pygame.mouse.set_visible(False)

    general.screen.fill(pygame.Color((0, 0, 0)))
    general.health_indicator()

    general.player.move(direction, direction_y)  # Движения перса в направлении direction
    general.all_sprites.update()

    if is_player_attack:
        pos = pygame.mouse.get_pos()
        pos = (pos[0] + general.camera.transform_.x(), pos[1] + general.camera.transform_.y())
        general.player.weapon.shoot(pos)

    general.all_sprites.draw(general.screen)

    if general.player.transform_.y() > 2000 and general.player.is_alive:
        general.player.death()
    elif general.player.transform_.x() > 44700:
        finish()

    pygame.display.flip()
    general.clock.tick(general.FPS)


if __name__ == '__main__':
    start_screen()
    start()    # Вызов старта
    while True:
        update()    # цикл...
