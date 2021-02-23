import pygame
import general


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

    def addForce(self, force):    # пока не используется
        self.velocity += force

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

    def update(self):
        self.rect = self.image.get_rect().move(self.transform_.x() - general.camera.transform_.x(),
                                               self.transform_.y() - general.camera.transform_.y())


class Background(Sprite):
    def __init__(self, image, transform, group=None, speed=0):
        super().__init__(image, transform, group)
        self.speed = speed

    def update(self):
        self.rect = self.image.get_rect().move(self.transform_.x() - int(general.camera.transform_.x() * self.speed),
                                               self.transform_.y() - int(general.camera.transform_.y() * self.speed))


class AnimationClip:
    def __init__(self, sheet, columns, rows, time_frames):
        self.sheet = sheet

        self.frames = []
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


class Animator:
    def __init__(self, controller):
        controller = open(f'data/Animations/{controller}.txt', 'r').read()
        self.animations = []
        for ani in controller.split('\n'):
            ani = ani.split(';')
            self.animations.append(AnimationClip(general.load_image(ani[0]), ani[1], ani[2], eval(ani[3])))
        self.current_ani = self.animations[0]

    def set_animation(self, i):
        if i >= len(self.animations):
            return
        self.current_ani = self.animations[i]

    def update(self):
        self.current_ani.update()


class Button(Sprite):
    def __init__(self, image, transform, func, group=None):
        super().__init__(image, transform, group)
        self.func = func

    def update(self, pos=None):
        if pos is None:
            return
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.width and \
                self.rect.y <= pos[1] <= self.rect.y + self.rect.height:
            self.func()