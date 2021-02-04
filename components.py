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
