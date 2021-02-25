import pygame
from components import Transform, Sprite, RigidBody, Animator
import general
from random import random, randrange


class Character(Sprite):    # Класс персонажа
    def __init__(self, animator_name, transform, group=None, hp=1000, speed=500, jump_force=1350):
        self.rb = RigidBody()   # Физака
        self.animator = Animator(animator_name)  # Контроллер Анимации
        self.is_grounded = False   # Флаг, находится ли перс на земле?
        self.is_flip = False   # Оцеркален ли перс?
        self.is_alive = True   # Флаг, жив ли перс?

        super().__init__(self.animator.current_ani.image, transform, group)

        self.hp = hp   # Здоровье
        self.speed = speed   # Скорость
        self.jump_force = jump_force   # Сила прыжка
        self.weapon = None   # Оружие

        self.orig_img = self.image.copy()

        self.can_pick_up = None

    def set_animation(self, animation):   # Смена анимации
        self.animation = animation

    def select_weapon(self, weapon=None):    # Выбов оружия
        if weapon is not None:
            self.weapon = weapon
        else:
            if self.can_pick_up is None:
                return
            self.weapon.throw_weapons()
            self.weapon = self.can_pick_up
            self.weapon.init_pos(self.transform_)

        if general.player_group in self.groups():
            self.weapon.is_enemy = False

    def take_damage(self, damage):   # Получение урона
        general.SOUND_HIT.play()    # Звук попадения
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

        # Оружие с которым сталкивается перс
        weapons = pygame.sprite.spritecollide(self, general.weapons_group, False)
        self.can_pick_up = None
        if weapons:
            for weapon in weapons:
                if weapon.transform_.parent is None:
                    self.can_pick_up = weapon
                    break

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
    def __init__(self, type_enemy, transform):
        enemy = general.ENEMIES[type_enemy]
        super().__init__(enemy['animator'], transform, general.enemy_group, hp=enemy['hp'], speed=200)
        self.is_attack = 0  # Атакует ли враг (используется как bool)
        self.time = 0  # время

        self.max_x = self.transform_.x() + enemy['radius']
        self.min_x = self.transform_.x() - enemy['radius']
        self.direction = [-1, 1][randrange(0, 2)]  # направление

        self.select_weapon(Weapon(enemy['weapon'], self.transform_))  # выьор оружия

    def update(self):
        distance = abs(general.player.transform_.x() - self.transform_.x())  # дистанция до игрока
        self.move(0)
        if distance > 500:
            self.patrol()
        else:
            self.attacking()
        super().update()

    def attacking(self):  # Атака на игрока
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

    def patrol(self):  # Патрулирование
        if self.transform_.x() >= self.max_x:
            self.direction = -1
        elif self.transform_.x() <= self.min_x:
            self.direction = 1

        self.is_flip = bool(self.direction - 1)
        self.move(self.direction)


class Weapon(Sprite):    # Класс оружия
    def __init__(self, name, parent=None, radius=1000, pos=None):
        self.options = eval(open(f'data/Weapons/{name}.txt', 'r').read())   # Все параметры оружия

        if parent is not None:  # Если родитель есть
            super().__init__(general.weapons[self.options['img']],
                             Transform(self.options['pos'], parent=parent), general.weapons_group)
        else:  # Иначе присваваем transform позицию
            super().__init__(general.weapons[self.options['img']],
                             Transform(pos, parent=None), general.weapons_group)

        self.options['bullet'] = general.bullets[self.options['bullet']]

        self.spawn_pos = self.options['spawn']  # Точка появления пули
        self.orig_img = self.image.copy()
        self.bullet = self.options['bullet'].copy()   # пуля

        self.attack = False
        self.shot_timer = 0  # таймер следущего выстрела (скорострельность)

        self.is_enemy = True

    def init_pos(self, parent):  # Настройка после подбора
        self.transform_.set_pos(self.options['pos'][0], self.options['pos'][1])
        self.transform_.parent = parent

    def throw_weapons(self):  # Настройка после выброса
        self.transform_.set_pos(self.transform_.x(), self.transform_.y())
        self.transform_.parent = None

    def flip(self, is_flip):  # Вращение
        self.image = pygame.transform.flip(self.orig_img, is_flip, False)
        self.bullet = pygame.transform.flip(self.options['bullet'], is_flip, False)
        if is_flip:
            self.transform_.pos = pygame.math.Vector2(self.options['pos_f'])
            self.spawn_pos = self.options['spawn_f']
        else:
            self.transform_.pos = pygame.math.Vector2(self.options['pos'])
            self.spawn_pos = self.options['spawn']

    def shoot(self, pos):  # Выстрел
        if self.shot_timer > 0:
            return

        general.SOUNDS[self.options['audio']].play()    # Звук

        direction = (pos[0] - self.transform_.x() - self.spawn_pos[0],
                     pos[1] - self.transform_.y() - self.spawn_pos[1])

        max_ = max(map(lambda x: abs(x), direction))  # Максимальное модульное значение

        if 'shotgun' in self.options['name']:
            # Создание и передача параметров пули
            bullets = [Bullet(self.bullet, Transform(self.transform_.global_pos() + self.spawn_pos),
                              self.options['speed'], self.options['damage'], self.is_enemy) for _ in range(10)]

            for i in range(len(bullets)):
                # Рандомное измение направления пули
                bullets[i].rb.velocity.x = bullets[i].speed * (direction[0] / max_ + randrange(-3, 4) / 10)
                bullets[i].rb.velocity.y = bullets[i].speed * (direction[1] / max_ + randrange(-3, 4) / 10)
        else:
            # Создание и передача параметров в пулю
            bullet = Bullet(self.bullet, Transform(self.transform_.global_pos() + self.spawn_pos),
                            self.options['speed'], self.options['damage'], self.is_enemy)

            # Направление пули
            bullet.rb.velocity.x = bullet.speed * direction[0] / max_
            bullet.rb.velocity.y = bullet.speed * direction[1] / max_

        self.shot_timer = self.options['rate_of']    # Обновление таймера

    def update(self):
        super().update()
        if self.shot_timer > 0:
            self.shot_timer -= 1 / general.FPS


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


