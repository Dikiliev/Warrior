import pygame
from components import Transform, Sprite, RigidBody
import general
from random import random, randrange


class Character(Sprite):    # Класс персонажа
    def __init__(self, image, transform, group=None, hp=100, speed=500, jump_force=1350):
        self.rb = RigidBody()   # Физака
        self.animator = None   # Контроллер Анимации
        self.is_grounded = False   # Флаг, находится ли перс на земле?
        self.is_flip = False   # Оцеркален ли перс?
        self.is_alive = True   # Флаг, жив ли перс?

        super().__init__(image, transform, group)

        self.hp = hp   # Здоровье
        self.speed = speed   # Скорость
        self.jump_force = jump_force   # Сила прыжка
        self.weapon = None   # Оружие

        self.orig_img = self.image.copy()

    def set_animation(self, animation):   # Смена анимации
        self.animation = animation

    def select_weapon(self, weapon):    # Выбов оружия
        self.weapon = weapon
        if general.player_group in self.groups():
            self.weapon.is_enemy = False

    def take_damage(self, damage):   # Получение урона
        print('damage ' + str(damage))
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.death()

    def death(self):   # Смерть
        self.is_alive = False
        self.weapon.kill()
        self.kill()

    def update(self):
        if self.animator:
            self.animator.update()
            self.orig_img = self.animator.current_ani.image   # Замена спрайта (Анимация)

            # Поворот перса
            if self.is_flip:
                self.image = pygame.transform.flip(self.orig_img, True, False)
            else:
                self.image = self.orig_img.copy()

        # Поворот оружия и его update
        if self.weapon is not None:
            self.weapon.flip(self.is_flip)
            self.weapon.update()

        if self.rb:
            self.rb.update()
            colliders = pygame.sprite.spritecollide(self, general.borders_group, False)    # Все объекты с которыми сталкивается перс

            self.is_grounded = False
            if colliders:    # Проверка сталкивается вообще
                for coll in colliders:    # Проходимся по каждому коллайдеру с которыми соприкасается перс
                    if coll.transform_.x() <= self.transform_.x() + self.rect.width // 2 <= coll.transform_.x() + coll.rect.width \
                            and coll.transform_.y() <= self.transform_.y() + self.rect.height - 10:    # Есди перс на или под коллайдером

                        if coll.transform_.y() + coll.rect.height // 2 <= self.transform_.y():  # Есди коллайдер сверху
                            self.rb.velocity.y = self.rb.gravity
                        else:  # Есди коллайдер снизу
                            if self.rb.velocity.y > 0:
                                self.rb.velocity.y = 0    # то перс не падает
                            self.is_grounded = True    # и он находится тип на земле

                            # для того чтобы поднять перса если он немного 'упал' в спрайта
                            self.transform_.pos.y = coll.transform_.y() - self.rect.height + 10
                        continue

                    # Если Спрайт не стена, завершаем (что бы перс не застревал на спрайтах заемли)
                    elif coll.transform_.y() >= self.transform_.y() + self.rect.height // 1.2 or \
                            coll.transform_.y() + coll.rect.height - self.rect.height // 5 <= self.transform_.y():
                        continue

                    # если коллайдер с правой стороны и перс пытается двигатся в ту сторону
                    if coll.transform_.x() + coll.rect.width // 2 >= self.transform_.x() + self.rect.width:
                        if self.rb.velocity.x > 0:
                            self.rb.velocity.x = 0    # блокирование движения

                        #   сдвиг перса (если он немного зашел в стену)
                        self.transform_.pos.x = coll.transform_.x() - self.rect.width + 1   # Чтобы

                    # если коллайдер с левой стороны и перс пытается двигатся в ту сторону
                    elif coll.transform_.x() + coll.rect.width // 2 <= self.transform_.x():
                        if self.rb.velocity.x < 0:
                            self.rb.velocity.x = 0    # блокирование движения

                        #   сдвиг перса (если он немного зашел в стену)
                        self.transform_.pos.x = coll.transform_.x() + coll.rect.width - 1

            self.transform_.pos += (self.rb.velocity / general.FPS)    # Движение
        super().update()

    def move(self, direction):    # Движение и смена анимации
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


