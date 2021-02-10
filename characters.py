import pygame
from components import Transform, Sprite, RigidBody
import general


class Character(Sprite):    # Класс перса
    def __init__(self, image, transform, group=None, hp=100, speed=500, jump_force=1350):
        self.rb = RigidBody()
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


class Enemy(Character):
    def __init__(self, image, transform, hp=100, speed=500, jump_force=1350, radius=1000):
        super().__init__(image, transform, general.enemy_group, hp, speed, jump_force)

    def update(self):
        distance = abs(general.player.transform_.x() - self.transform_.x())
        self.weapon.shoot(general.player.transform_.int_pos())
        super().update()


class Weapon(Sprite):    # Класс оружия (недоработан!)
    def __init__(self, name, parent=None, group=None, radius=1000):
        self.options = eval(open(f'data/Weapons/{name}.txt', 'r').read())

        super().__init__(general.weapons[self.options['img']], Transform(self.options['pos'], parent=parent), group)

        self.options['bullet'] = general.bullets[self.options['bullet']]

        self.spawn_pos = self.options['spawn']
        self.orig_img = self.image.copy()
        self.bullet = self.options['bullet'].copy()

        self.attack = False
        self.next_shot = 0

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
        s = Bullet(self.bullet, Transform(self.transform_.global_pos() + self.spawn_pos), general.player_group)
        s.speed = self.options['speed']

        direction = (pos[0] - self.transform_.x() + general.camera.transform_.x() - self.spawn_pos[0],
                     pos[1] - self.transform_.y() + general.camera.transform_.y() - self.spawn_pos[1])

        maxx = max(map(lambda x: abs(x), direction))
        s.rb.velocity.x = s.speed * direction[0] / maxx
        s.rb.velocity.y = s.speed * direction[1] / maxx

        self.next_shot = self.options['rate_of']

    def update(self):
        super().update()
        if self.next_shot > 0:
            self.next_shot -= 1 / general.FPS


class Bullet(Sprite):    # Класс сюрикена, только его пока нету)))
    def __init__(self, image, transform, group=None, speed=1500, damage=25):
        self.rb = RigidBody()
        self.rb.gravity = 0

        super().__init__(image, transform)
        self.speed = speed
        self.damage = damage
        self.time_destroy = 10.0  # Время до самоунчтожения

    def update(self):
        if self.rb:    # Усли перс физичный
            self.rb.update()    # вызывает update у RigidBody
            colliders = pygame.sprite.spritecollide(self, general.borders_group, False)    # Все объекты с которыми сталкивается перс

            if colliders:    # Проверка сталкивается вообще
                self.kill()
            elif self.time_destroy <= 0:
                self.kill()
            self.time_destroy -= 1 / general.FPS

            self.transform_.pos += (self.rb.velocity / general.FPS)  # меняем позицию перса

        super().update()