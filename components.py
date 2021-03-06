import pygame
import general
import random


class Transform:    # Типа класс позиции и размера
    def __init__(self, pos, scale=(1, 1), parent=None):
        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.scale = pygame.math.Vector2(scale[0], scale[1])
        self.parent = parent

    def int_pos(self):
        return self.x(), self.y()

    def set_pos(self, x, y):
        self.pos = pygame.math.Vector2(x, y)

    def global_pos(self):
        return pygame.math.Vector2(self.x(), self.y())

    def x(self):
        if self.parent is not None:
            return int(self.parent.pos.x + self.pos.x)
        return int(self.pos.x)

    def y(self):
        if self.parent is not None:
            return int(self.parent.pos.y + self.pos.y)
        return int(self.pos.y)


class RigidBody:    # Типа физика))
    def __init__(self):
        self.velocity = pygame.math.Vector2(0, 0)
        self.gravity = 800

    def update(self):    # Вызывается каждый кадр
        if self.velocity.y < self.gravity:
            self.velocity.y += self.gravity // 15
            if self.velocity.y > self.gravity:
                self.velocity.y = self.gravity


class Camera:
    def __init__(self, transform, offset=(0, 0)):
        self.transform_ = transform
        self.offset = pygame.math.Vector2(offset[0], offset[1])     # Смещение

    def follow(self, pos):     # Слежение
        self.transform_.pos = pos + self.offset


class Sprite(pygame.sprite.Sprite):    # Класс Спрайта
    def __init__(self, image, transform, group=None):
        super().__init__(general.all_sprites)
        if group is not None:
            self.add(group)

        self.transform_ = transform
        self.image = image
        self.rect = self.image.get_rect().move(self.transform_.x() - general.camera.transform_.x(),
                                               self.transform_.y() - general.camera.transform_.y())

    def update(self):  # Смещение в зависимости от камеры
        self.rect = self.image.get_rect().move(self.transform_.x() - general.camera.transform_.x(),
                                               self.transform_.y() - general.camera.transform_.y())

    def draw(self, screen):
        if abs(general.player.transform_.x() - self.transform_.x()) > 2000:
            return

        super().draw()


class Background(Sprite):  # Задний фон
    def __init__(self, image, transform, speed=0):
        super().__init__(image, transform)
        self.speed = speed

    def update(self):
        self.rect = self.image.get_rect().move(self.transform_.x() - int(general.camera.transform_.x() * self.speed),
                                               self.transform_.y() - int(general.camera.transform_.y() * self.speed))


class AnimationClip:  # Анимация
    def __init__(self, sheet, columns, rows, time_frames):
        self.sheet = sheet

        self.frames = []  # Спрайты
        self.cut_sheet(sheet, int(columns), int(rows))

        self.image = self.frames[0]

        self.time = 0.0
        self.end = max(list(time_frames.keys()))
        self.time_frames = {}

        for time in time_frames:
            self.time_frames[time] = self.frames[time_frames[time]]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.time += 1 / general.FPS
        keys = list(self.time_frames.keys())
        key = max(keys, key=lambda x: (float(x) <= self.time, x))
        if self.time >= self.end:
            self.time = 0
        self.image = self.time_frames[key]


class Animator:  # Контроллер Анимации
    def __init__(self, controller):
        controller = open(f'data/Animations/{controller}.txt', 'r').read()
        self.animations = []
        for ani in controller.split('\n'):
            ani = ani.split(';')
            self.animations.append(AnimationClip(general.load_image(ani[0]), ani[1], ani[2], eval(ani[3])))
        self.current_ani = self.animations[0]

    def set_animation(self, i):  # Смена анимации
        if i >= len(self.animations):
            return
        self.current_ani = self.animations[i]

    def update(self):
        self.current_ani.update()


class Particle(Sprite):  # класс частицы
    def __init__(self, image, transform_, velocity):
        super().__init__(image, transform_)

        # у каждой частицы своя скорость — это вектор
        self.velocity = velocity
        self.gravity = 500
        self.life_time = 0.2

    def update(self):
        self.life_time -= 1 / general.FPS
        if self.life_time <= 0:
            self.kill()
            return

        # движение с ускорением под действием гравитации
        self.velocity.y += self.gravity / general.FPS
        # перемещаем частицу
        self.transform_.pos += self.velocity / general.FPS

        # Изменяем размер
        self.image = pygame.transform.scale(self.image, (int(200 * self.life_time), int(200 * self.life_time)))

        super().update()


class Bandages(Sprite):     # Аптечка
    def __init__(self, image, transform):
        super().__init__(image, transform, general.bandages_group)


class Button(Sprite):     # Кнопка
    def __init__(self, image, transform, func, group=None):
        super().__init__(image, transform, group)
        self.func = func

    def update(self, pos=None):
        if pos is None:
            return
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.width and \
                self.rect.y <= pos[1] <= self.rect.y + self.rect.height:
            self.func()
