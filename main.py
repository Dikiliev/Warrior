import general
from general import load_image
from components import Camera, RigidBody, Transform, Background, Animator, Sprite, Button
from characters import Character, Weapon, ShotGun Enemy
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
    # создание кнопок
    menu_buttons = [Sprite(general.load_image('fon.jpg'), Transform((0, 0))),
                    Sprite(general.load_image('Title.jpg'), Transform((710, 80))),
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


camera = None
cursor = None
player = None
is_player_attack = False


def start():
    global cursor
    global camera
    global player

    general.load_map()

    player = Character(general.load_image('Pers/Idle.png'), Transform((100, 100)), group=general.player_group)
    general.player = player

    enemy_1 = Enemy(general.load_image('Enemy/Enemy1_Idle.png'), Transform((1200, 100)), speed=200, hp=500)
    enemy_1.select_weapon(Weapon('ak_47', enemy_1.transform_))
    enemy_1.animator = Animator('Enem3')

    camera = Camera(Transform((0, 0), parent=player.transform_), offset=(-900, -540))
    general.camera = camera

    player.animator = Animator('Pers')

    weapon = ShotGun('shotgun', player.transform_)
    player.select_weapon(weapon)

    cursor = Background(load_image('cursor.png'), Transform((100, 100)))


direction = 0
mouse_pos = (0, 0)


def update():    # цикл...
    global direction, mouse_pos, is_player_attack
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
                is_player_attack = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_player_attack = False

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

    if is_player_attack:
        pos = pygame.mouse.get_pos()
        pos = (pos[0] + general.camera.transform_.x(), pos[1] + general.camera.transform_.y())
        player.weapon.shoot(pos)

    general.all_sprites.draw(general.screen)

    pygame.display.flip()
    general.clock.tick(general.FPS)


if __name__ == '__main__':
    start_screen()
    start()    # Вызов старта
    while True:
        update()    # цикл...