class Enemy(Character):    # Класс Врага
    def __init__(self, image, transform, hp=100, speed=500, jump_force=1350, radius=250):
        super().__init__(image, transform, general.enemy_group, hp, speed, jump_force)
        self.is_attack = 0
        self.time = 0

        self.max_x = self.transform_.x() + radius
        self.min_x = self.transform_.x() - radius
        self.direction = [-1, 1][randrange(0, 2)]

    def update(self):
        distance = abs(general.player.transform_.x() - self.transform_.x())
        self.move(0)
        if distance > 500:
            self.patrol()
        else:
            self.attacking()
        super().update()

    def attacking(self):
        pos = general.player.transform_.int_pos()
        pos = [pos[0] + 40, pos[1] + 40]

        if pos[0] > self.transform_.x() + 40 + 100 < self.max_x:
            self.is_flip = False
            self.move(1)
        elif pos[0] < self.transform_.x() + 40 - 100 > self.min_x:
            self.move(-1)
            self.is_flip = True

        self.time -= 1 / general.FPS
        if self.time <= 0:
            self.is_attack ^= 1
            if self.is_attack:
                self.time = random() * 0.5
            else:
                self.time = random() * 3
        if self.is_attack:

            self.weapon.shoot(pos)

    def patrol(self):
        if self.transform_.x() >= self.max_x:
            self.direction = -1
        elif self.transform_.x() <= self.min_x:
            self.direction = 1

        self.is_flip = bool(self.direction - 1)
        self.move(self.direction)


class Weapon(Sprite):    # Класс оружия
    def __init__(self, name, parent=None, radius=1000):
        self.options = eval(open(f'data/Weapons/{name}.txt', 'r').read())

        super().__init__(general.weapons[self.options['img']], Transform(self.options['pos'], parent=parent))

        self.options['bullet'] = general.bullets[self.options['bullet']]

        self.spawn_pos = self.options['spawn']
        self.orig_img = self.image.copy()
        self.bullet = self.options['bullet'].copy()

        self.attack = False
        self.next_shot = 0

        self.is_enemy = True

    def flip(self, is_flip):
        self.image = pygame.transform.flip(self.orig_img, is_flip, False)
        self.bullet = pygame.transform.flip(self.options['bullet'], is_flip, False)
        if is_flip:
            self.transform_.pos = pygame.math.Vector2(self.options['pos_f'])
            self.spawn_pos = self.options['spawn_f']
        else:
            self.transform_.pos = pygame.math.Vector2(self.options['pos'])
            self.spawn_pos = self.options['spawn']

    def shoot(self, pos):
        if self.next_shot > 0:
            return

        s = Bullet(self.bullet, Transform(self.transform_.global_pos() + self.spawn_pos), is_enemy=self.is_enemy)
        s.speed = self.options['speed']

        direction = (pos[0] - self.transform_.x() - self.spawn_pos[0],
                     pos[1] - self.transform_.y() - self.spawn_pos[1])

        maxx = max(map(lambda x: abs(x), direction))
        s.rb.velocity.x = s.speed * direction[0] / maxx
        s.rb.velocity.y = s.speed * direction[1] / maxx

        self.next_shot = self.options['rate_of']

    def update(self):
        super().update()
        if self.next_shot > 0:
            self.next_shot -= 1 / general.FPS


class Bullet(Sprite):    # Класс сюрикена, только его пока нету)))
    def __init__(self, image, transform, speed=1500, damage=25, is_enemy=True):
        self.rb = RigidBody()
        self.rb.gravity = 0
        self.is_enemy = is_enemy

        super().__init__(image, transform)
        self.speed = speed
        self.damage = damage
        self.time_destroy = 10.0  # Время до самоунчтожения

    def update(self):
        if self.rb:    # Усли перс физичный
            self.rb.update()    # вызывает update у RigidBody
            collider = pygame.sprite.spritecollideany(self, general.borders_group)    # Все объекты с которыми сталкивается перс

            if collider:    # Проверка сталкивается вообще
                self.kill()
            else:
                if self.is_enemy:
                    collider = pygame.sprite.spritecollideany(self, general.player_group)
                else:
                    collider = pygame.sprite.spritecollideany(self, general.enemy_group)
                if collider:
                    collider.take_damage(self.damage)
                    self.kill()

            if self.time_destroy <= 0:
                self.kill()
            self.time_destroy -= 1 / general.FPS

            self.transform_.pos += (self.rb.velocity / general.FPS)  # меняем позицию перса

        super().update()


