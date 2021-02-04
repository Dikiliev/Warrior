import pygame
from components import Transform, Sprite, RigidBody
import general


class Character(Sprite):    # Класс перса
    def __init__(self, image, transform, group=None, hp=100, speed=400, jump_force=1150):
        self.rb = None
        self.animator = None
        self.is_grounded = False
        self.is_flip = False
        self.is_alive = True

        super().__init__(image, transform, group)

        self.hp = hp
        self.speed = speed
        self.jump_force = jump_force
        self.weapon = None

        self.orig_img = self.image.copy()

    def add_RigidBody(self, rb):    # Добавления физики
        self.rb = rb

    def set_animation(self, animation):
        self.animation = animation

    def select_weapon(self, weapon, offset):    # добавление оружия
        self.weapon = weapon

    def take_damage(self, damage):
        print('damage ' + str(damage))
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.death()

    def death(self):
        if self.is_alive:
            self.is_alive = False
            print('Death!!!')

    def update(self):    # Понял, да...)
        if self.animator:
            self.animator.update()
            self.orig_img = self.animator.current_ani.image
            if self.is_flip:
                self.image = pygame.transform.flip(self.orig_img, True, False)
            else:
                self.image = self.orig_img.copy()

        if self.weapon is not None:
            self.weapon.flip(self.is_flip)
            self.weapon.update()

        if self.rb:    # Усли перс физичный
            self.rb.update()    # вызывает update у RigidBody
            colliders = pygame.sprite.spritecollide(self, general.borders_group, False)    # Все объекты с которыми сталкивается перс

            self.is_grounded = False
            if colliders:    # Проверка сталкивается вообще
                for coll in colliders:    # Проходимся по каждому коллайдеру с которыми соприкасается перс
                    if coll.transform_.x() <= self.transform_.x() + self.rect.width // 2 <= coll.transform_.x() + coll.rect.width \
                            and coll.transform_.y() <= self.transform_.y() + self.rect.height - 10:    # Есди коллайдер снизу перса

                        if coll.transform_.y() + coll.rect.height // 2 <= self.transform_.y():  # Есди коллайдер сверху перса
                            self.rb.velocity.y = self.rb.gravity
                            # для того чтобы поднять перса если он немного 'упал' в спрайта
                        else:

                            if self.rb.velocity.y > 0:
                                self.rb.velocity.y = 0    # то перс не падает
                            self.is_grounded = True    # и он находится тип на земле

                            # для того чтобы поднять перса если он немного 'упал' в спрайта
                            self.transform_.pos.y = coll.transform_.y() - self.rect.height + 10
                        continue

                    if coll.transform_.y() >= self.transform_.y() + self.rect.height // 1.2 or \
                            coll.transform_.y() + coll.rect.height - self.rect.height // 5 <= self.transform_.y():  # Если Спрайт не стена, завершаем
                        continue

                    if coll.transform_.x() + coll.rect.width // 2 >= self.transform_.x() + self.rect.width:    # если коллайдер с правой стороны и перс пытается двигатся в ту сторону
                        if self.rb.velocity.x > 0:
                            self.rb.velocity.x = 0  # То просто блокируем

                        #   Если сдвинуть перса если он немного зашел в стену
                        self.transform_.pos.x = coll.transform_.x() - self.rect.width + 1   # Чтобы

                    if coll.transform_.x() + coll.rect.width // 2 <= self.transform_.x():    # если коллайдер с левой стороны и перс пытается двигатся в ту сторону
                        if self.rb.velocity.x < 0:
                            self.rb.velocity.x = 0    # То просто блокируем

                        #   Если сдвинуть перса если он немного зашел в стену
                        self.transform_.pos.x = coll.transform_.x() + coll.rect.width - 1

            self.transform_.pos += (self.rb.velocity / general.FPS)    # меняем позицию перса
        super().update()

    def move(self, direction):    # Движение
        self.rb.velocity.x = direction * self.speed
        if direction < 0:
            self.animator.set_animation(1)
        elif direction > 0:
            self.animator.set_animation(1)
        else:
            self.animator.set_animation(0)

    def jump(self):    # Прыжок
        if not self.is_grounded:
            return

        self.rb.velocity.y -= self.jump_force

    def shoot(self):
        pass