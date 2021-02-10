import general
from general import load_image
from components import Camera, RigidBody, Transform, Background, Animator
from characters import Character, Weapon
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


camera = None
cursor = None
player = None


def start():
    global cursor
    global camera
    global player

    general.load_map()

    player = Character(general.load_image('Pers/Idle.png'), Transform((100, 100)), group=general.player_group)

    camera = Camera(Transform((0, 0), parent=player.transform_), offset=(-900, -540))
    general.camera = camera

    player.animator = Animator('Pers')

    weapon = Weapon('ak_47', player.transform_, general.player_group)
    player.weapon = weapon

    cursor = Background(load_image('cursor.png'), Transform((100, 100)))


direction = 0
mouse_pos = (0, 0)


def update():    # цикл...
    global direction, mouse_pos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                direction = 1
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                direction = -1
            elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                player.jump()
            elif event.key == pygame.K_ESCAPE:
                terminate()

        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_RIGHT, pygame.K_d) and direction == 1:
                direction = 0
            elif event.key in (pygame.K_LEFT, pygame.K_a) and direction == -1:
                direction = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player.weapon.attack = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                player.weapon.attack = False

        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            cursor.transform_.set_pos(mouse_pos[0] - 10, mouse_pos[1] - 10)
            camera.transform_.pos = camera.offset + (cursor.transform_.pos - pygame.math.Vector2(960, 540)) * 0.2
            if cursor.transform_.x() > 940:
                player.is_flip = False
            else:
                player.is_flip = True

            pygame.mouse.set_visible(False)

    general.screen.fill(pygame.Color((0, 0, 0)))

    player.move(direction)  # Движения перса в направлении direction
    general.all_sprites.update()
    general.all_sprites.draw(general.screen)

    pygame.display.flip()
    general.clock.tick(general.FPS)


if __name__ == '__main__':
    start()    # Вызов старта
    while True:
        update()    # цикл...
